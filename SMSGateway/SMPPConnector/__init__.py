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
smpp_reconnect_interval_seconds = 0.25

# defines the mapping from SMPP encodings to python decoders
# if the value is a function, func(raw_bytes) will be called to decode the bytes
# if the value is a string, then we'll call raw_bytes.decode(value)
# if the value is None, an exception will be raised
decoder_map: typing.Dict[int, typing.Union[typing.Callable[[bytes], str], str, None]] = {
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


def do_not_optimize_away_my_imports():
    gsm0338.get_codec_info()


# for pdu.destination_addr and pdu.source_addr
# FIXME: use the correct decoder
def decode_pdu_addr(raw: bytes) -> str:
    try:
        return raw.decode('ascii')
    except Exception as ex:
        logger.exception(ex)
        return str(raw)


def decode_pdu_message_content(pdu: smpplib.command) -> str:
    decoder = decoder_map[smpplib.consts.SMPP_ENCODING_DEFAULT]
    if (pdu.data_coding in decoder_map) and decoder_map[pdu.data_coding] is not None:
        decoder = decoder_map[pdu.data_coding]
    else:
        logger.error(f"Unknown encoding {pdu.data_coding}")

    try:
        if callable(decoder):
            encoded_message = decoder(pdu.short_message)
        else:
            encoded_message = pdu.short_message.decode(decoder)
    except Exception as ex:
        logger.exception(ex)
        encoded_message = binascii.hexlify(pdu.short_message).decode("ascii")

    return encoded_message


class SMPPConnector(GenericConnector):
    """
    Connects to a SMPP server.
    """

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
        logger.info(f"delivered {pdu.receipted_message_id}")
        if pdu.command == "deliver_sm":
            # got new message
            sender = decode_pdu_addr(pdu.source_addr)
            receiver = decode_pdu_addr(pdu.destination_addr)  # usually '0'
            message = decode_pdu_message_content(pdu)
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
                if device.c[class_identifier]['client'] == pdu.client:
                    to_vertex = device
                    break

            envelope: Envelope = Envelope(
                from_vertex=self,
                to_vertex=to_vertex,
                sms=new_sms
            )

            self.send_message(envelope)
