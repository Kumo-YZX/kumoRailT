##
# Module Name: Depot #
# Function: Define command to control items in DEPOT table. #
# Author: Kumo(https://github.com/Kumo-YZX) #
# Last Edit: Feb/04/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'depot')

    def create(self, definition_file='depot_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

    def insert(self, depot_id, depot_cn):
        """Insert item to the table.
           Parameter depot_id is self-defined but less than 9999.
           Parameter depot_cn must be in Han(Direct hanzi) format.
        """
        self.insert_data({'depot_id': depot_id, 'depot_cn': depot_cn.encode('hex')})

    def insert_dict(self, parameter_dict):
        """Insert to table with parameter in json format.
        """
        self.insert_data(parameter_dict)

    def search(self, depot_id=0):
        """Search for item in this table.
           Parameters are not essential.
           If provided, designed item will be returned, else it will return all items.
           Results is formatted in existence-result format with raw items.
        """
        if depot_id:
            res = self.query_data([{'depot_id': depot_id}])
        else:
            res = self.query_data([])
        return len(res), res

    def delete(self, depot_id=0):
        """Delete data.
           Parameter depot_id are not essential.
           If provided, designated item will be deleted.
           If not provided, all items will be deleted.
        """
        if depot_id:
            self.delete_data([{'depot_id': depot_id}])
        else:
            self.delete_data([])


def test():
    obj = Table()
    obj.create()
    while(1):
        depot_id = raw_input("depot_id:")
        if int(depot_id) == 9999:
            break
        depot_cn = raw_input("depot_cn:")
        obj.insert(int(depot_id), depot_cn)
    print('dbmaria/dbp2/depot.py: Info: Add depot data completed.')


if __name__ == '__main__':
    test()

