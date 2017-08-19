from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
import sqlite3 as lite


class EditModule:
    CHOOSING, SELECTSETTINGS, CHOOSEMODULE, TYPING_REPLY, EDITBUTTONS, EDITBUTTONSNAME, EDITBUTTONSTOPIC = range(7)

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
                                 pass_user_data=True),
                    RegexHandler('^(Buttons)$',
                                 self.edit_module_busttons,
                                 pass_user_data=True)
                ],

                self.EDITBUTTONS: [
                    RegexHandler('^(Добавить)$',
                                 self.edit_module_busttons_add,
                                 pass_user_data=True),
                    RegexHandler('^(Удалить)$',
                                 self.edit_module_busttons_remove,
                                 pass_user_data=True)
                ],

                self.EDITBUTTONSNAME: [
                    MessageHandler(Filters.text,
                                   self.edit_module_busttons_add_name,
                                   pass_user_data=True)
                ],

                self.EDITBUTTONSTOPIC: [
                    MessageHandler(Filters.text,
                                   self.edit_module_busttons_add_topic,
                                   pass_user_data=True)
                ],



                self.TYPING_REPLY: [MessageHandler(Filters.text,
                                                   self.save_module_settings,
                                                   pass_user_data=True),
                                    ]
            },

            fallbacks=[RegexHandler('^Done$', self.done, pass_user_data=True)]
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

    def edit_module_busttons(self, bot, update, user_data):
        user_data['choise'] = update.message.text
        reply_keyboard = [["Добавить", "Удалить"]]
        update.message.reply_text('Вот, что вы можете сделать с кнопками',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return self.EDITBUTTONS

    def edit_module_busttons_add(self, bot, update, user_data):
        update.message.reply_text('Введите название для кнопки', reply_markup=ReplyKeyboardRemove())
        return self.EDITBUTTONSNAME

    def edit_module_busttons_add_name(self, bot, update, user_data):
        user_data['add_button_name'] = update.message.text
        update.message.reply_text('Введите сообщение для отпраквки на модуль')
        return self.EDITBUTTONSTOPIC

    def edit_module_busttons_add_topic(self, bot, update, user_data):
        user_data['add_button_topic'] = update.message.text
        update.message.reply_text('Кнопка добавлена')
        return self.save_module_settings(bot, update, user_data)

    def edit_module_busttons_remove(self, bot, update, user_data):
        user_data['choise'] = update.message.text
        reply_keyboard = [["Добавить", "Удалить"]]
        update.message.reply_text('Вот, что вы можете сделать с кнопками',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return self.EDITBUTTONS

    def save_module_settings(self, bot, update, user_data):
        message = "Новые настройки сохранены!\n"

        if user_data['choise'] == "Name":
            user_data["name"] = update.message.text
        elif user_data['choise'] == "Topic":
            user_data["topic"] = update.message.text
        elif user_data['choise'] == "Notify":
            if update.message.text == "Да":
                user_data["notify"] = 1
            else:
                user_data["notify"] = 0
        elif user_data['choise'] == "Buttons":
            self.add_button(user_data['moduleid'], user_data['add_button_name'], user_data['add_button_topic'])
        update.message.reply_text(message)
        print(user_data)

        return self.edit_module_state(bot, update, user_data)

    def add_button(self,moduleid, name, topic):
        con = lite.connect('data.db')
        cur = con.cursor()
        command = "INSERT INTO ModuleButtons(moduleid, name, message) VALUES('%s', '%s', '%s')" % \
                  (moduleid, name, topic)
        #TODO: убрать дебаг
        print(command)
        cur.execute(command)
        con.commit()

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
            ['Notify', 'Buttons'],
            ['Done']
        ]

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(self.get_settings_message(user_data), reply_markup=markup)
        return self.SELECTSETTINGS

    def done(self, bot, update, user_data):

        conn = lite.connect("data.db")
        cursor = conn.cursor()

        sql = "UPDATE Modules SET name = '%s', topic = '%s', notify = %d WHERE userid = %d AND moduleid = '%s'" % \
              (user_data["name"], user_data["topic"], user_data["notify"], user_data["userid"], user_data["moduleid"])
        cursor.execute(sql)
        conn.commit()

        user = update.message.from_user
        # self.logger.info("User %s canceled the conversation." % user.first_name)
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END
