import binascii
import logging
import typing
from dataclasses import dataclass
from threading import Thread

import smpplib
import smpplib.client
import smpplib.consts
import smpplib.gsm

from .gsm_7bit_encoder import gsm_decode
from ..IListener import IListener

logger = logging.getLogger(__name__)
smpp_devices: typing.List["SMPPDevice"] = []
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
    smpplib.consts.SMPP_ENCODING_PICTOGRAM: "",
    smpplib.consts.SMPP_ENCODING_ISO2022JP: "iso2022_jp",
    smpplib.consts.SMPP_ENCODING_EXTJIS: "shift_jisx0213",
    smpplib.consts.SMPP_ENCODING_KSC5601: "euc_kr",
}


@dataclass(init=False)
class SMPPDevice:
    device_config: any
    smpp_client: smpplib.client.Client
    smpp_client_listen_thread: Thread


def smpp_message_send_handler(pdu: smpplib.command):
    logger.info(f"sent {pdu.sequence} {pdu.message_id}")


def smpp_message_receive_handler(pdu: smpplib.command):
    logger.info(f"delivered {pdu.receipted_message_id}")
    if pdu.command == "deliver_sm":
        # got new message

        sender = ""
        try:
            sender = pdu.source_addr.decode('ascii')
        except Exception as ex:
            logger.exception(ex)
            sender = str(pdu.source_addr)

        # try to detect data encoding
        decoder = decoder_map[smpplib.consts.SMPP_ENCODING_DEFAULT]
        if pdu.data_coding in decoder_map:
            decoder = decoder_map[pdu.data_coding]
        else:
            logger.warning(f"Unknown encoding {pdu.data_coding}")

        encoded_message = ""
        try:
            if callable(decoder):
                encoded_message = decoder(pdu.short_message)
            else:
                encoded_message = pdu.short_message.decode(decoder)
        except Exception as ex:
            logger.exception(ex)
            encoded_message = binascii.hexlify(pdu.short_message).decode("ascii")

        logger.info(
            f"New SMS from {sender}: {encoded_message}")


class SMPPListener(IListener):
    def __init__(self, listener_config, global_config):
        # we can't actually "listen" something because we are the client not the server
        if "device" in global_config.user_config:
            for device in global_config.user_config["device"]:
                if device["connector"] == "SMPP":
                    # that's the device we need to connect to
                    new_device = SMPPDevice()
                    new_device.device_config = device
                    smpp_devices.append(new_device)

    def start(self):
        # connect to the devices
        for device in smpp_devices:
            device.client = smpplib.client.Client(device.device_config["ip"], device.device_config["port"])
            device.client.set_message_sent_handler(smpp_message_send_handler)
            device.client.set_message_received_handler(smpp_message_receive_handler)
            device.client.connect()
            try:
                device.client.bind_transceiver(system_id=device.device_config["username"],
                                               password=device.device_config["password"])
            except smpplib.exceptions.PDUError as ex:
                logger.exception(ex)
                if ex.args[1] == 5:
                    logger.error("Connection per account limit reached")
                    # TODO: try again after a while
            device.smpp_client_listen_thread = Thread(target=device.client.listen)
            device.smpp_client_listen_thread.start()

    def stop(self):
        for device in smpp_devices:
            pass
