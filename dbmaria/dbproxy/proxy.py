# Module Name: Proxy #
# Function: Define commands to manage proxy. #
# Author: Kumo Lam(https://github.com/Kumo-YZX) #
# Last Edit: Feb/19/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'proxy')

    def create(self, definition_file='proxy_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))
    
    def insert_dict(self, para_dict):
        """Insert an item to the table.
           The item should be in dict format.
        """
        self.insert_data(para_dict)

    def random(self, proxy_type):
        """Get a random proxy with specified type.
           Parameter proxy_type is not essential, and http proxy will be returned.
           If provided with 'https', https proxy will be returned.
        """
        if proxy_type == 'https' or proxy_type == 'HTTPS':
            res = self.query_random([{"https": True}], amount=1)
        else:
            res = self.query_random([{"http": True}], amount=1)
        return len(res), res

    def search(self):
        """Search for all the proxy.
        """
        res = self.query_data([])
        return len(res), res

    def update_status(self, proxy_id, connect_times, fail_times):
        """Update the total connect times and fail times of a proxy.
        """
        self.update_data({"connect_times": connect_times, "fail_times": fail_times},
                         [{"proxy_id": {"judge": "=", "value": proxy_id}}])

    def delete(self, proxy_id):
        """Delete a proxy with specified ID.
        """
        self.delete_data([{"proxy_id": {"judge": "=", "value": proxy_id}}])

    def verify(self, address, port):
        """Verify the existence of a proxy.
           The existence, also can be call amount, will be returned.
        """
        res = self.verify_existence([{"address": {"judge": "=", "value": address},
                                     "port": {"judge": "=", "value": port}}])
        return res[0]['COUNT(1)']


def test():
    obj = Table()
    obj.create()


if __name__ == "__main__":
    test()
