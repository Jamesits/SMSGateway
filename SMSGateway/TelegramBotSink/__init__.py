import logging
import typing

import pystache
# noinspection PyPackageRequirements
import telegram
# noinspection PyPackageRequirements
from telegram.ext import Updater, CommandHandler

from SMSGateway.envelope import Envelope
from SMSGateway.generic_vertex import GenericVertex
from SMSGateway.utils import dict_value_normalize, create_mustache_context_from_sms

logger = logging.getLogger(__name__)


class TelegramBotSink(GenericVertex):
    def __init__(self, alias: str, object_type: str, local_config: typing.Dict[str, any], global_config: any):
        super().__init__(alias, object_type, local_config, global_config)

        dict_value_normalize(self.local_config, 'message',
                             'From: {{sender}}\n'
                             'To: {{receiver}}\n'
                             'Received at: {{received_at}}\n'
                             'Content: {{content}}'
                             )

        self.bot = telegram.Bot(token=self.local_config['token'])
        self.updater = Updater(self.local_config['token'], use_context=True)
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler("start", self.command_start))
        self.dp.add_handler(CommandHandler("chatid", self.command_get_chat_id))
        self.dp.add_error_handler(self.error_callback)
        self.updater.start_polling()

    def error_callback(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def command_start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')

    def command_get_chat_id(self, update, context):
        """Echo the chat id."""
        update.message.reply_text(update.message.chat.id)

    def message_received_callback(self, envelope: Envelope):
        logger.info(f"Got message {envelope.sms.content}")
        mustache_context = create_mustache_context_from_sms(envelope.sms)
        self.bot.send_message(chat_id=self.local_config['chat_id'], text=pystache.render(
            self.local_config['message'],
            mustache_context,
        ))
