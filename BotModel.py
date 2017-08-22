from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import paho.mqtt.client as mqtt
import config

import sqlite3 as lite
import json
from EditModuleModel import EditModule
from AddModuleModel import AddModule
from Database import DB


class BotModel:
    EditNotificationState, EditDataTopic, EditModuleName, SetNotificationState = range(4)

    def __init__(self, token, mqtt):
        self.token = token
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.mqtt = mqtt
        self.mqtt.SetMessageEvent(self.mqtt_message)
        db = DB(config.database)
        rows = db.fetchall("SELECT * FROM Modules")
        for row in rows:
            self.mqtt.subscribe(row['topic'])
        print(mqtt.subTopics)

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

        db = DB(config.database)
        row = db.fetchone("SELECT * FROM Modules WHERE name LIKE '%s' AND userid = %d" % (
            update.message.text, update.message.chat_id))
        if row is not None:
            rows = db.fetchall("SELECT * FROM ModuleButtons WHERE moduleid = '%s'" % row['moduleid'])
            keyboard = []
            for (i, row) in enumerate(rows):
                keyboard.append(
                    [InlineKeyboardButton('%s' % row['name'], callback_data='%s' % row['buttonid'])])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Кнопки", reply_markup=reply_markup)

        bot.send_message(chat_id=update.message.chat_id,
                         text='%s Chat ID:%d' % (update.message.text, update.message.chat_id))

    def error(self, bot, update, error):
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))

    def buttons(self, bot, update, user_data):
        query = update.callback_query
        db = DB(config.database)
        row = db.fetchone(
            "SELECT topic, message FROM ModuleButtons, Modules WHERE ModuleButtons.buttonid = '%d' AND ModuleButtons.moduleid = Modules.moduleid" % int(
                query.data))
        if row is not None:
            self.mqtt.publish(row['topic'], row['message'])


    def mqtt_message(self, client, userdata, msg):
        msg_json = json.loads(msg.payload.decode("utf-8"))
        db = DB(config.database)
        row = db.fetchone("SELECT * FROM Modules WHERE moduleid = '%s'" % msg_json['token'])
        if row is not None:
            if row['notify'] == 1:
                if msg_json['payload'] == '1':
                    # 428885624
                    self.updater.bot.send_message(row['userid'], "The light was on!")
                elif msg_json['payload'] == '0':
                    self.updater.bot.send_message(row['userid'], "The lights are turned off!")
