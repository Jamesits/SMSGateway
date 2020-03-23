import logging
import queue
from abc import ABC
from time import sleep

from SMSGateway.envelope import Envelope

logger = logging.getLogger(__name__)


class GenericEventQueue(ABC):
    """The global event queue interface"""
    def __init__(self):
        pass

    def enqueue(self, envelope: Envelope):
        raise NotImplementedError

    def event_loop_sync(self):
        raise NotImplementedError


class PythonQueueBasedEventQueue(GenericEventQueue):
    """A very basic event queue implementation"""
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.queue_poll_interval_seconds = 0.25

    def enqueue(self, envelope: Envelope):
        logger.info(f"Got message from {envelope.from_vertex.alias}")
        self.queue.put_nowait(envelope)

    def event_loop_sync(self):
        while True:
            try:
                envelope: Envelope = self.queue.get_nowait()
                if envelope.to_vertex is not None:
                    try:
                        envelope.to_vertex.message_received_callback(envelope)
                    except Exception as ex:
                        logger.exception(
                            f"Event processing failed at {envelope.to_vertex.type}/{envelope.to_vertex.alias}")
                else:
                    logger.warning(f"Queue received message with empty destination")
            except queue.Empty:
                sleep(self.queue_poll_interval_seconds)
