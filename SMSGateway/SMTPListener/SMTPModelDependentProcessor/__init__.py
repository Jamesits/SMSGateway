import logging

from SMSGateway import config
from .dbltek import SMTPMailProcessorDbltek

logger = logging.getLogger(__name__)


def mail_handler(session, envelope):
    source_ip = session.peer[0]
    source_device = config.get_device("smtp", source_ip)

    try:
        if source_device['vendor'] == 'dbltek':
            return SMTPMailProcessorDbltek.process(source_device, session, envelope)
        # add more 'elif' here
        else:
            raise NotImplementedError(f"Cannot find SMTP handler for vendor {source_device['vendor']}")
    except Exception as ex:
        if isinstance(ex, NotImplementedError):
            raise ex
        logger.exception(ex, stack_info=True)
