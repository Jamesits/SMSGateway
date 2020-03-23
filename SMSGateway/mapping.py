# defines all the mappings from string to class
# use all lower letters
from collections import defaultdict

from SMSGateway.DbltekSmsListener import DbltekSMSListener
from SMSGateway.SMPPListener import SMPPListener
from SMSGateway.SMTPListener import SMTPListener
from SMSGateway.SMTPSink import SMTPSink
from SMSGateway.TelegramBotSink import TelegramBotSink
from SMSGateway.generic_source import GenericSource

source_mapping = defaultdict(
    lambda: GenericSource,
    {
        # overrides
    }
)

listener_mapping = {
    "smtp": SMTPListener,
    "dbltek_api_server": DbltekSMSListener,
    "smpp": SMPPListener,
}

sink_mapping = {
    "smtp": SMTPSink,
    "telegram-bot": TelegramBotSink,
}

filter_mapping = {

}

mapping_mapping = {
    "source": source_mapping,
    "listener": listener_mapping,
    "sink": sink_mapping,
    "filter": filter_mapping,
}
