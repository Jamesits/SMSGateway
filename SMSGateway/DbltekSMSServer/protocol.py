import logging
logger = logging.getLogger(__name__)

class DbltekSMSServerUDPProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        logger.debug(f'Received from {addr}: {message}')
        #self.transport.sendto(data, addr)