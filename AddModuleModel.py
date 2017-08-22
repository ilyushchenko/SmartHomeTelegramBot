from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
import sqlite3 as lite
import random
import string


class AddModule:
    ModuleName, ModuleTopic = range(2)

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def get_handlers(self):
        handlers = []
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('addmodule', self.add_module)],

            states={
                self.ModuleName: [MessageHandler(Filters.text, self.set_name_of_module, pass_user_data=True)],

                self.ModuleTopic: [MessageHandler(Filters.text, self.set_topic_of_module, pass_user_data=True)],
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        handlers.append(conv_handler)
        return handlers

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
            self.mqtt.subscribe(user_data["topic"])

            # bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
        update.message.reply_text(
            'Module successfully added!\n\nName: %s\nTopic: %s \n\nPrivate token: <b>%s</b>\nИспользуйте токен, для передачи сообщения с модуля' % (
                user_data["name"], user_data["topic"], token),
            reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    def cancel(self, bot, update):
        user = update.message.from_user
        # self.logger.info("User %s canceled the conversation." % user.first_name)
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END
