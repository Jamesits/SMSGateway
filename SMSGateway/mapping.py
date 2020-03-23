# defines all the mappings from string to class
# use all lower letters
from collections import defaultdict
import typing

from SMSGateway.DbltekSmsListener import DbltekSMSListener
from SMSGateway.SMPPListener import SMPPListener
from SMSGateway.SMTPListener import SMTPListener
from SMSGateway.SMTPSink import SMTPSink
from SMSGateway.TelegramBotSink import TelegramBotSink
from SMSGateway.generic_source import GenericSource
from SMSGateway.generic_vertex import GenericVertex

MappingType = typing.Dict[str, typing.Type[GenericVertex]]

source_mapping: MappingType = defaultdict(
    lambda: GenericSource,
    {
        # overrides
    }
)

listener_mapping: MappingType = {
    "smtp": SMTPListener,
    "dbltek_api_server": DbltekSMSListener,
    "smpp": SMPPListener,
}

sink_mapping: MappingType = {
    "smtp": SMTPSink,
    "telegram-bot": TelegramBotSink,
}

filter_mapping: MappingType = {

}

mapping_mapping: typing.Dict[str, MappingType] = {
    "source": source_mapping,
    "listener": listener_mapping,
    "sink": sink_mapping,
    "filter": filter_mapping,
}
