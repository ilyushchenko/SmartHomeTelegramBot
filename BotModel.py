from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import paho.mqtt.client as mqtt
import config

import sqlite3 as lite
import json
from EditModuleModel import EditModule
from AddModuleModel import AddModule


class BotModel:
    EditNotificationState, EditDataTopic, EditModuleName, SetNotificationState = range(4)

    def __init__(self, token):
        self.token = token
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help)
        on_handler = CommandHandler('on', self.on)
        off_handler = CommandHandler('off', self.off)
        echo_handler = MessageHandler(Filters.text, self.echo)
        edit_module = EditModule()
        add_module = AddModule()
        self.dispatcher.add_error_handler(self.error)
        self.dispatcher.add_handler(edit_module.bind())
        self.dispatcher.add_handler(add_module.bind())
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(on_handler)
        self.dispatcher.add_handler(off_handler)
        self.dispatcher.add_handler(echo_handler)

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

    def echo(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text='%s Chat ID:%d' % (update.message.text, update.message.chat_id))

    # Global functioons
    def error(self, bot, update, error):
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))

    # Switch functions
    def on(self, bot, update):
        # -*- coding: utf-8 -*-
        mqttc = mqtt.Client("HomeControlTelegramBot")
        mqttc.connect(config.MQTTAddress, 1883)
        mqttc.publish("switch/LS01", 1)
        mqttc.loop(2)

    def off(self, bot, update):
        # -*- coding: utf-8 -*-
        mqttc = mqtt.Client("HomeControlTelegramBot")
        mqttc.connect(config.MQTTAddress, 1883)
        mqttc.publish("switch/LS01", 0)
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
