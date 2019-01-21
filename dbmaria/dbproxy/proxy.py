#----------------------------------------------------------------#
# Module Name: Proxy #
# Function: Define commands to manage proxys. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Dec/27/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbmaria', '../dbmaria2.py')

from dbmaria import dbBase
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'proxy')

    def create(self, definitionFile = 'proxy_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))
    
    def insertDict(self, paraDict):
        """Insert an item to the table.
           The item should be in dict format.
        """
        self.insertData(paraDict)

    def random(self, proxyType):
        """Get a random proxy with specified type.
           Parameter proxyType is not essential, and http proxy will be returned.
           If provided with 'https', https proxy will be returned.
        """
        if proxyType == 'https' or proxyType == 'HTTPS':
            res = self.queryRandom([{"https":True}], amount=1)
        else:
            res = self.queryRandom([{"http":True}], amount=1)
        return len(res), res

    def search(self):
        """Search for all the proxys.
        """
        res = self.queryData([])
        return len(res), res

    def updateStatus(self, proxyId, connectTimes, failTimes):
        """Update the total connect times and fail times of a proxy.
        """
        self.updateData({"connectTimes":connectTimes, "failTimes":failTimes},
                        [{"proxyId":{"judge":"=", "value":proxyId}}])

    def delete(self, proxyId):
        """Delete a proxy with specified ID.
        """
        self.deleteData([{"proxyId":{"judge":"=", "value":proxyId}}])

    def verify(self, address, port):
        """Verify the existence of a proxy.
           The existence, also can be call amount, will be returned.
        """
        res = self.verifyExistence([{"address":{"judge":"=", "value":address}, "port":{"judge":"=", "value":port}}])
        return res[0]['COUNT(1)']

def test():
    obj = table()
    obj.create()

if __name__ == "__main__":
    test()