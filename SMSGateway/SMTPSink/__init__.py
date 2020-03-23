import logging
import smtplib
import ssl
import typing
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pystache

from SMSGateway.envelope import Envelope
from SMSGateway.generic_vertex import GenericVertex
from SMSGateway.sms import SMS
from SMSGateway.utils import dict_value_normalize, create_mustache_context_from_sms

logger = logging.getLogger(__name__)


class SMTPSink(GenericVertex):
    def __init__(self, alias: str, object_type: str, local_config: typing.Dict[str, any], global_config: any):
        super().__init__(alias, object_type, local_config, global_config)

        # fill default config
        dict_value_normalize(self.local_config, 'encryption', 'tls', to_lower=True, trim=True)
        if self.local_config['encryption'] == 'ssl': self.local_config['encryption'] = 'tls'
        if self.local_config['encryption'] == 'tls':
            default_port = 465
        elif self.local_config['encryption'] == 'starttls':
            default_port = 587
        elif self.local_config['encryption'] == 'plaintext':
            default_port = 25
        else:
            raise SyntaxError(f"SMTP unknown encryption method {self.local_config['encryption']}")
        dict_value_normalize(self.local_config, 'port', default_port)
        dict_value_normalize(self.local_config, 'from_address', local_config['username'])
        dict_value_normalize(self.local_config, 'subject', "New SMS from {{sender}}")
        dict_value_normalize(self.local_config, 'body_plaintext',
                             'From: {{sender}}\n'
                             'To: {{receiver}}\n'
                             'Received at: {{received_at}}\n'
                             'Content: {{content}}\n'
                             '\n\n'
                             'SMSGateway'
                             )

    def __get_ssl_context(self) -> ssl.SSLContext:
        return ssl.create_default_context()

    def __get_smtp_client_context_manager(self) -> smtplib.SMTP:
        if self.local_config['encryption'] == 'plaintext':
            server = smtplib.SMTP(
                host=self.local_config['server'],
                port=self.local_config['port'],
            )
        elif self.local_config['encryption'] == 'tls':
            server = smtplib.SMTP_SSL(
                host=self.local_config['server'],
                port=self.local_config['port'],
                context=self.__get_ssl_context()
            )
        elif self.local_config['encryption'] == 'starttls':
            server = smtplib.SMTP(
                host=self.local_config['server'],
                port=self.local_config['port'],
            )
            server.ehlo()
            server.starttls(context=self.__get_ssl_context())
        else:
            raise AttributeError(f"Unknown encryption method {self.local_config['encryption']}")

        server.ehlo()
        server.login(self.local_config['username'], self.local_config['password'])
        return server

    def __send_mail(self, sms: SMS):
        mustache_context = create_mustache_context_from_sms(sms)
        message = MIMEMultipart("alternative")
        message["Subject"] = pystache.render(self.local_config['subject'], mustache_context)
        message["From"] = self.local_config['from_address']
        message["To"] = self.local_config['to_address']
        if 'body_plaintext' in self.local_config:
            message.attach(MIMEText(
                pystache.render(self.local_config['body_plaintext'], mustache_context),
                "plain"
            ))
        if 'body_html' in self.local_config:
            message.attach(MIMEText(
                pystache.render(self.local_config['body_html'], mustache_context),
                "html"
            ))

        with self.__get_smtp_client_context_manager() as server:
            server.sendmail(
                from_addr=self.local_config['from_address'],
                to_addrs=[self.local_config['to_address']],
                msg=message.as_string(),
            )

    def message_received_callback(self, envelope: Envelope):
        logger.info(f"Got message {envelope.sms.content}")
        self.__send_mail(envelope.sms)
