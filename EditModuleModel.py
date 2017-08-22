from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from model.UserModel import User
from model.ModuleModel import Module


class EditModule:
    CHOOSING_MODULE_NUMBER, \
    CHOOSING, \
    SELECT_SETTINGS, \
    TYPING_REPLY, \
    TYPING_MODULE_TOPIC, \
    TYPING_MODULE_NAME, \
    EDIT_NOTIFY, \
    EDIT_NOTIFY_SAVE, \
    EDIT_BUTTONS, \
    CHOOSING_REMOVE_BUTTON, \
    CHOOSING_REMOVE_BUTTON_CONFIRM, \
    ADD_BUTTONS_NAME, \
    ADD_BUTTONS_MESSAGE = range(13)

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def get_handlers(self):
        handlers = []
        edit_module_handler = ConversationHandler(
            entry_points=[CommandHandler('editmodule', self.__edit_module, pass_user_data=True)],

            states={
                self.CHOOSING_MODULE_NUMBER: [
                    RegexHandler('^(\d*)$',
                                 self.__choose_module,
                                 pass_user_data=True),
                    CommandHandler("cancel", self.__cancel, pass_user_data=True),
                    MessageHandler(Filters.all,
                                   self.__choose_module_error,
                                   pass_user_data=True)
                ],
                self.CHOOSING: [
                    MessageHandler(Filters.text,
                                   self.__edit_module_state,
                                   pass_user_data=True),
                ],
                self.SELECT_SETTINGS: [
                    RegexHandler('^(Name)$',
                                 self.__edit_module_name),
                    RegexHandler('^(Topic)$',
                                 self.__edit_module_topic),
                    RegexHandler('^(Notify)$',
                                 self.__edit_module_notify),
                    RegexHandler('^(Buttons)$',
                                 self.__edit_module_busttons)
                ],
                self.TYPING_MODULE_NAME: [
                    MessageHandler(Filters.text,
                                   self.__edit_module_name_save,
                                   pass_user_data=True)
                ],
                self.TYPING_MODULE_TOPIC: [
                    MessageHandler(Filters.text,
                                   self.__edit_module_topic_save,
                                   pass_user_data=True)
                ],
                self.EDIT_NOTIFY_SAVE: [
                    RegexHandler('^(Да|Нет)$',
                                 self.__edit_module_notify_save,
                                 pass_user_data=True)
                ],
                self.EDIT_BUTTONS: [
                    RegexHandler('^(Добавить)$',
                                 self.__edit_module_busttons_add,
                                 pass_user_data=True),
                    RegexHandler('^(Удалить)$',
                                 self.__edit_module_busttons_remove,
                                 pass_user_data=True)
                ],
                self.CHOOSING_REMOVE_BUTTON: [
                    RegexHandler('^(\d*)$',
                                 self.__edit_module_busttons_remove_select,
                                 pass_user_data=True),
                ],
                self.CHOOSING_REMOVE_BUTTON_CONFIRM: [
                    RegexHandler('^(Да|Нет)$',
                                 self.__edit_module_busttons_remove_confirm,
                                 pass_user_data=True),
                ],
                self.ADD_BUTTONS_NAME: [
                    MessageHandler(Filters.text,
                                   self.__edit_module_busttons_add_name,
                                   pass_user_data=True)
                ],

                self.ADD_BUTTONS_MESSAGE: [
                    MessageHandler(Filters.text,
                                   self.__edit_module_busttons_add_message,
                                   pass_user_data=True)
                ],

                self.TYPING_REPLY: [MessageHandler(Filters.text,
                                                   self.__save_module_settings,
                                                   pass_user_data=True),
                                    ]
            },

            fallbacks=[
                RegexHandler('^Done$', self.__done, pass_user_data=True),
            ]
        )
        handlers.append(edit_module_handler)
        return handlers

    # Section of Edit module

    def __edit_module_topic(self, bot, update):
        message = 'Введите новый топик'
        update.message.reply_text(message)
        return self.TYPING_MODULE_TOPIC

    def __edit_module_topic_save(self, bot, update, user_data):
        module = Module(user_data['token'])
        module.topic = update.message.text
        update.message.reply_text("Топик модуля изменен")
        return self.__edit_module_state(bot, update, user_data)

    def __edit_module_name(self, bot, update):
        message = 'Введите новое имя для модуля'
        update.message.reply_text(message)
        return self.TYPING_MODULE_NAME

    def __edit_module_name_save(self, bot, update, user_data):
        module = Module(user_data['token'])
        module.name = update.message.text
        update.message.reply_text("Текст модуля изменен")
        return self.__edit_module_state(bot, update, user_data)

    def __edit_module_notify(self, bot, update):
        reply_keyboard = [["Да", "Нет"]]
        update.message.reply_text('Вы хотите получать уведомления?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return self.EDIT_NOTIFY_SAVE

    def __edit_module_notify_save(self, bot, update, user_data):
        module = Module(user_data['token'])
        if update.message.text == "Да":
            module.notify = True
        else:
            module.notify = False
        update.message.reply_text('Настройки уведомлений успешно изменены',
                                  reply_markup=ReplyKeyboardRemove())
        return self.__edit_module_state(bot, update, user_data)

    def __edit_module_busttons(self, bot, update):
        reply_keyboard = [["Добавить", "Удалить"]]
        update.message.reply_text('Вот, что вы можете сделать с кнопками',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return self.EDIT_BUTTONS

    def __edit_module_busttons_add(self, bot, update, user_data):
        update.message.reply_text('Введите название для кнопки', reply_markup=ReplyKeyboardRemove())
        return self.ADD_BUTTONS_NAME

    def __edit_module_busttons_add_name(self, bot, update, user_data):
        user_data['add_button_name'] = update.message.text
        update.message.reply_text('Введите сообщение для отпраквки на модуль')
        return self.ADD_BUTTONS_MESSAGE

    def __edit_module_busttons_add_message(self, bot, update, user_data):
        user_data['add_button_message'] = update.message.text
        module = Module(user_data['token'])
        module.add_button(user_data['add_button_name'], user_data['add_button_message'])
        del user_data['add_button_name']
        del user_data['add_button_message']
        update.message.reply_text('Кнопка добавлена')
        return self.__save_module_settings(bot, update, user_data)

    def __get_buttons_message(self, buttons):
        message = ''
        for (i, button) in enumerate(buttons):
            message += '%d - %s [Message: %s]\n' % (i, button.name, button.message)
        return message

    def __edit_module_busttons_remove(self, bot, update, user_data):
        message = 'Вот вписок кнопок, для этого модуля:\n\n'
        module = Module(user_data['token'])
        buttons = module.get_buttons()
        message += self.__get_buttons_message(buttons)
        message += 'Введите номер кнопки, для удаления'
        user_data['remove_buttons'] = buttons
        update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        return self.CHOOSING_REMOVE_BUTTON

    def __edit_module_busttons_remove_select(self, bot, update, user_data):
        button_number = int(update.message.text)
        if button_number >= 0 and button_number < len(user_data["remove_buttons"]):
            button = user_data["remove_buttons"][button_number]
            del user_data["remove_buttons"]
            user_data["remove_button"] = button.button_id

            reply_keyboard = [["Да", "Нет"]]
            update.message.reply_text('Вы точно хотитеудалить кнопку',
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                       resize_keyboard=True))
            return self.CHOOSING_REMOVE_BUTTON_CONFIRM
        else:
            update.message.reply_text('Ой, такой кнопки нет!\n'
                                      'Номер должен быть от 0 до %d \n\n'
                                      'Попробуйте ввести номер еще раз или введите /cancel, для отмены'
                                      % (len(user_data["remove_buttons"]) - 1))
            return self.CHOOSING_REMOVE_BUTTON

    def __edit_module_busttons_remove_confirm(self, bot, update, user_data):
        if update.message.text == "Да":
            module = Module(user_data['token'])
            module.delete_button(int(user_data["remove_button"]))
            del user_data["remove_button"]
            update.message.reply_text('Кнопка удалена', reply_markup=ReplyKeyboardRemove())
            return self.__edit_module_state(bot, update, user_data)
        else:
            del user_data["remove_button"]
            update.message.reply_text('Кнопка не удалена', reply_markup=ReplyKeyboardRemove())
            return self.__edit_module_state(bot, update, user_data)

    def __save_module_settings(self, bot, update, user_data):
        message = "Новые настройки сохранены!\n"

        # if user_data['choise'] == "Name":
        #     user_data["name"] = update.message.text
        # elif user_data['choise'] == "Topic":
        #     user_data["last_topic"] = update.message.text
        #     user_data["topic"] = user_data["topic"]
        # elif user_data['choise'] == "Notify":
        #     if update.message.text == "Да":
        #         user_data["notify"] = 1
        #     else:
        #         user_data["notify"] = 0
        # elif user_data['choise'] == "Buttons":
        #     self.__add_button(user_data['moduleid'], user_data['add_button_name'], user_data['add_button_topic'])
        # update.message.reply_text(message)

        return self.__edit_module_state(bot, update, user_data)

    def __add_button(self, moduleid, name, message):
        command = "INSERT INTO ModuleButtons(moduleid, name, message) VALUES('%s', '%s', '%s')" % \
                  (moduleid, name, message)
        # self.db.execute(command)
        # self.db.commit()

    def __edit_module(self, bot, update, user_data):
        user = User(int(update.message.chat_id))
        modules = user.get_modules()
        print(modules)
        message = 'Введите номер модуля:\n\n'
        for (i, module) in enumerate(modules):
            message += '%d - <b>%s</b> [Topic: %s]\n' % (i, module.name, module.topic)
        user_data["modules"] = modules
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return self.CHOOSING_MODULE_NUMBER

    def __choose_module(self, bot, update, user_data):
        module_number = int(update.message.text)
        if module_number >= 0 and module_number < len(user_data["modules"]):
            module = user_data["modules"][module_number]
            del user_data["modules"]
            user_data['token'] = module.token
            return self.__edit_module_state(bot, update, user_data)
        else:
            update.message.reply_text('Ой, такого молудя нет!\n'
                                      'Номер должен быть от 0 до %d \n\n'
                                      'Попробуйте ввести номер еще раз или введите /cancel, для отмены'
                                      % (len(user_data["modules"]) - 1))
            return self.CHOOSING_MODULE_NUMBER

    def __choose_module_error(self, bot, update, user_data):
        message = 'Упс! Ошибочка\n' \
                  'Нужно ввести цифру от <b>0 до %d</b> или /cancel, для отмены' % (len(user_data["modules"]) - 1)
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return self.CHOOSING_MODULE_NUMBER

    def __get_settings_message(self, user_data):
        module = Module(user_data['token'])
        message = 'Ок! Текущие настройки:\n'
        message += 'Название: %s\n' % module.name
        message += 'Топик: %s\n' % module.topic
        if module.notify:
            message += 'Уведомление: Да\n\n'
        else:
            message += 'Уведомление: Нет\n\n'
        message += 'Выберите, что хотите изменить или сохраните настройки'
        return message

    def __edit_module_state(self, bot, update, user_data):
        reply_keyboard = [
            ['Name', 'Topic'],
            ['Notify', 'Buttons'],
            ['Done']
        ]

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(self.__get_settings_message(user_data), reply_markup=markup)
        return self.SELECT_SETTINGS

    def __done(self, bot, update, user_data):
        del user_data
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def __cancel(self, bot, update, user_data):
        del user_data
        update.message.reply_text('Изменение настроек модуля отменено',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
