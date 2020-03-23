import binascii
import datetime
import logging
import typing
from threading import Thread
from time import sleep

import gsm0338
import smpplib
import smpplib.client
import smpplib.consts
import smpplib.gsm

from SMSGateway.envelope import Envelope
from SMSGateway.generic_connector import GenericConnector
from SMSGateway.generic_vertex import GenericVertex
from SMSGateway.sms import SMS

class_identifier = "SMPPConnector"
logger = logging.getLogger(__name__)
smpp_reconnect_interval_seconds: float = 0.25
default_decoder: str = "utf_16_be"
DecoderType = typing.Union[typing.Callable[[bytes], str], str, None]

# defines the mapping from SMPP encodings to python decoders
# if the value is a function, func(raw_bytes) will be called to decode the bytes
# if the value is a string, then we'll call raw_bytes.decode(value)
# if the value is None, an exception will be raised
decoder_map: typing.Dict[typing.Optional[int], DecoderType] = {
    None: None,
    smpplib.consts.SMPP_ENCODING_DEFAULT: "gsm03.38",
    smpplib.consts.SMPP_ENCODING_IA5: "ascii",
    smpplib.consts.SMPP_ENCODING_BINARY: "utf_16_be",
    smpplib.consts.SMPP_ENCODING_ISO88591: "latin_1",
    smpplib.consts.SMPP_ENCODING_BINARY2: "utf_16_be",
    smpplib.consts.SMPP_ENCODING_JIS: "shift_jis",
    smpplib.consts.SMPP_ENCODING_ISO88595: "iso8859_5",
    smpplib.consts.SMPP_ENCODING_ISO88598: "iso8859_8",
    smpplib.consts.SMPP_ENCODING_ISO10646: "utf_16_be",
    smpplib.consts.SMPP_ENCODING_PICTOGRAM: None,  # different for each ISP, so we just ignore it
    smpplib.consts.SMPP_ENCODING_ISO2022JP: "iso2022_jp",
    smpplib.consts.SMPP_ENCODING_EXTJIS: "shift_jisx0213",
    smpplib.consts.SMPP_ENCODING_KSC5601: "euc_kr",
}


def __pycharm_do_not_optimize_away_my_imports():
    gsm0338.get_codec_info()


# FIXME: use the correct decoder
def decode_pdu_addr(raw: bytes) -> str:
    """
    Decode the destination_addr and source_addr field of a pdu.PDU.
    :param raw: raw bytes
    :return: decoded string
    """
    try:
        return raw.decode('ascii')
    except Exception as ex:
        logger.exception(ex)
        return str(raw)


def decode_pdu_message_content(encoding: typing.Optional[int], raw: bytes) -> str:
    """
    Decode the message content of a pdu.PDU.
    :param encoding: the data_coding field in the pdu
    :param raw: the message content in its raw form, i.e. the short_message field in the pdu
    :return:
    """
    decoder: DecoderType
    if encoding in decoder_map:
        decoder = decoder_map[encoding]
    else:
        logger.error(f"Unknown encoding {encoding}")
        decoder = "utf_16_be"

    if decoder is None:
        logger.error(f"Unsupported encoding {encoding}, fallback to {default_decoder}")
        decoder = default_decoder

    encoded_message: typing.Optional[str]
    try:
        if callable(decoder):
            encoded_message = decoder(raw)
        else:
            encoded_message = raw.decode(decoder)
    except Exception as ex:
        logger.exception(ex)
        # if everything fails, we just spit some octets in hex form
        encoded_message = binascii.hexlify(raw).decode("ascii")

    return encoded_message


