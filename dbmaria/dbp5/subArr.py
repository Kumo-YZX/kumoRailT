#----------------------------------------------------------------#
# Module Name: SubArr #
# Function: Create SubArr set for monitor process. #
# Author: Kumo #
# Last Edit: Dec/24/2018 #
#----------------------------------------------------------------#

def loadMoudle(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadMoudle('dbmaria', '../dbmaria2.py')
loadMoudle('arrival', '../dbp4/arrival.py')

from dbmaria import dbBase
import arrival
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'subArr')

    def create(self, definitionFile='subArr_definition.json'):
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def insFromArr(self, arrivalId, category=0):
        """Copy a arrival data to subArr table.
           category marks departure/arrival. 
        """
        arrivalObj = arrival.table()
        arrivalStatus, arrivalInfo = arrivalObj.searchById(arrivalId)
        if arrivalStatus:
            if category:
                self.insertData({"arrivalId":arrivalInfo[0]["arrivalId"],
                                 "staTele":arrivalInfo[0]["staTele"],
                                 "staRank":arrivalInfo[0]["staRank"],
                                 "category":1,
                                 "scheduleDate":arrivalInfo[0]["depDate"],
                                 "scheduleTime":arrivalInfo[0]["depTime"],
                                 "trainStr":arrivalInfo[0]["trainStr"],
                                 "status":1})
            else:
                self.insertData({"arrivalId":arrivalInfo[0]["arrivalId"],
                                 "staTele":arrivalInfo[0]["staTele"],
                                 "staRank":arrivalInfo[0]["staRank"],
                                 "category":0,
                                 "scheduleDate":arrivalInfo[0]["arrDate"],
                                 "scheduleTime":arrivalInfo[0]["arrTime"],
                                 "trainStr":arrivalInfo[0]["trainStr"],
                                 "status":1})

    def unable(self, trainStr):
        """Set status to 0 so that it will not be monitored.
        """
        self.updateData({"status":0}, [{"trainStr":{"judge":'=', "value":trainStr}}])

    def catch(self, needStatus=1):
        """Query for all effective subArrs, only subArrId returned.
           The needStatus parameter decides whether useless subArr will be returned.
           Only the ID column will be returned.
        """
        if needStatus:
            queryInfo = self.queryData([{"status":{"judge":'=', "value":1}}], ["subArrId"])
        else:
            queryInfo = self.queryData(columnList=["subArrId"])
        return len(queryInfo), queryInfo

    def delete(self, trainStr):
        self.deleteData([{"trainStr":trainStr}])

    def searchById(self, subArrId):
        """Search for a subArr data with its Id.
           The subArrId parameter must be an integer.
        """
        arrInfo = self.queryData([{"subArrId":{"judge":'=', "value":subArrId}}])
        return len(arrInfo), arrInfo

def initialize():
    obj = table()
    obj.create()

def add():
    arrivalId = int(raw_input("arrivalId:"))
    categoryNum = int(raw_input("category:"))
    obj = table()
    obj.insFromArr(arrivalId, categoryNum)

if __name__ == "__main__":
    import sys
    if sys.argv[1] == 'add':
        add()
    else:
        initialize()




