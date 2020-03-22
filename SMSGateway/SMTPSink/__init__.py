import logging

from SMSGateway.envelope import Envelope
from SMSGateway.generic_vertex import GenericVertex

logger = logging.getLogger(__name__)


class SMTPSink(GenericVertex):
    def message_received_callback(self, envelope: Envelope):
        logger.info(f"Got message {envelope.sms.content}")
