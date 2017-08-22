from components.Database import DB
from model.ButtonModel import Button
import random
import string


class Module:
    def __init__(self, token=None):
        self._token = None
        self.__userid = None
        self.__name = None
        self.__topic = None
        self.__notify = None
        if token is not None:
            self.__token = token
            db = DB()
            row = db.fetchone("SELECT * FROM Modules WHERE moduleid = '%s'" % self.token)
            self.__userid = row['userid']
            self.__name = row['name']
            self.__topic = row['topic']
            self.__notify = row['notify']

    def __repr__(self):
        return "Class: Module (Token: %s, User ID: %d, Name: %s, Topic: %s, Notify: %d)" % \
               (self.__token, self.__userid, self.__name, self.__topic, self.__notify)

    @property
    def token(self):
        return self.__token

    @property
    def user_id(self):
        return self.__userid

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value
        db = DB()
        sql = "UPDATE Modules SET name = '%s' WHERE moduleid = '%s'" % (self.name, self.token)
        db.execute(sql)
        db.commit()

    @property
    def topic(self):
        return self.__topic

    @topic.setter
    def topic(self, value):
        self.__topic = value
        db = DB()
        sql = "UPDATE Modules SET topic = '%s' WHERE moduleid = '%s'" % (self.topic, self.token)
        db.execute(sql)
        db.commit()

    @property
    def notify(self) -> bool:
        if self.__notify == 1:
            return True
        else:
            return False

    @notify.setter
    def notify(self, value: bool):
        if value:
            self.__notify = 1
        else:
            self.__notify = 0
        db = DB()
        sql = "UPDATE Modules SET notify = %d WHERE moduleid = '%s'" % (self.notify, self.token)
        db.execute(sql)
        db.commit()

    def create(self, user_id, name, topic, notify=0):
        self.__token = ''.join(
            random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
        self.__userid = user_id
        self.__name = name
        self.__topic = topic
        self.__notify = notify
        sql = "INSERT INTO Modules(userid, moduleid, name, topic, notify) VALUES(%d, '%s', '%s', '%s', %d)" \
              % (self.user_id, self.token, self.name, self.topic, self.__notify)
        db = DB()
        db.execute(sql)
        db.commit()
        return True

    def get_buttons(self):
        buttons = []
        db = DB()
        rows = db.fetchall("SELECT * FROM ModuleButtons WHERE moduleid = '%s'" % self.token)
        for row in rows:
            button = Button(row["buttonid"])
            buttons.append(button)
        return buttons

    def add_button(self, name, message):
        sql = "INSERT INTO ModuleButtons(moduleid, name, message) VALUES('%s', '%s', '%s')" % \
              (self.token, name, message)
        db = DB()
        db.execute(sql)
        db.commit()

    def delete_button(self, button_id: int):
        sql = "DELETE FROM ModuleButtons WHERE buttonid = %d AND moduleid = '%s'" % (button_id, self.token)
        db = DB()
        db.execute(sql)
        db.commit()
