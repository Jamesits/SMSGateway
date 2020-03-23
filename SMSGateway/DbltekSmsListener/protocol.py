import logging
import pprint
import asyncio

logger = logging.getLogger(__name__)


# https://github.com/iivorait/FSG-GOIP-snippet/blob/master/doc/goip_sms_Interface_en.pdf
# TODO: implement anti-reply
# (cache the latest few messages and discard them / resend reply in case UDP packet is lost on the route)
class DbltekSMSServerUDPProtocol(asyncio.BaseProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        logger.debug(f'Received from {addr}: {message}')
        # self.transport.sendto(data, addr)
        ret = None
        if message.startswith("req"):
            ret = self.on_keepalive(message, addr)
        elif message.startswith("RECEIVE"):
            ret = self.on_sms_receive(message, addr)
        else:
            raise NotImplementedError(f"Unknown packet: {message}")

        if ret is not None:
            self.transport.sendto(ret.encode("utf-8"), addr)
            logger.debug(f"Keepalive packet reply to {addr}: {ret}")

    def on_keepalive(self, message, addr):
        req = {key: value for (key, value) in [x.split(":", 1) if not x.endswith(":") else (x.rstrip(":"), "") for x in
                                               message.rstrip(";").split(";")]}
        logger.debug(f"Keepalive packet from {addr}: {pprint.pformat(req, indent=4)}")
        ret = f"reg:{req['req']},status:200"
        return ret

    def on_sms_receive(self, message, addr):
        req = {key: value for (key, value) in [x.split(":", 1) if not x.endswith(":") else (x.rstrip(":"), "") for x in
                                               message.rstrip(";").split(";")]}
        logger.debug(f"Keepalive packet from {addr}: {pprint.pformat(req, indent=4)}")

        # TODO: validate device, execute route
        # source_device = config.get_device("dbltek_sms_server", source_ip)

        ret = f"RECEIVE {req['RECEIVE']} OK\n"
        return ret
