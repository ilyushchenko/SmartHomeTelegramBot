from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
import logging
import paho.mqtt.client as mqtt
import config
import random
import string
import sqlite3 as lite
import json


class BotModel:
    ModuleName, ModuleTopic = range(2)
    EditNotificationState, EditDataTopic, EditModuleName, SetNotificationState = range(4)

    def __init__(self, token):
        self.token = token
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('addmodule', self.add_module)],

            states={
                self.ModuleName: [MessageHandler(Filters.text, self.set_name_of_module, pass_user_data=True)],

                self.ModuleTopic: [MessageHandler(Filters.text, self.set_topic_of_module, pass_user_data=True)],

                # self.LOCATION: [MessageHandler(Filters.location, location),
                #            CommandHandler('skip', skip_location)],
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        edit_module_handler = ConversationHandler(
            entry_points=[CommandHandler('editmodule', self.edit_module)],

            states={
                # TODO: Добавить выбор модуля
                self.EditNotificationState: [RegexHandler('^(Notification)$', self.edit_notification)],
                self.EditDataTopic: [RegexHandler('^(Data Topic)$', self.edit_notification)],
                self.EditModuleName: [RegexHandler('^(Name)$', self.edit_notification)],
                self.SetNotificationState: [RegexHandler('^(On|Off)$', self.set_notification)],
                # self.LOCATION: [MessageHandler(Filters.location, location),
                #            CommandHandler('skip', skip_location)],
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help)
        caps_handler = CommandHandler('caps', self.caps, pass_args=True)
        on_handler = CommandHandler('on', self.on)
        off_handler = CommandHandler('off', self.off)
        echo_handler = MessageHandler(Filters.text, self.echo)

        self.dispatcher.add_handler(conv_handler)
        self.dispatcher.add_handler(edit_module_handler)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(caps_handler)
        self.dispatcher.add_handler(on_handler)
        self.dispatcher.add_handler(off_handler)
        self.dispatcher.add_handler(echo_handler)

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)

        # log all errors
        self.dispatcher.add_error_handler(self.error)

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
        bot.send_message(chat_id=update.message.chat_id, text='%s Chat ID:%d' %(update.message.text, update.message.chat_id))

    def caps(self, bot, update, args):
        print(args)
        text_caps = ' '.join(args).upper()
        bot.send_message(chat_id=update.message.chat_id, text=text_caps)

    # Section of Adding module
    def add_module(self, bot, update):
        update.message.reply_text(
            'Ok! To add a module, you must enter a unique name and sign it on the topic.\n\n'
            'Send /cancel to stop adding.\n\n'
            'Please enter the name of the module.')

        return self.ModuleName

    def set_name_of_module(self, bot, update, user_data):

        user_data["name"] = update.message.text
        reply_keyboard = [['esp', 'home'], ['home/test']]

        update.message.reply_text('Ok, now enter the title of the topic, or choose from existing',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return self.ModuleTopic

    def set_topic_of_module(self, bot, update, user_data):
        user_data["topic"] = update.message.text
        # Подключаемся к базе данных
        con = lite.connect('data.db')

        with con:
            token = ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
            cur = con.cursor()
            command = "INSERT INTO Modules(userid, moduleid, name, topic) VALUES(%d, '%s', '%s', '%s')" % (
                update.message.chat_id, token, user_data['name'], user_data['topic'])
            print(command)
            cur.execute(command)

            # bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
        update.message.reply_text(
            'Module successfully added!\n\nName: %s\nTopic: %s \n\nPrivate token: <b>%s</b>\nИспользуйте токен, для передачи сообщения с модуля' % (
                user_data["name"], user_data["topic"], token),
            reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    def cancel(self, bot, update):
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation." % user.first_name)
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

        # Section of Edit module

    def edit_module(self, bot, update):
        reply_keyboard = [['Notification'], ['Data Topic'], ["Name"]]
        update.message.reply_text('What do you want to change?\n\n',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return self.EditNotificationState

    def edit_notification(self, bot, update):
        reply_keyboard = [["On", "Off"]]

        update.message.reply_text('Enable or disable notifications?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return self.SetNotificationState

    def set_notification(self, bot, update):
        # TODO: Вставить обработку оповещения
        update.message.reply_text('Notification settings successfully changed!',
                                  reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

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

        msg_json = json.loads(msg.payload)

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