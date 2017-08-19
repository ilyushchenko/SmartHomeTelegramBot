from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
import sqlite3 as lite


class EditModule:
    CHOOSING, SELECTSETTINGS, CHOOSEMODULE, TYPING_REPLY = range(4)

    def bind(self):
        edit_module_handler = ConversationHandler(
            entry_points=[CommandHandler('editmodule', self.edit_module, pass_user_data=True)],

            states={
                self.CHOOSEMODULE: [
                    RegexHandler('^(\d+)$',
                                 self.choose_module,
                                 pass_user_data=True)
                ],
                self.CHOOSING: [
                    MessageHandler(Filters.text,
                                   self.edit_module_state,
                                   pass_user_data=True),
                ],
                self.SELECTSETTINGS: [
                    RegexHandler('^(Name|Topic)$',
                                 self.edit_module_settings,
                                 pass_user_data=True),
                    RegexHandler('^(Notify)$',
                                 self.edit_module_notify,
                                 pass_user_data=True)
                ],
                self.TYPING_REPLY: [MessageHandler(Filters.text,
                                                   self.save_module_settings,
                                                   pass_user_data=True),
                                    ]
            },

            fallbacks=[RegexHandler('^Done$', self.cancel, pass_user_data=True)]
        )
        return edit_module_handler

    # Section of Edit module

    def edit_module_settings(self, bot, update, user_data):
        user_data['choise'] = update.message.text
        message = ''
        if update.message.text == "Name":
            message = 'Введите новое имя для модуля'
        elif update.message.text == "Topic":
            message = 'Введите новый топик'
        update.message.reply_text(message)

        return self.TYPING_REPLY

    def edit_module_notify(self, bot, update, user_data):
        user_data['choise'] = update.message.text
        reply_keyboard = [["Да", "Нет"]]
        update.message.reply_text('Вы хотите получать уведомления?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return self.TYPING_REPLY

    def save_module_settings(self, bot, update, user_data):
        message = "Новые настройки сохранены!\n"
        # TODO: Добавить изменение настроек в базу данных

        # con = lite.connect('data.db')
        # with con:
        #     cur = con.cursor()
        #     cur.execute("SELECT * FROM Modules WHERE userid = '%d'" % update.message.chat_id)
        #     rows = cur.fetchall()
        #
        #     modules = []
        #     message = 'Список доступных модулей:\n\n'
        #     for (i, row) in enumerate(rows):
        #         message += '%d - <b>%s</b> [Topic: %s]\n' % (i, row[2], row[3])
        #         modules.append(row)
        # message += '\n\nВведите номер модуля, для изменения параметров'
        # if row is not None:
        #         if row[4] == 1:
        #             if msg_json['payload'] == '1':
        #                 # 428885624
        #                 self.updater.bot.send_message(row[0], "The light was on!")
        #             elif msg_json['payload'] == '0':
        #                 self.updater.bot.send_message(row[0], "The lights are turned off!")
        #
        # reply_keyboard = [['Notification'], ['Data Topic'], ["Name"]]
        update.message.reply_text(message)

        return self.edit_module_state(bot, update, user_data)

    def edit_module(self, bot, update, user_data):
        con = lite.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Modules WHERE userid = '%d'" % update.message.chat_id)
            rows = cur.fetchall()
            modules = []
            message = 'Список доступных модулей:\n\n'
            for (i, row) in enumerate(rows):
                message += '%d - <b>%s</b> [Topic: %s]\n' % (i, row[2], row[3])
                modules.append(row)
            message += '\n\nВведите номер модуля, для изменения параметров'
        user_data['modules'] = modules
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return self.CHOOSEMODULE

    def choose_module(self, bot, update, user_data):
        module_number = int(update.message.text)
        if module_number >= 0 and module_number < len(user_data["modules"]):
            module = user_data["modules"][module_number]
            del user_data["modules"]
            user_data["userid"] = module[0]
            user_data["moduleid"] = module[1]
            user_data["name"] = module[2]
            user_data["topic"] = module[3]
            user_data["notify"] = module[4]
            return self.edit_module_state(bot, update, user_data)
        else:
            update.message.reply_text('Упс! Такого модуля не найдено!\n'
                                      'Попробуйте ввести номер еще раз')
            return self.CHOOSEMODULE

    def get_settings_message(self, user_data):
        message = 'Ок! Текущие настройки:\n'
        message += 'Название: %s\n' % user_data["name"]
        message += 'Топик: %s\n' % user_data["topic"]
        message += 'Уведомление: %d\n\n' % user_data["notify"]
        message += 'Выберите, что хотите изменить или сохраните настройки'
        return message

    def edit_module_state(self, bot, update, user_data):
        reply_keyboard = [
            ['Name', 'Topic'],
            ['Notify'],
            ['Done']
        ]

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(self.get_settings_message(user_data), reply_markup=markup)
        return self.SELECTSETTINGS

    def cancel(self, bot, update, user_data):
        user = update.message.from_user
        # self.logger.info("User %s canceled the conversation." % user.first_name)
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END
