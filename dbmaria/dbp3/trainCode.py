# Module Name: TrainCode #
# Function: Define commands to control items in train_code table. TrainCodes follow trains. #
# Author: Kumo(https://github.com/Kumo-YZX) #
# Last Edit: Feb/20/2019 #

def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json

class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'trainCode')

    def create(self, definition_file='trainCode_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def insert(self, train_str, depart_date, train_code):
        """Insert a train_code data to database.
           The depart_date parameter must be in YYYY-MM-DD format.
           The train_str and train_code parameter must be strings with length of 8 and 12.
        """
        if not(self.verify(train_str, depart_date)):
            self.insert_data({"train_str":train_str, "depart_date":depart_date, "train_code":train_code})

    def search(self, train_str, dep_date=''):
        """Search for a data with particular train_str.
           The dep_date parameter is not essential.
           If provided, result will only contain data behind that date.
           It bust must be in YYYY-MM-DD format.
           Return value is in L(length)/R(result) format.
        """
        if dep_date == '':
            res = self.query_data([{"train_str":train_str}])
        else:
            res = self.query_data([{"train_str":train_str,
                                   "depart_date":{"judge":">=", "value":dep_date}}])
        return len(res), res

    def insert_dict(self, parameter_dict):
        self.insert_data(parameter_dict)

    def search_all(self):
        """Search for all the data in this table.
           Not recommend to use.
        """
        res = self.query_data([])
        return len(res), res

    def delete(self, key=None, value=None):
        """Delete items in this table.
           Parameters are not required, and all items will be deleted.
           If provided, only the item designated will be deleted. 
        """
        if key is None:
            self.delete_data([])
        else:
            self.delete_data([{key:value}])

    def verify(self, train_str, date):
        """Count the data that matches particular train_str and date.
        """
        res = self.verify_existence([{"train_str":train_str,
                                     "depart_date":date}])
        return res[0]['COUNT(1)']

def initialize():
    obj = Table()
    obj.create()

if __name__ == "__main__":
    initialize()


