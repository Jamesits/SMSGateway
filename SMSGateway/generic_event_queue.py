import logging
import queue
from abc import ABC
from time import sleep

from SMSGateway.envelope import Envelope

logger = logging.getLogger(__name__)


class GenericEventQueue(ABC):
    def __init__(self):
        raise NotImplementedError

    def enqueue(self, envelope: Envelope):
        raise NotImplementedError

    def event_loop_sync(self):
        raise NotImplementedError


class PythonQueueBasedEventQueue(GenericEventQueue):
    def __init__(self):
        self.queue = queue.Queue()
        self.queue_poll_interval_seconds = 0.25

    def enqueue(self, envelope: Envelope):
        logger.info(f"Got message from {envelope.from_vertex.alias}")
        self.queue.put_nowait(envelope)

    def event_loop_sync(self):
        while True:
            try:
                envelope = self.queue.get_nowait()
                if envelope.to_vertex is not None:
                    envelope.to_vertex.message_received_callback(envelope)
                else:
                    logger.warning(f"Queue received message with empty destination")
            except queue.Empty:
                sleep(self.queue_poll_interval_seconds)
