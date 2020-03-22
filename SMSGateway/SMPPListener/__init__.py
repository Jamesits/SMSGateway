import binascii
import datetime
import logging
from threading import Thread
from time import sleep

import smpplib
import smpplib.client
import smpplib.consts
import smpplib.gsm

from SMSGateway.SMPPListener.gsm_7bit_encoder import gsm_decode
from SMSGateway.envelope import Envelope
from SMSGateway.generic_listener import GenericListener
from SMSGateway.generic_vertex import GenericVertex
from SMSGateway.sms import SMS

class_identifier = "SMPPListener"
logger = logging.getLogger(__name__)
decoder_map = {
    smpplib.consts.SMPP_ENCODING_DEFAULT: gsm_decode,
    smpplib.consts.SMPP_ENCODING_IA5: "ascii",
    smpplib.consts.SMPP_ENCODING_BINARY: "utf_16_be",
    smpplib.consts.SMPP_ENCODING_ISO88591: "latin_1",
    smpplib.consts.SMPP_ENCODING_BINARY2: "utf_16_be",
    smpplib.consts.SMPP_ENCODING_JIS: "shift_jis",
    smpplib.consts.SMPP_ENCODING_ISO88595: "iso8859_5",
    smpplib.consts.SMPP_ENCODING_ISO88598: "iso8859_8",
    smpplib.consts.SMPP_ENCODING_ISO10646: "utf_16_be",
    smpplib.consts.SMPP_ENCODING_PICTOGRAM: None,
    smpplib.consts.SMPP_ENCODING_ISO2022JP: "iso2022_jp",
    smpplib.consts.SMPP_ENCODING_EXTJIS: "shift_jisx0213",
    smpplib.consts.SMPP_ENCODING_KSC5601: "euc_kr",
}


# for pdu.destination_addr and pdu.source_addr
# FIXME: use the correct decoder
def decode_pdu_addr(raw: bytes) -> str:
    try:
        return raw.decode('ascii')
    except Exception as ex:
        logger.exception(ex)
        return str(raw)


class SMPPListener(GenericListener):
    def start(self):
        pass

    def stop(self):
        pass

    def add_out_edge(self, adjacent_vertex: "GenericVertex"):
        super().add_out_edge(adjacent_vertex)

        adjacent_vertex.c[class_identifier]['client'] = smpplib.client.Client(adjacent_vertex.local_config["ip"],
                                                                              adjacent_vertex.local_config["port"])
        adjacent_vertex.c[class_identifier]['client'].set_message_sent_handler(self.smpp_message_send_handler)
        adjacent_vertex.c[class_identifier]['client'].set_message_received_handler(self.smpp_message_receive_handler)

        def smpp_thread_func():
            while True:
                logger.info(f"SMPP connect to {adjacent_vertex.alias}")
                try:
                    adjacent_vertex.c[class_identifier]['client'].connect()
                    adjacent_vertex.c[class_identifier]['client'].bind_transceiver(
                        system_id=adjacent_vertex.local_config["username"],
                        password=adjacent_vertex.local_config["password"])
                    adjacent_vertex.c[class_identifier]['client'].listen()
                except smpplib.exceptions.PDUError as ex:
                    if ex.args[1] == 5:
                        logger.exception("Connection per account limit reached")
                        sleep(1)
                    else:
                        logger.exception("Unknown error during SMPP connection")
                except smpplib.exceptions.ConnectionError as ex:
                    logger.exception("Connection failed")
                    sleep(0.2)

        adjacent_vertex.smpp_thread_func = smpp_thread_func
        adjacent_vertex.smpp_client_listen_thread = Thread(target=adjacent_vertex.smpp_thread_func)
        adjacent_vertex.smpp_client_listen_thread.start()

    def smpp_message_send_handler(self, pdu: smpplib.command):
        logger.info(f"sent {pdu.sequence} {pdu.message_id}")

    def smpp_message_receive_handler(self, pdu: smpplib.command):  # pdu is a smpplib.pdu.PDU
        logger.info(f"delivered {pdu.receipted_message_id}")
        if pdu.command == "deliver_sm":
            # got new message
            sender = decode_pdu_addr(pdu.source_addr)
            receiver = decode_pdu_addr(pdu.destination_addr)  # usually '0'

            # try to detect data encoding
            decoder = decoder_map[smpplib.consts.SMPP_ENCODING_DEFAULT]
            if (pdu.data_coding in decoder_map) and decoder_map[pdu.data_coding] is not None:
                decoder = decoder_map[pdu.data_coding]
            else:
                logger.warning(f"Unknown encoding {pdu.data_coding}")

            try:
                if callable(decoder):
                    encoded_message = decoder(pdu.short_message)
                else:
                    encoded_message = pdu.short_message.decode(decoder)
            except Exception as ex:
                logger.exception(ex)
                encoded_message = binascii.hexlify(pdu.short_message).decode("ascii")

            logger.info(f"New SMS from {sender}: {encoded_message}")

            # construct sms data structure
            new_sms = SMS(
                sender=sender,
                receiver=receiver,
                content=encoded_message,
                received_at=datetime.datetime.now(),
            )

            # get the sending device object
            to_vertex = None
            for device in self.out_edge_adjacent_vertices:
                if device.c[class_identifier]['client'] == pdu.client:
                    to_vertex = device
                    break

            envelope = Envelope(
                from_vertex=self,
                to_vertex=to_vertex,
                sms=new_sms
            )

            self.send_message(envelope)
