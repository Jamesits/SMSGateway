from .base import SMTPMailProcessorBase
from ..sms import SMS
import logging
import base64
from datetime import datetime
import pytz
logger = logging.getLogger(__name__)

class SMTPMailProcessorDbltek(SMTPMailProcessorBase):
    @staticmethod
    def process(device, session, envelope): 
        eml = envelope.content.decode('utf8', errors='replace')
        mail_body = eml.split("\r\n")[-1]
        mail_body_decoded = base64.b64decode(mail_body).decode('utf-8').strip("\n")
        logger.debug(f"Received raw body: \"{mail_body_decoded}\"")
        # message detail after base64 decode:
        #SN:GOIP8AAAAA12345678 Channel:1 Sender:10-16 23:31:25,+8613000000000,content

        metadata, sender, sms_content = mail_body_decoded.split(',', 2)
        sn, channel, time = metadata.split(' ', 2)
        sn = sn.split(':', 1)[1]
        channel = channel.split(':', 1)[1]
        time = time.split(':', 1)[1]

        dt = datetime.strptime(time, "%m-%d %H:%M:%S").replace(
                year=datetime.now().year,
                tzinfo=pytz.FixedOffset(device["timezone"] * 60)
            )

        sms = SMS({
            "transport_sender_uri": f"smtp://{session.peer[0]}:{session.peer[1]}/{sn}/{channel}",
            "transport_receiver_uri": f"smtp://{session.host_name}",
            "sms_sender": sender,
            "sms_receiver": sn,
            "sms_content": sms_content,
            "sms_received_time": dt,
        })
        
        return sms
        