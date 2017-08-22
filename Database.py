# -*- coding: utf-8 -*-
import sqlite3


class DB:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = self.__dict_factory

    def execute(self, sql: str) -> sqlite3.Cursor:
        self.cursor = self.connection.cursor()
        with self.connection:
            return self.cursor.execute(sql)

    def fetchall(self, sql: str):
        with self.connection:
            return self.execute(sql).fetchall()

    def fetchone(self, sql: str):
        with self.connection:
            return self.execute(sql).fetchone()

    def commit(self):
        with self.connection:
            self.connection.commit()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    def __dict_factory(self, cursor, row):
        dict = {}
        for idx, col in enumerate(cursor.description):
            dict[col[0]] = row[idx]
        return dict
