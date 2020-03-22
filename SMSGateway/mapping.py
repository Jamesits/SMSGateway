# defines all the mappings from string to class
# use all lower letters

from SMSGateway.DbltekSmsListener import DbltekSMSListener
from SMSGateway.SMPPListener import SMPPListener
from SMSGateway.SMTPListener import SMTPListener
from SMSGateway.SMTPSink import SMTPSink
from SMSGateway.TelegramBotSink import TelegramBotSink

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
    "listener": listener_mapping,
    "sink": sink_mapping,
    "filter": filter_mapping,
}
