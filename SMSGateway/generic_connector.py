from abc import ABC

from SMSGateway.generic_vertex import GenericVertex


class GenericConnector(GenericVertex, ABC):
    """
    A connector is a component in the server that either
    receives messages from message sources, or sends messages to message sinks
    """

    def start(self: "GenericConnector"):
        """Enable the listener"""
        pass

    def stop(self: "GenericConnector"):
        """Disable the listener"""
        pass
