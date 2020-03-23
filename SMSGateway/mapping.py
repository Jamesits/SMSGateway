# defines all the mappings from string to class
# use all lower letters
import typing
from collections import defaultdict

from SMSGateway.DbltekApiServerConnector import DbltekApiServerConnector
from SMSGateway.SMPPConnector import SMPPConnector
from SMSGateway.SMTPClientConnector import SMTPClientConnector
from SMSGateway.SMTPListener import SMTPConnector
from SMSGateway.TelegramBotConnector import TelegramBotConnector
from SMSGateway.generic_device import GenericDevice
from SMSGateway.generic_vertex import GenericVertex

MappingType = typing.Dict[str, typing.Type[GenericVertex]]

device_mapping: MappingType = defaultdict(
    lambda: GenericDevice,
    {
        # overrides
    }
)

connector_mapping: MappingType = {
    "smtp-server": SMTPConnector,
    "dbltek-api-server": DbltekApiServerConnector,
    "smpp-client": SMPPConnector,
    "smtp-client": SMTPClientConnector,
    "telegram-bot": TelegramBotConnector,
}

filter_mapping: MappingType = {

}

mapping_mapping: typing.Dict[str, MappingType] = {
    "device": device_mapping,
    "connector": connector_mapping,
    "filter": filter_mapping,
}
