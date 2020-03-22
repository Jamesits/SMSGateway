from abc import ABC

from SMSGateway.generic_vertex import GenericVertex


class GenericListener(GenericVertex, ABC):
    """A listener is a component in the server that receives messages from message sources"""

    def start(self: "GenericListener"):
        """Enable the listener"""
        raise NotImplementedError

    def stop(self: "GenericListener"):
        """Disable the listener"""
        raise NotImplementedError
