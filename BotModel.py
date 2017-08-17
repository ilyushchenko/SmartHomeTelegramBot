from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import paho.mqtt.client as mqtt
import config


class BotModel:
    ModuleName, ModuleTopic = range(2)

    def __init__(self, token):
        self.token = token
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('addmodule', self.AddModule)],

            states={
                self.ModuleName: [MessageHandler(Filters.text, self.SetNameOfModule)],

                self.ModuleTopic: [MessageHandler(Filters.text, self.SetTopicOfModule)],

                # self.LOCATION: [MessageHandler(Filters.location, location),
                #            CommandHandler('skip', skip_location)],
            },

            fallbacks=[CommandHandler('cancel', self.Cancel)]
        )

        start_handler = CommandHandler('start', self.Start)
        caps_handler = CommandHandler('caps', self.caps, pass_args=True)
        on_handler = CommandHandler('on', self.On)
        off_handler = CommandHandler('off', self.Off)
        echo_handler = MessageHandler(Filters.text, self.echo)

        self.dispatcher.add_handler(conv_handler)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(caps_handler)
        self.dispatcher.add_handler(on_handler)
        self.dispatcher.add_handler(off_handler)
        self.dispatcher.add_handler(echo_handler)

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)

        # log all errors
        self.dispatcher.add_error_handler(self.Error)

    def Run(self):
        self.updater.start_polling()

    def Start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

    def echo(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

    def caps(self, bot, update, args):
        print(args)
        text_caps = ' '.join(args).upper()
        bot.send_message(chat_id=update.message.chat_id, text=text_caps)

    def SetAlarm(self, bot, update):
        pass

    # Section of Adding module
    def AddModule(self, bot, update):
        update.message.reply_text(
            'Ok! To add a module, you must enter a unique name and sign it on the topic.\n\n'
            'Send /cancel to stop adding.\n\n'
            'Please enter the name of the module.')

        return self.ModuleName

    def SetNameOfModule(self, bot, update):
        reply_keyboard = [['esp', 'home'], ['home/test']]

        update.message.reply_text('Ok, now enter the title of the topic, or choose from existing',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return self.ModuleTopic

    def SetTopicOfModule(self, bot, update):
        update.message.reply_text('Module successfully added!',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def Cancel(self, bot, update):
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation." % user.first_name)
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    # Global functioons
    def Error(self, bot, update, error):
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))

    # Switch functions
    def On(self, bot, update):
        # -*- coding: utf-8 -*-
        mqttc = mqtt.Client("HomeControlTelegramBot")
        mqttc.connect(config.MQTTAddress, 1883)
        mqttc.publish("switch/LS01", 1)
        mqttc.loop(2)

    def Off(self, bot, update):
        # -*- coding: utf-8 -*-
        mqttc = mqtt.Client("HomeControlTelegramBot")
        mqttc.connect(config.MQTTAddress, 1883)
        mqttc.publish("switch/LS01", 0)
        mqttc.loop(2)

    def MqttMessage(self, client, userdata, msg):
        if(msg.topic == "info/switch/LS01"):
            if msg.payload == b'1':
                 #428885624
                self.updater.bot.send_message(428885624, "The light was on!")
            elif msg.payload == b'0':
                self.updater.bot.send_message(428885624, "The lights are turned off!")