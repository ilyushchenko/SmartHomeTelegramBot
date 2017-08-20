from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import paho.mqtt.client as mqtt
import config

import sqlite3 as lite
import json
from EditModuleModel import EditModule
from AddModuleModel import AddModule


class BotModel:
    EditNotificationState, EditDataTopic, EditModuleName, SetNotificationState = range(4)

    def __init__(self, token, mqtt):
        self.token = token
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.mqtt = mqtt
        self.mqtt.SetMessageEvent(self.mqtt_message)
        con = lite.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Modules")
            rows = cur.fetchall()
            for row in rows:
                self.mqtt.subscribe(row[3])
            print(mqtt.subTopics)
        buttons_handler = CallbackQueryHandler(self.buttons, pass_user_data=True)
        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help)
        on_handler = CommandHandler('on', self.on)
        off_handler = CommandHandler('off', self.off)
        text_handler = MessageHandler(Filters.text, self.search_module)
        edit_module = EditModule(self.mqtt)
        add_module = AddModule(self.mqtt)

        self.dispatcher.add_error_handler(self.error)
        self.dispatcher.add_handler(edit_module.bind())
        self.dispatcher.add_handler(add_module.bind())

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(on_handler)
        self.dispatcher.add_handler(off_handler)
        self.dispatcher.add_handler(text_handler)

        self.dispatcher.add_handler(buttons_handler)

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)

        # log all errors

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

        con = lite.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Modules WHERE name LIKE '%s' AND userid = %d" % (
                update.message.text, update.message.chat_id))
            row = cur.fetchone()
            print(row)
            if row is not None:
                print("SELECT * FROM ModuleButtons WHERE moduleid = '%s'" % row[1])
                cur.execute("SELECT * FROM ModuleButtons WHERE moduleid = '%s'" % row[1])
                rows = cur.fetchall()

                keyboard = []

                for (i, row) in enumerate(rows):
                    keyboard.append(
                        [InlineKeyboardButton('%s' % row[2], callback_data='%s' % row[0])])
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Кнопки", reply_markup=reply_markup)

        bot.send_message(chat_id=update.message.chat_id,
                         text='%s Chat ID:%d' % (update.message.text, update.message.chat_id))

    # Global functioons
    def error(self, bot, update, error):
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))

    # Switch functions
    def on(self, bot, update):

        keyboard = [
            [InlineKeyboardButton("Включить", callback_data='1'),
             InlineKeyboardButton("Выключить", callback_data='2')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        # -*- coding: utf-8 -*-
        # mqttc = mqtt.Client("HomeControlTelegramBot")
        # mqttc.connect(config.MQTTAddress, 1883)
        # mqttc.publish("switch/LS01", 1)
        # mqttc.loop(2)

    def buttons(self, bot, update, user_data):
        query = update.callback_query

        con = lite.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute(
                "SELECT topic, message FROM ModuleButtons, Modules WHERE ModuleButtons.buttonid = '%d' AND ModuleButtons.moduleid = Modules.moduleid" % int(
                    query.data))
            row = cur.fetchone()
            if row is not None:
                self.mqtt.publish(row[0], row[1])

    def off(self, bot, update):
        # -*- coding: utf-8 -*-
        mqttc = mqtt.Client("HomeControlTelegramBot")
        mqttc.connect(config.MQTTAddress, 1883)
        mqttc.publish("switch/LS01", 0)
        # mqttc.publish("switch/LS01", json.dumps({'token': '5FbyTRkCr3CTrfG8', 'payload': '0'}))
        mqttc.loop(2)

    def mqtt_message(self, client, userdata, msg):
        msg_json = json.loads(msg.payload.decode("utf-8"))
        con = lite.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Modules WHERE moduleid = '%s'" % msg_json['token'])
            row = cur.fetchone()
            if row is not None:
                if row[4] == 1:
                    if msg_json['payload'] == '1':
                        # 428885624
                        self.updater.bot.send_message(row[0], "The light was on!")
                    elif msg_json['payload'] == '0':
                        self.updater.bot.send_message(row[0], "The lights are turned off!")
