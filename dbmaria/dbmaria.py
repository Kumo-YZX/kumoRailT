#--#
#db interface to mariadb#
#--#

import pymysql.cursors
import pymysql
import json

debug = 0

class dbBase(object):

    def __init__(self, tableName, configFileName = '/var/ww4/kumoRailT/dbmaria/dbconfig.json'):
        self.tableName = tableName
        with open(configFileName) as cofi:
            config = json.load(cofi)
        self.dbConnection = pymysql.connect(host=config['host'],
                                            port=config['port'],
                                            user=config['user'],
                                            password=config['password'],
                                            db=config['db'],
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor
        )
    
    def createTable(self, varList):
        firstCode = 'CREATE TABLE IF NOT EXISTS ' + self.tableName + '('
        sqlCode = ''
        lastCode = ''
        for everyVar in varList:
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

        #if debug:
        print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        print 'CREATE TABLE ' + self.tableName + ' DONE'
        return 1

    def deleteTable(self):
        sqlCode = 'DROP TABLE ' + self.tableName + ');'

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        print 'DELETE TABLE ' + self.tableName + ' DONE'
        return 1
    
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
            print 'INSERT DATA TO ' + self.tableName + ' DONE'

    def deleteData(self, conditionDict=[]):
        firstCode = 'DELETE FROM ' + self.tableName
        lastCode = ' WHERE '
        if len(conditionDict):
            for productIndex in range(len(conditionDict)):
                lastCode = lastCode + '('
                for everyKey in list(conditionDict[productIndex].keys()):
                    lastCode = lastCode + everyKey + conditionDict[productIndex][everyKey]['judge'] 
                    if isinstance(conditionDict[productIndex][everyKey]['value'], basestring):
                        lastCode = lastCode + '\'' + conditionDict[productIndex][everyKey]['value'] + '\''
                    else:
                        lastCode = lastCode + str(conditionDict[productIndex][everyKey]['value'])
                    lastCode = lastCode + ' AND '
                lastCode = lastCode[0:-5] + ')'
                if not(productIndex==len(conditionDict)-1):
                    lastCode = lastCode + ' OR '
            lastCode = lastCode + ';'
        else:
            lastCode = ';'

        sqlCode = firstCode + lastCode

        del firstCode
        del lastCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        if debug:
            print 'DELETE DATA FROM ' + self.tableName + ' DONE'
        return 1

    def queryData(self, columnList=[], conditionDict=[], orderDict={}):
        firstCode = 'SELECT '
        if len(columnList):
            for everyColumn in columnList:
                firstCode = firstCode + ' '  + everyColumn + ','
        else:
            firstCode = firstCode + ' * '

        firstCode = firstCode[0:-1] + ' FROM ' + self.tableName

        conditionCode = ' WHERE '
        if len(conditionDict):
            for productIndex in range(len(conditionDict)):
                conditionCode = conditionCode + '('
                for everyKey in list(conditionDict[productIndex].keys()):
                    if conditionDict[productIndex][everyKey]['judge'] == 'between':
                        conditionCode = conditionCode + '(' + everyKey + ' between ' +\
                                   str(conditionDict[productIndex][everyKey]['start']) +\
                                   ' AND ' + str(conditionDict[productIndex][everyKey]['end']) + ')'
                    else:
                        conditionCode = conditionCode + everyKey + conditionDict[productIndex][everyKey]['judge']
                        if isinstance(conditionDict[productIndex][everyKey]['value'], basestring):
                            conditionCode = conditionCode + '\'' + conditionDict[productIndex][everyKey]['value'] + '\''
                        else:
                            conditionCode = conditionCode + str(conditionDict[productIndex][everyKey]['value'])
                    conditionCode = conditionCode + ' AND '
                conditionCode = conditionCode[0:-5] + ')'
                if not(productIndex==len(conditionDict)-1):
                    conditionCode = conditionCode + ' OR '
            conditionCode = conditionCode
        else:
            conditionCode = ''

        orderCode = ''
        if len(orderDict):
            if 'variable' in orderDict:
                orderCode = orderCode + ' ORDER BY ' + orderDict['variable']
            if 'desc' in orderDict:
                if orderDict['desc']:
                    orderCode = orderCode + ' DESC '
            if 'amount' in orderDict:
                orderCode = orderCode + ' LIMIT ' + str(orderDict['amount'])

        sqlCode = firstCode + conditionCode + orderCode + ';'
        del firstCode
        del conditionCode
        del orderCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'QUERT DATA FROM ' + self.tableName + ' DONE'

        return result

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
            print 'QUERT DATA FROM ' + self.tableName + ' DONE'

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
            print 'QUERT DATA FROM ' + self.tableName + ' DONE'

        return result


    def verifyExistence(self, conditionDict=[]):
        firstCode = 'SELECT COUNT(1) FROM ' + self.tableName

        lastCode = ' WHERE '
        if len(conditionDict):
            for productIndex in range(len(conditionDict)):
                lastCode = lastCode + '('
                for everyKey in list(conditionDict[productIndex].keys()):
                    lastCode = lastCode + everyKey + conditionDict[productIndex][everyKey]['judge'] 
                    if isinstance(conditionDict[productIndex][everyKey]['value'], basestring):
                        lastCode = lastCode + '\'' + conditionDict[productIndex][everyKey]['value'] + '\''
                    else:
                        lastCode = lastCode + str(conditionDict[productIndex][everyKey]['value'])
                    lastCode = lastCode + ' AND '
                lastCode = lastCode[0:-5] + ')'
                if not(productIndex==len(conditionDict)-1):
                    lastCode = lastCode + ' OR '
            lastCode = lastCode + ';'
        else:
            lastCode = ';'

        sqlCode = firstCode + lastCode
        del firstCode
        del lastCode

        if debug:
            print sqlCode
        # print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'VERIFY DATA FROM ' + self.tableName + ' DONE'

        return result[0]['COUNT(1)']

    def updateData(self, valueDict, conditionDict=[]):
        firstCode = 'UPDATE ' + self.tableName + ' SET '
        sqlCode = ''
        for everyValue in list(valueDict.keys()):
            sqlCode = sqlCode + everyValue + ' = '
            if isinstance(valueDict[everyValue], basestring):
                sqlCode = sqlCode + '\'' +valueDict[everyValue] + '\'' + ', '
            else:
                sqlCode = sqlCode + str(valueDict[everyValue]) + ', '
        sqlCode = sqlCode[0:-2]

        lastCode = ' WHERE '
        if len(conditionDict):
            for productIndex in range(len(conditionDict)):
                lastCode = lastCode + '('
                for everyKey in list(conditionDict[productIndex].keys()):
                    lastCode = lastCode + everyKey + conditionDict[productIndex][everyKey]['judge'] 
                    if isinstance(conditionDict[productIndex][everyKey]['value'], basestring):
                        lastCode = lastCode + '\'' + conditionDict[productIndex][everyKey]['value'] + '\''
                    else:
                        lastCode = lastCode + str(conditionDict[productIndex][everyKey]['value'])
                    lastCode = lastCode + ' AND '
                lastCode = lastCode[0:-5] + ')'
                if not(productIndex==len(conditionDict)-1):
                    lastCode = lastCode + ' OR '
            lastCode = lastCode + ';'
        else:
            lastCode = ';'

        sqlCode = firstCode + sqlCode + lastCode
        del firstCode
        del lastCode

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
        self.dbConnection.commit()

        if debug:
            print 'UPDATE DATA OF ' + self.tableName + ' DONE'
        return 1

    def searchRandom(self, key='', value=1):
        sqlCode = 'SELECT * FROM ' + self.tableName + ' WHERE ' + key + ' = ' + str(value) + ' ORDER BY RAND() LIMIT 1;'

        if debug:
            print sqlCode

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sqlCode)
            result = cursor.fetchall()

        if debug:
            print 'QUERT RANDOM FROM ' + self.tableName + ' DONE'

        return result


