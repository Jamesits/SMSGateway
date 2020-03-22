# defines all the mappings from string to class
# use all lower letters

from SMSGateway.DbltekSmsListener import DbltekSMSListener
from SMSGateway.SMPPListener import SMPPListener
from SMSGateway.SMTPListener import SMTPListener
from SMSGateway.SMTPSink import SMTPSink

listener_mapping = {
    "smtp": SMTPListener,
    "dbltek_api_server": DbltekSMSListener,
    "smpp": SMPPListener,
}

sink_mapping = {
    "smtp": SMTPSink,
}

filter_mapping = {

}

source_mapping = {
    "smtp"
}

mapping_mapping = {
    "listener": listener_mapping,
    "sink": sink_mapping,
    "filter": filter_mapping,
    "source": source_mapping,
}
