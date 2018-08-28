#--#
#db interface to mariadb#
#--#

import pymysql.cursors
import pymysql
import json

debug = 0

class dbBase(object):

    def __init__(self, tableName, configFileName = 'dbconfig.json'):
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

    def queryData(self, columnList=[], conditionDict=[]):
        firstCode = 'SELECT '
        if len(columnList):
            for everyColumn in columnList:
                firstCode = firstCode + ' '  + everyColumn + ','
        else:
            firstCode = firstCode + ' *  '

        firstCode = firstCode[0:-1] + ' FROM ' + self.tableName

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


