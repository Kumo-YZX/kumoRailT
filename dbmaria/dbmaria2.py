#----------------------------------------------------------------#
# Module Name: Dbmaria2 #
# Function: Interface to mariadb, the 2nd version. #
# Author: Kumo #
# Last Edit: Dec/14/2018 #
#----------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('dbconfig', 'dbconfig.py')

import pymysql.cursors
import pymysql
import json
import dbconfig

# If variable debug is set true, prompt message will be printed.
debug = 0

class dbBase(object):

    def __init__(self, tableName):
        """
        """
        self.tableName = tableName
        self.dbConnection = pymysql.connect(
                                            host = dbconfig.host,
                                            port = dbconfig.port,
                                            user = dbconfig.user,
                                            password = dbconfig.password,
                                            db = dbconfig.db,
                                            charset = 'utf8mb4',
                                            cursorclass = pymysql.cursors.DictCursor
        )
        print "Welcome to dbmaria2 world"

    def formCondition(self, conditionList, OASequence=0, orderFactor=None, amountLimit=None):
        """To form a query code with conditions provided.
           conditionList must not be None, at least '[]' should be proven.
        """
        if OASequence:
            firstRelationship = ' OR '
            secondRelationship = ' AND '
        else:
            firstRelationship = ' AND '
            secondRelationship = ' OR '

        self.middleCode = ''
        if len(conditionList):
            self.middleCode = ' WHERE '
            #cyc1
            for productIndex in range(len(conditionList)):
                self.middleCode = self.middleCode + '('
                #cyc2
                for everyKey in list(conditionList[productIndex].keys()):
                    if isinstance(conditionList[productIndex][everyKey], dict):
                        if conditionList[productIndex][everyKey]['judge'] == "between":
                            self.middleCode = self.middleCode + '(' + everyKey + ' between ' +\
                                str(conditionList[productIndex][everyKey]['start']) +\
                                ' AND ' + str(conditionList[productIndex][everyKey]['end']) + ')'
                        else:
                            self.middleCode = self.middleCode + everyKey + conditionList[productIndex][everyKey]['judge']
                            if isinstance(conditionList[productIndex][everyKey]['value'], basestring):
                                self.middleCode = self.middleCode + '\'' + conditionList[productIndex][everyKey]['value'] + '\''
                            else:
                                self.middleCode = self.middleCode + str(conditionList[productIndex][everyKey]['value'])
                    else:
                        self.middleCode = self.middleCode + everyKey + '='
                        if isinstance(conditionList[productIndex][everyKey], basestring):
                            self.middleCode = self.middleCode + '\'' +conditionList[productIndex][everyKey] + '\''
                        else:
                            self.middleCode = self.middleCode + str(conditionList[productIndex][everyKey])
                    self.middleCode = self.middleCode + firstRelationship
                self.middleCode = self.middleCode[0:-(len(firstRelationship))] + ')'
                if productIndex != len(conditionList)-1:
                    self.middleCode = self.middleCode + secondRelationship

        if isinstance(orderFactor, dict):
            varName = (orderFactor.keys())[0]
            if orderFactor[varName] == 'DESC':
                self.middleCode = self.middleCode + ' ORDER BY ' + varName + ' DESC '
            else:
                self.middleCode = self.middleCode + ' ORDER BY ' + varName
        
        if isinstance(amountLimit, int):
            self.middleCode = self.middleCode + ' LIMIT ' + str(amountLimit)

        # if debug:
        #     print self.middleCode

    def queryData(self, conditionList, columnList=None, OASequence=0, orderFactor=None, amountLimit=None):
        """Query data formatted in columnList with conditionList amd OASequence.
           columnList must be in V/D format, with conditionList in CD format.
           OASequence, orderFactor, amountLimit must be boolean, dict, integer values.
        """
        firstCode = 'SELECT '
        if isinstance(columnList, list):
            for everyColumn in columnList:
                if isinstance(everyColumn, dict):
                    originalName = (everyColumn.keys())[0]
                    newName = everyColumn[originalName]
                    firstCode = firstCode + ' ' + originalName + ' ' + newName + ','
                else:
                    firstCode = firstCode + ' ' + str(everyColumn) + ','
        else:
            firstCode = firstCode + ' *  '

        firstCode = firstCode[0:-1] + ' FROM ' + self.tableName

        self.formCondition(conditionList, OASequence, orderFactor, amountLimit)

        sqlCode = firstCode + self.middleCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'Info: query data from ' + self.tableName + ' completed'

        return result

    def deleteData(self, conditionList, OASequence=0):
        firstCode = 'DELETE FROM ' + self.tableName

        self.formCondition(conditionList, OASequence)

        sqlCode = firstCode + self.middleCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        if debug:
            print 'Info: delete data from ' + self.tableName + ' completed'

    def verifyExistence(self, conditionList, OASequence=0):
        firstCode = 'SELECT COUNT(1) FROM ' + self.tableName

        self.formCondition(conditionList, OASequence)

        sqlCode = firstCode + self.middleCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'Info: verify data from ' + self.tableName + ' completed'

        return result

    def queryRandom(self, conditionList, OASequence=0, amount=1):
        firstCode = 'SELECT * FROM ' + self.tableName 

        self.formCondition(conditionList, OASequence, orderFactor={"RAND()":""}, amountLimit=amount)

        sqlCode = firstCode + self.middleCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'Info: query ranfom data from ' + self.tableName + ' completed'

        return result

    def updateData(self, columnDict, conditionList, OASequence=0):
        """Update a item by values in columnDict. 
           Keys of columnDict are name of columns and values are new value.
           The conditionList and OASequence decides the 
        """
        firstCode = 'UPDATE ' + self.tableName
        firstCode = firstCode + ' SET '

        for everyColumn in columnDict.keys():
            if isinstance(columnDict[everyColumn], basestring):
                firstCode = firstCode + everyColumn + ' = \'' + columnDict[everyColumn] + '\', '
            else:
                firstCode = firstCode + everyColumn + ' = ' + str(columnDict[everyColumn]) + ', '

        firstCode = firstCode[0:-2]

        self.formCondition(conditionList, OASequence)

        sqlCode = firstCode + self.middleCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        if debug:
            print 'Info: update data in ' + self.tableName + ' completed'

    def queryIntersect(self, conditionDict1, conditionDict2, columnList=None):
        firstCode = 'SELECT'
        if columnList is not None:
            for everyColumn in columnList:
                firstCode = firstCode + ' '  + everyColumn + ','
        else:
            firstCode = firstCode + ' * '

        firstCode = firstCode[0:-1] + ' FROM ' + self.tableName

        key1 = (conditionDict1.keys())[0]
        value1 = conditionDict1[key1]
        key2 = (conditionDict2.keys())[0]
        value2 = conditionDict2[key2]

        sqlCode = '(' + firstCode + ' WHERE ' + key1 + ' = \'' + value1 + '\')' +\
                  ' INTERSECT ' +\
                  '(' + firstCode + ' WHERE ' + key2 + ' = \'' + value2 + '\');'

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'Info: query data with intersected condition from ' + self.tableName + ' completed'

        return result

    def queryJoin(self):
        sqlCode = 'SELECT a.trainStr, s.seleSta, count(*) arrCount FROM arrival a ' +\
                  'INNER JOIN staInfo s WHERE a.staTele = s.staTele AND s.seleSta = 1 ' +\
                  'GROUP BY a.trainStr HAVING arrCount > 1 ORDER BY arrCount DESC;'

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'Info: query data with joined condition from ' + self.tableName + ' completed'

        return result


    def createTable(self, parameterList):
        firstCode = 'CREATE TABLE IF NOT EXISTS ' + self.tableName + '('
        sqlCode = ''
        lastCode = ''
        for everyVar in parameterList:
            if "primary" in everyVar:
                if "auto_inc" in everyVar:
                    sqlCode = everyVar['varName'] + ' ' + everyVar['varType'] + ' AUTO_INCREMENT PRIMARY KEY,' + sqlCode
                else:
                    sqlCode = everyVar['varName'] + ' ' + everyVar['varType'] + ' PRIMARY KEY,' + sqlCode
            else:
                sqlCode = sqlCode + everyVar['varName'] + ' ' + everyVar['varType'] + ','

            if "foreign" in everyVar:
                lastCode = lastCode + 'FOREIGN KEY (' + everyVar['varName'] + ') REFERENCES ' + everyVar['foreign']['table'] + '(' + everyVar['foreign']['var'] + '),'
        
        if len(lastCode):
            sqlCode = firstCode + sqlCode + lastCode[0:-1] + ');'
        else:
            sqlCode = firstCode + sqlCode[0:-1] + ');'

        del firstCode
        del lastCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        print 'Info: create table ' + self.tableName + ' completed'

    def deleteTable(self):
        sqlCode = 'DROP TABLE ' + self.tableName + ';'

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        print 'Info: delete table ' + self.tableName + ' completed'

    def insertData(self, dataDict):
        firstCode = 'INSERT INTO ' + self.tableName + ' ('
        lastCode = ') VALUES ('
        for everyKey in list(dataDict.keys()):
            firstCode = firstCode + everyKey + ','
            if isinstance(dataDict[everyKey], basestring):
                lastCode = lastCode + '\'' + dataDict[everyKey] + '\','
            else:
                lastCode = lastCode + str(dataDict[everyKey]) + ','
        sqlCode = firstCode[0:-1] + lastCode[0:-1] + ');'

        del firstCode
        del lastCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        if debug:
            print sqlCode
            print 'Info: insert data to ' + self.tableName + ' completed'

