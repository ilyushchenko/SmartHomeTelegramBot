from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import json
from EditModuleModel import EditModule
from AddModuleModel import AddModule
from components.Database import DB
from model.ModuleModel import Module
from model.UserModel import User
from model.ButtonModel import Button


class BotModel:
    EditNotificationState, EditDataTopic, EditModuleName, SetNotificationState = range(4)

    def __init__(self, token, mqtt):
        self.token = token
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.mqtt = mqtt
        self.mqtt.SetMessageEvent(self.mqtt_message)
        db = DB()
        rows = db.fetchall("SELECT * FROM Modules")
        for row in rows:
            self.mqtt.subscribe(row['topic'])

        buttons_handler = CallbackQueryHandler(self.buttons, pass_user_data=True)
        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help)
        text_handler = MessageHandler(Filters.text, self.search_module)
        edit_module = EditModule(self.mqtt)
        add_module = AddModule(self.mqtt)

        self.load_handlers(self.dispatcher, [edit_module, add_module])

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(text_handler)

        self.dispatcher.add_handler(buttons_handler)
        self.dispatcher.add_error_handler(self.error)
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)
        # log all errors

    def load_handlers(self, dispatcher, handlers_array):
        for handler_class in handlers_array:
            for handler in handler_class.get_handlers():
                dispatcher.add_handler(handler)

    def get_help_text(self):
        return 'Вы можете использовать следующие команды:\n\n' \
               '/addmodule - Добавление модуля умного дома\n' \
               '/on - Включение модуля\n' \
               '/off - Выключение модуля\n'

    def run(self):
        self.updater.start_polling()

    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text='Добро пожаловать!'
                              'Я бот, управляющий умным домом.\n\n'
                         )
        self.help(bot, update)

    def help(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=self.get_help_text())

    def search_module(self, bot, update):
        user = User(update.message.chat_id)
        modules = user.get_modules()
        if len(modules) > 0:
            for module in modules:
                if module.name == update.message.text:
                    buttons = module.get_buttons()
                    if len(buttons) > 0:
                        keyboard = []
                        for (i, button) in enumerate(buttons):
                            keyboard.append(
                                [InlineKeyboardButton('%s' % button.name, callback_data='%s' % button.button_id)])
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        update.message.reply_text("Кнопки модуля", reply_markup=reply_markup)
                    else:
                        update.message.reply_text("Кнопок для этого модуля нет")
        else:
            update.message.reply_text("Азаза, а модулей то нет!")

    def error(self, bot, update, error):
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))

    def buttons(self, bot, update, user_data):
        query = update.callback_query
        button = Button(int(query.data))
        module = Module(button.module_id)
        self.mqtt.publish(module.topic, button.message)

    def mqtt_message(self, client, userdata, msg):
        msg_json = json.loads(msg.payload.decode("utf-8"))
        module = Module(msg_json['token'])
        if module.notify:
            if msg_json['payload'] == '1':
                # 428885624
                self.updater.bot.send_message(module.user_id, "The light was on!")
            elif msg_json['payload'] == '0':
                self.updater.bot.send_message(module.user_id, "The lights are turned off!")
