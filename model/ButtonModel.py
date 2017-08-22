from components.Database import DB


class Button:
    def __init__(self, button_id: int):
        self.__button_id = button_id
        db = DB()
        row = db.fetchone("SELECT * FROM ModuleButtons WHERE buttonid = %d" % self.button_id)
        self.__module_id = row['moduleid']
        self.__name = row['name']
        self.__message = row['message']

    def __repr__(self):
        return "Class: Button (ID: %d, Token: %s, Name: %s, Message: %s)" % \
               (self.button_id, self.module_id, self.name, self.message)

    @property
    def button_id(self):
        return self.__button_id

    @property
    def module_id(self):
        return self.__module_id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value
        db = DB()
        sql = "UPDATE ModuleButtons SET name = '%s' WHERE buttonid = %d" % (self.name, self.button_id)
        db.execute(sql)
        db.commit()

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, value):
        self.__message = value
        db = DB()
        sql = "UPDATE Modules SET message = '%s' WHERE buttonid = %d" % (self.message, self.button_id)
        db.execute(sql)
        db.commit()
