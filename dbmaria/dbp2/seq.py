# Module Name: Seq #
# Function: Define commands to control items in SEQ table. Seqs follow depots. #
# Author: Kumo(https://github.com/Kumo-YZX) #
# Last Edit: Feb/19/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'seq')

    def create(self, definition_file='seq_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def verify(self, key, value):
        """Verify the existence of an item.
           Parameters are all required and should mark data.
        """
        res = self.verify_existence([{key: value}])
        return res[0]['COUNT(1)']

    def import_all(self, seq_file='seq_data.json'):
        """Import data from specified file.
           Repeated value will not be writen.
           Parameter filename are not essential, or default value will be used.
        """
        with open(seq_file) as fi:
            seq_list = json.load(fi)

        for everySeq in seq_list:
            if everySeq['sequence'] == "":
                everySeq['sequence'] = 0
            if self.verify('seq_id', everySeq['sequence']):
                print('Info: seq already exists')
            else:
                if everySeq['staff_dep'] == 0:
                    everySeq['staff_dep'] = 127
                if everySeq['vehicle_dep'] == 0:
                    everySeq['vehicle_dep'] = 127
                self.insert_data({"seq_id": everySeq['sequence'],
                                  "staff": everySeq['staff_dep'],
                                  "depot": everySeq['vehicle_dep'],
                                  "emu_type": everySeq['emu_type'].encode('utf8').encode('hex'),
                                  "remark": everySeq['remark'].encode('utf8').encode('hex')})

    def insert_dict(self, parameter_dict):
        """Insert to table with value in json format.
        """
        self.insert_data(parameter_dict)

# Edited Dec/14/2018: Change Meaningless default value to NONE #
    def delete(self, key=None, value=None):
        """Delete an item.
           Parameters are not essential, causing all data deleted.
           If provided, designed item will be deleted.
        """
        if key is None:
            self.delete_data([])
        else:
            self.delete_data([{key: value}])

    def search(self, key=None, value=None):
        """Search for item(s).
           Parameters are not essential, and all items will be returned.
           If provided, the item they marked will be returned.
           Results is formatted in existence-result value.
        """
        if key is None:
            res = self.query_data([])
        else:
            res = self.query_data([{key: value}])
        
        return len(res), res

    # def update(self, key, value):
    #     pass


def initialize():
    seq_obj = Table()
    seq_obj.create()
    seq_obj.import_all()


if __name__ == "__main__":
    initialize()

