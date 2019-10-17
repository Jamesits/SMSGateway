import logging
import pprint
logger = logging.getLogger(__name__)

# https://github.com/iivorait/FSG-GOIP-snippet/blob/master/doc/goip_sms_Interface_en.pdf
class DbltekSMSServerUDPProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        logger.debug(f'Received from {addr}: {message}')
        #self.transport.sendto(data, addr)
        ret = None
        if message.startswith("req"):
            ret = self.on_keepalive(message, addr)
        else:
            raise NotImplementedError(f"Unknown packet: {message}")

        if ret is not None:
            self.transport.sendto(ret.encode("utf-8"), addr)
            logger.debug(f"Keepalive packet reply to {addr}: {ret}")

    def on_keepalive(self, message, addr):
        req = {key:value for (key, value) in [x.split(":", 1) if not x.endswith(":") else (x.rstrip(":"), "") for x in message.strip(";").split(";")]}
        logger.debug(f"Keepalive packet from {addr}: {pprint.pformat(req, indent=4)}")
        ret = f"reg:{req['req']},status:200"
        return ret
