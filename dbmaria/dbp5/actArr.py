#----------------------------------------------------------------#
# Module Name: ActArr #
# Function: Record the actucal status of an arrival. #
# Author: Kumo #
# Last Edit: Dec/24/2018 #
#----------------------------------------------------------------#

def loadMoudle(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadMoudle('dbmaria', '../dbmaria2.py')
loadMoudle('arrival', '../dbp4/arrival.py')
loadMoudle('subArr', 'subArr.py')

from dbmaria import dbBase
import arrival, subArr
import json

class table(dbBase):

    def __init__(self):
        dbBase.__init__(self, 'actArr')

    def create(self, definitionFile="actArr_definition.json"):
        """Create an actArr table.
        """
        with open(definitionFile) as fi:
            self.createTable(json.load(fi))

    def new(self, subArrId, theDate):
        """add a new log to actArr table with no data.
           subArrId must be a int marking a subArr data, or an error will be raised.
           today must be a date
        """
        import datetime
        subArrDB = subArr.table()
        subArrStatus, subArrInfo = subArrDB.searchById(subArrId)
        scheduleDate = theDate + datetime.timedelta(days = subArrInfo[0]["scheduleDate"])
        if subArrStatus:
            self.insertData({"subArrId":subArrId,
                             "scheduleDate":scheduleDate.strftime("%Y-%m-%d"),
                             "scheduleTime":subArrInfo[0]["scheduleTime"],
                             "delay":0,
                             "queryMark":0})
        else:
            raise IndexError('subArr do not exist!')

    def catch(self, theDate, theTime):
        """Get void log with a specified date and a up(no more than) limit time.
           theDate can be in string format.
           theTime must be in intager format.
        """
        catchInfo = self.queryData([{"scheduleDate":{"judge":'=', "value":theDate},
                                     "scheduleTime":{"judge":'<=', "value":theTime},
                                     "queryMark":{"judge":'=', "value":0}}])
        return len(catchInfo), catchInfo

    def write(self, actArrId, delay, updateMark=0):
        """Write data to an unmarked log.
           The actArrId parameter must be a int marking an existing log.
           The updateMark parameter should be 1 if you want to finish monitoring.
           The delay parameter marks the delay time (minus menas train is ahead of time.)
        """
        if updateMark:
            self.updateData({"queryMark":1, "delay":delay}, [{"actArrId":{"judge":'=', "value":actArrId}}])
        else:
            self.updateData({"delay":delay}, [{"actArrId":{"judge":'=', "value":actArrId}}])

    def search(self, subArrId):
        """Search for details of a sheet of actArr.
           subArrId must be a int.
        """
        searchInfo = self.queryData([], [{"subArrId":{"judge":'=', "value":subArrId}}])
        return len(searchInfo), searchInfo

def initilize():
    actArrObj = table()
    actArrObj.create()

if __name__ == "__main__":
    initilize()
