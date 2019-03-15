# Module Name: user
# Database module to access to and manage user table.
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
        DbBase.__init__(self, 'user')

    def __repr__(self):
        print("User Name:")

    def create(self, definition_file='user_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def insert(self, user_name, identity='U', comment=""):
        """
        Insert an item to the table.
        User name are required.
        Identity and comment is optional.
        :param user_name: string
        :param identity: char
        :param comment: string
        :return: None
        """
        self.insert_data({"user_name": user_name[0:28],
                          "identity": identity,
                          "comment": comment})

    def search(self, user_name):
        """
        Search for a user with user name.
        Return value contains a list of dict of the actual item.
        :param user_name: string
        :return: Int, List
        """
        res = self.query_data([{"user_name": user_name}])
        return len(res), res

    def verify(self, user_name):
        """
        Verify the existence of a user.
        Amount of matched item will be returned.
        :param user_name:
        :return: Int
        """
        res = self.verify_existence([{"user_name": user_name}])
        return res[0]['COUNT(1)']

    def set_identity(self, user_name, identify='U'):
        """
        Set the identity for the user who's name is user_name.
        All the parameters are required.
        :param user_name:
        :param identify:
        :return: None
        """
        self.update_data({"identity": identify},
                         [{"user_name": user_name}])

    def set_comment(self, user_name, comment=""):
        """
        Set the comment for the user who's name is user_name.
        All parameters are required.
        :param user_name:
        :param comment:
        :return: None
        """
        self.update_data({"comment": comment},
                         [{"user_name": user_name}])

    def delete(self, user_name=None):
        """
        Delete a user.
        If the user_name parameter is not set, all users will be deleted.
        Or only specified user will be deleted.
        :param user_name:
        :return: None
        """
        if user_name is None:
            self.delete_data([])
        else:
            self.delete_data([{"user_name": user_name}])


def init():
    obj = Table()
    obj.create()


if __name__ == "__main__":
    init()