class SMPPConnector(GenericConnector):
    """
    Connects to a SMPP server.
    """
    csms_store: typing.Dict[int, typing.List]

    def __init__(self, alias: str, object_type: str, local_config: typing.Dict[str, typing.Any],
                 global_config: typing.Any):
        super().__init__(alias, object_type, local_config, global_config)
        self.csms_store = {}

    def start(self):
        pass

    def stop(self):
        pass

    def add_out_edge(self, adjacent_vertex: "GenericVertex"):
        super().add_out_edge(adjacent_vertex)

        def smpp_thread_func():
            while True:
                logger.info(f"SMPP connect to {adjacent_vertex.alias}")
                try:
                    # we must recreate the client every time, otherwise we'll get
                    # ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
                    adjacent_vertex.c[class_identifier]['client'] = smpplib.client.Client(
                        adjacent_vertex.local_config["ip"],
                        adjacent_vertex.local_config["port"]
                    )
                    adjacent_vertex.c[class_identifier]['client'].set_message_sent_handler(
                        self.smpp_message_send_handler
                    )
                    adjacent_vertex.c[class_identifier]['client'].set_message_received_handler(
                        self.smpp_message_receive_handler
                    )
                    adjacent_vertex.c[class_identifier]['client'].connect()
                    adjacent_vertex.c[class_identifier]['client'].bind_transceiver(
                        system_id=adjacent_vertex.local_config["username"],
                        password=adjacent_vertex.local_config["password"],
                    )
                    adjacent_vertex.c[class_identifier]['client'].listen()
                except smpplib.exceptions.PDUError as ex:
                    if ex.args[1] == 5:
                        logger.exception("Connection per account limit reached")
                    else:
                        logger.exception("Unknown error during SMPP connection")
                except smpplib.exceptions.ConnectionError:
                    logger.exception("Connection failed")
                # wait and reconnect
                sleep(smpp_reconnect_interval_seconds)

        adjacent_vertex.c[class_identifier]['smpp_thread_func'] = smpp_thread_func
        adjacent_vertex.c[class_identifier]['smpp_client_listen_thread'] = Thread(target=smpp_thread_func)
        adjacent_vertex.c[class_identifier]['smpp_client_listen_thread'].start()

    def smpp_message_send_handler(self, pdu: smpplib.command):
        logger.info(f"sent {pdu.sequence} {pdu.message_id}")

    def smpp_message_receive_handler(self, pdu: smpplib.command):  # pdu is a smpplib.pdu.PDU
        if pdu.command == "deliver_sm":
            assert isinstance(pdu, smpplib.command.DeliverSM)
            # got new message
            # note: pdu.sequence is just a serial number of current session

            # detect if it is a CSMS (partial message)
            # https://en.wikipedia.org/wiki/Concatenated_SMS
            udh_header_length: int = 0
            csms_reference_number: int = 0
            total_parts: int = 0
            sequence: int = 0
            if len(pdu.short_message) > 6:
                if int(pdu.short_message[0]) - 2 == int(pdu.short_message[2]):
                    udh_header_length = pdu.short_message[0]
                    if pdu.short_message[0] == 0x05 and pdu.short_message[1] == 0x00:
                        # 8-bit CSMS
                        csms_reference_number = int(pdu.short_message[3])
                        total_parts = int(pdu.short_message[4])
                        sequence = int(pdu.short_message[5])
                    elif pdu.short_message[0] == 0x06 and pdu.short_message[1] == 0x08:
                        # 16-bit CSMS
                        csms_reference_number = int(pdu.short_message[3]) << 8 + int(pdu.short_message[4])
                        total_parts = int(pdu.short_message[5])
                        sequence = int(pdu.short_message[6])

            sender = decode_pdu_addr(pdu.source_addr)
            receiver = decode_pdu_addr(pdu.destination_addr)  # usually '0'
            short_message_content = pdu.short_message[udh_header_length + 1:]
            message = decode_pdu_message_content(pdu.data_coding, short_message_content)

            # try to concentrate the SMS
            if total_parts > 0:
                # verify message store status
                if csms_reference_number not in self.csms_store:
                    # we received the first entry of this message, initialize our entry
                    self.csms_store[csms_reference_number] = [None] * total_parts
                elif len(self.csms_store[csms_reference_number]) != total_parts:
                    logger.warning(
                        f"CSMS {csms_reference_number} original_parts={len(self.csms_store[csms_reference_number])}, new_parts={total_parts}, overriding")
                    self.csms_store[csms_reference_number] = [None] * total_parts

                # put our received part in; note that sequence starts with 1
                self.csms_store[csms_reference_number][sequence - 1] = message
                if None in self.csms_store[csms_reference_number]:
                    # more parts to receive, hold on for now
                    logger.info(f"New CSMS ({sequence}/{total_parts}) from {sender} to {receiver}: {message}")
                    return
                else:
                    # all parts have been received
                    message = ''.join(self.csms_store.pop(csms_reference_number))

            logger.info(f"New SMS from {sender} to {receiver}: {message}")
            # construct sms data structure
            new_sms = SMS(
                sender=sender,
                receiver=receiver,
                content=message,
                received_at=datetime.datetime.now(),
            )

            # get the sending device object
            to_vertex: typing.Optional[GenericVertex] = None
            for device in self.out_edge_adjacent_vertices:
                # DeliverSM doesn't come with a '.client' in its type definition, so we work around it
                if device.c[class_identifier]['client'] == pdu.__dict__.get('client', None):
                    to_vertex = device
                    break

            envelope: Envelope = Envelope(
                from_vertex=self,
                to_vertex=to_vertex,
                sms=new_sms
            )

            self.send_message(envelope)
        else:
            logger.info(f"Unknown command {pdu.command}")
