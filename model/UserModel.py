from components.Database import DB
from model.ModuleModel import Module


class User:
    def __init__(self, uid: int):
        self.__uid = uid

    def __repr__(self):
        return "Class: User (User ID: %d, Token: %s, Name: %s, Message: %s)" % self.__uid

    @property
    def user_id(self):
        return self.__uid

    def get_modules(self):
        modules = []
        db = DB()
        rows = db.fetchall("SELECT * FROM Modules WHERE userid = %d" % self.user_id)
        for row in rows:
            module = Module(row['moduleid'])
            modules.append(module)
        return modules
