import dataclasses
import logging
import typing
from abc import ABC
from collections import defaultdict

from SMSGateway.envelope import Envelope

logger = logging.getLogger(__name__)


@dataclasses.dataclass(init=False)
class GenericVertex(ABC):
    """Generic node in the routing graph data structure"""
    alias: str
    type: str
    local_config: typing.Dict[str, any]
    global_config: any
    in_edge_adjacent_vertices: typing.List["GenericVertex"]
    out_edge_adjacent_vertices: typing.List["GenericVertex"]
    c: typing.Dict[str, typing.Dict]  # for any custom data that other modules need

    def __init__(self, alias: str, object_type: str, local_config: typing.Dict[str, any], global_config: any):
        self.alias = alias
        self.type = object_type
        self.local_config = local_config
        self.global_config = global_config
        self.in_edge_adjacent_vertices = []
        self.out_edge_adjacent_vertices = []
        self.c = defaultdict(dict)

    def add_in_edge(self, adjacent_vertex: "GenericVertex"):
        self.in_edge_adjacent_vertices.append(adjacent_vertex)

    def add_out_edge(self, adjacent_vertex: "GenericVertex"):
        self.out_edge_adjacent_vertices.append(adjacent_vertex)

    def message_received_callback(self, envelope: Envelope):
        # by default, duplicate the message to every out edges
        for vertex in self.out_edge_adjacent_vertices:
            new_envelope = Envelope(
                from_vertex=self,
                to_vertex=vertex,
                sms=envelope.sms,
            )
            self.send_message(new_envelope)

    def send_message(self, envelope: Envelope):
        if envelope.from_vertex != self:
            logger.error("GenericVertex.send_message() envelope.from_vertex is not ourselves")
            return
        self.global_config.queue.enqueue(envelope)
