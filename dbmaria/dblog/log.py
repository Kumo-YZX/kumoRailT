# Module Name: log
# Database interface to "log" table, which holds the messages and replies.
# Author: Kumo Lam (https://github.com/Kumo-YZX)
# Last Edit: Mar/16/2019
#


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'log')

    def create(self, definition_file='log_definition.json'):
        """
        Create the table with definition file.
        :param definition_file:
        :return: None
        """
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def insert(self, user_name, message, reply, time_mark):
        """
        Insert a record item.
        Make sure the user exists!
        :param user_name: string
        :param message: string
        :param reply: string
        :param time_mark: string
        :return: None
        """
        self.insert_data({"user_name": user_name[0:28],
                          "message": message,
                          "reply": reply,
                          "time_mark": time_mark})

    def search(self, user_name):
        """
        Search for an user's log.
        The amount of logs will be returned.
        Following the amount is a list of all the logs.
        :param user_name:
        :return: Int, List
        """
        res = self.query_data([{"user_name": user_name}])
        return len(res), res

    def search_by_time(self, time_mark):
        """
        Search for logs with specified time mark.
        :param time_mark: string
        :return: Int, List
        """
        res = self.query_data([{"time_mark": time_mark}])
        return len(res), res

    def delete(self, user_name=None):
        """
        Delete log(s) of an user.
        If the user_name parameter is not set, all logs will be deleted.
        Or only specified logs will be deleted.
        If the user_name
        :param user_name:
        :return:
        """
        if user_name is None:
            self.delete_data([])
        else:
            self.delete_data({"user_name": user_name})


def init():
    obj = Table()
    obj.create()


if __name__ == "__main__":
    init()
