import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
import logging
import base64
from . import SMTPModelDependentProcessor

logger = logging.getLogger(__name__)

# https://github.com/aio-libs/aiosmtpd/issues/102#issuecomment-302810943
class NewSMTP(SMTP):
    @asyncio.coroutine
    def smtp_AUTH(self, arg):
        '''Authenticates user with any credential'''
        argv = str(arg).split(" ", 2)
        if argv[0] == 'PLAIN': # password-only auth
            if len(argv) == 1: # we have to ask for password
                yield from self.push('334')
                try:
                    second_line = yield from self._reader.readline()
                except (ConnectionResetError, asyncio.CancelledError) as error:
                    logger.error(error)
                try:
                    second_line = second_line.rstrip(b'\r\n').decode('ascii')
                    password = base64.b64decode(second_line).decode('ascii')
                    logger.debug(f"AUTH PLAIN with password \"{password}\"")
                    self.session.authenticated = True
                    self.session.auth_method = "PLAIN"
                    self.session.auth_password = password
                except UnicodeDecodeError:
                    yield from self.push('500 Error: Challenge must be ASCII')
                    return
                yield from self.push('235 Authentication successful')
            else: # The user provided a password in the same line
                password = base64.b64decode(argv[1]).decode('ascii')
                logger.debug(f"AUTH PLAIN with password \"{password}\"")
                self.session.authenticated = True
                self.session.auth_method = "PLAIN"
                self.session.auth_password = password
                yield from self.push('235 Authentication successful')
        elif argv[0] == 'LOGIN': # username + password auth
            yield from self.push('334 VXNlcm5hbWU6') # ask for username
            try:
                second_line = yield from self._reader.readline()
                username = base64.b64decode(second_line).decode('ascii')
                logger.debug(f"AUTH LOGIN with username \"{username}\"")
                self.session.auth_method = "LOGIN"
                self.session.auth_username = username
            except (ConnectionResetError, asyncio.CancelledError) as error:
                logger.error(error)
            yield from self.push('334 UGFzc3dvcmQ6') # ask for password
            try:
                second_line = yield from self._reader.readline()
                password = base64.b64decode(second_line).decode('ascii')
                logger.debug(f"AUTH LOGIN with password \"{password}\"")
                self.session.authenticated = True
                self.session.auth_password = password
            except (ConnectionResetError, asyncio.CancelledError) as error:
                logger.error(error)
            yield from self.push('235 Authentication successful')
        # elif argv[0] == 'CRAM-MD5': # challenge-response auth
        #     yield from self.push(f'334 {base64.b64encode("114514")}') # send a challenge
        #     try:
        #         second_line = yield from self._reader.readline()
        #         ret = base64.b64decode(second_line)
        #         logger.debug(f"AUTH CRAM-MD5 with result \"{ret}\"")
        #         self.authenticated = True
        #         self.auth_method = "CRAM-MD5"
        #     except (ConnectionResetError, asyncio.CancelledError) as error:
        #         logger.error(error)
        #     yield from self.push('235 Authentication successful')
        else:
            yield from self.push('501 Syntax: AUTH LOGIN')
            return

class SMTPMessageGatewayController(Controller):
    def factory(self):
        return NewSMTP(self.handler, enable_SMTPUTF8=self.enable_SMTPUTF8)

class SMTPMessageGatewayHandler:

    async def handle_DATA(self, server, session, envelope):
        # print('Message from %s' % envelope.mail_from)
        # print('Message for %s' % envelope.rcpt_tos)
        # print('Message data:\n')
        # print(envelope.content.decode('utf8', errors='replace'))
        # print('End of message')
        # session = {'peer': ('100.97.1.7', 49396), 'ssl': None, 'host_name': '100.97.2.2', 'extended_smtp': True, 'loop': <_WindowsSelectorEventLoop running=True closed=False debug=False>}
        ret = SMTPModelDependentProcessor.mail_handler(session, envelope)

        import pprint
        rets = pprint.pformat(ret, indent=4)
        logger.info(f"Decoded message: \n{rets}")
        
        return '250 Message accepted for delivery'

class SMTPMessageGateway:
    def __init__(self, listen_ip, listen_port):
        self.controller = SMTPMessageGatewayController(SMTPMessageGatewayHandler(), hostname=listen_ip, port=listen_port, enable_SMTPUTF8=True)

    def start(self):
        self.controller.start()

    def stop(self):
        self.controller.stop()