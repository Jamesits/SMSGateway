import logging

from ..IListener import IListener

logger = logging.getLogger(__name__)


class SMPPServer(IListener):
    def __init__(self, listener_config, global_config):
        # we can't actually "listen" something because we are the client not the server
        pass
