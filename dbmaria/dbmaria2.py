# Module Name: Dbmaria2 #
# Function: Interface to mariadb, the 2nd version. #
# Author: Kumo(https://github.com/Kumo-YZX) #
# Last Edit: Jan/22/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbconfig', 'dbconfig.py')

import pymysql.cursors
import pymysql
import dbconfig

# If variable debug is set true, prompt message will be printed.
debug = 0


class DbBase(object):

    def __init__(self, table_name):
        """initialization function
        """
        self.table_name = table_name
        self.middleCode = ''
        self.dbConnection = pymysql.connect(
                                            host=dbconfig.host,
                                            port=dbconfig.port,
                                            user=dbconfig.user,
                                            password=dbconfig.password,
                                            db=dbconfig.db,
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor
        )
        print("Welcome to dbmaria2 world")

    def from_condition(self, condition_list, oa_sequence=0, order_factor=None, amount_limit=None):
        """To form a query code with conditions provided.
           condition_list must not be None, at least '[]' should be proven.
        """
        if oa_sequence:
            first_relationship = ' OR '
            second_relationship = ' AND '
        else:
            first_relationship = ' AND '
            second_relationship = ' OR '

        self.middleCode = ''
        if len(condition_list):
            self.middleCode = ' WHERE '
            # cyc1
            for productIndex in range(len(condition_list)):
                self.middleCode = self.middleCode + '('
                # cyc2
                for everyKey in list(condition_list[productIndex].keys()):
                    if isinstance(condition_list[productIndex][everyKey], dict):
                        if condition_list[productIndex][everyKey]['judge'] == "between":
                            self.middleCode = self.middleCode + '(' + everyKey + ' between ' +\
                                str(condition_list[productIndex][everyKey]['start']) +\
                                ' AND ' + str(condition_list[productIndex][everyKey]['end']) + ')'
                        else:
                            self.middleCode = self.middleCode + everyKey +\
                                              condition_list[productIndex][everyKey]['judge']
                            if isinstance(condition_list[productIndex][everyKey]['value'], basestring):
                                self.middleCode = self.middleCode + '\'' +\
                                                  condition_list[productIndex][everyKey]['value'] + '\''
                            else:
                                self.middleCode = self.middleCode +\
                                                  str(condition_list[productIndex][everyKey]['value'])
                    else:
                        self.middleCode = self.middleCode + everyKey + '='
                        if isinstance(condition_list[productIndex][everyKey], basestring):
                            self.middleCode = self.middleCode + '\'' + condition_list[productIndex][everyKey] + '\''
                        else:
                            self.middleCode = self.middleCode + str(condition_list[productIndex][everyKey])
                    self.middleCode = self.middleCode + first_relationship
                self.middleCode = self.middleCode[0:-(len(first_relationship))] + ')'
                if productIndex != len(condition_list)-1:
                    self.middleCode = self.middleCode + second_relationship

        if isinstance(order_factor, dict):
            var_name = (order_factor.keys())[0]
            if order_factor[var_name] == 'DESC':
                self.middleCode = self.middleCode + ' ORDER BY ' + var_name + ' DESC '
            else:
                self.middleCode = self.middleCode + ' ORDER BY ' + var_name
        
        if isinstance(amount_limit, int):
            self.middleCode = self.middleCode + ' LIMIT ' + str(amount_limit)

        # if debug:
        #     print self.middleCode

    def query_data(self, condition_list, column_list=None, oa_sequence=0, order_factor=None, amount_limit=None):
        """Query data formatted in column_list with condition_list amd oa_sequence.
           column_list must be in V/D format, with condition_list in CD format.
           oa_sequence, order_factor, amount_limit must be boolean, dict, integer values.
        """
        first_code = 'SELECT '
        if isinstance(column_list, list):
            for everyColumn in column_list:
                if isinstance(everyColumn, dict):
                    original_name = (everyColumn.keys())[0]
                    new_name = everyColumn[original_name]
                    first_code = first_code + ' ' + original_name + ' ' + new_name + ','
                else:
                    first_code = first_code + ' ' + str(everyColumn) + ','
        else:
            first_code = first_code + ' *  '

        first_code = first_code[0:-1] + ' FROM ' + self.table_name

        self.from_condition(condition_list, oa_sequence, order_factor, amount_limit)

        sql_code = first_code + self.middleCode

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
            result = cursor.fetchall()

        if debug:
            print('Info: query data from ' + self.table_name + ' completed')

        return result

    def delete_data(self, condition_list, oa_sequence=0):
        first_code = 'DELETE FROM ' + self.table_name

        self.from_condition(condition_list, oa_sequence)

        sql_code = first_code + self.middleCode

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
        self.dbConnection.commit()

        if debug:
            print('Info: delete data from ' + self.table_name + ' completed')

    def verify_existence(self, condition_list, oa_sequence=0):
        first_code = 'SELECT COUNT(1) FROM ' + self.table_name

        self.from_condition(condition_list, oa_sequence)

        sql_code = first_code + self.middleCode

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
            result = cursor.fetchall()

        if debug:
            print('Info: verify data from ' + self.table_name + ' completed')

        return result

    def query_random(self, condition_list, oa_sequence=0, amount=1):
        first_code = 'SELECT * FROM ' + self.table_name 

        self.from_condition(condition_list, oa_sequence, order_factor={"RAND()":""}, amount_limit=amount)

        sql_code = first_code + self.middleCode

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
            result = cursor.fetchall()

        if debug:
            print('Info: query random data from ' + self.table_name + ' completed')

        return result

    def update_data(self, column_dict, condition_list, oa_sequence=0):
        """Update a item by values in column_dict. 
           Keys of column_dict are name of columns and values are new value.
           The condition_list and oa_sequence decides the 
        """
        first_code = 'UPDATE ' + self.table_name
        first_code = first_code + ' SET '

        for everyColumn in column_dict.keys():
            if isinstance(column_dict[everyColumn], basestring):
                first_code = first_code + everyColumn + ' = \'' + column_dict[everyColumn] + '\', '
            else:
                first_code = first_code + everyColumn + ' = ' + str(column_dict[everyColumn]) + ', '

        first_code = first_code[0:-2]

        self.from_condition(condition_list, oa_sequence)

        sql_code = first_code + self.middleCode

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
        self.dbConnection.commit()

        if debug:
            print('Info: update data in ' + self.table_name + ' completed')

    def query_intersect(self, condition_dict_1, condition_dict_2, column_list=None):
        first_code = 'SELECT'
        if column_list is not None:
            for everyColumn in column_list:
                first_code = first_code + ' ' + everyColumn + ','
        else:
            first_code = first_code + ' * '

        first_code = first_code[0:-1] + ' FROM ' + self.table_name

        key1 = (condition_dict_1.keys())[0]
        value1 = condition_dict_1[key1]
        key2 = (condition_dict_2.keys())[0]
        value2 = condition_dict_2[key2]

        sql_code = '(' + first_code + ' WHERE ' + key1 + ' = \'' + value1 + '\')' +\
                  ' INTERSECT ' +\
                  '(' + first_code + ' WHERE ' + key2 + ' = \'' + value2 + '\');'

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
            result = cursor.fetchall()

        if debug:
            print('Info: query data with intersected condition from ' + self.table_name + ' completed')

        return result

    def query_join(self):
        sql_code = 'SELECT a.trainStr, s.seleSta, count(*) arrCount FROM arrival a ' +\
                  'INNER JOIN staInfo s WHERE a.staTele = s.staTele AND s.seleSta = 1 ' +\
                  'GROUP BY a.trainStr HAVING arrCount > 1 ORDER BY arrCount DESC;'

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
            result = cursor.fetchall()

        if debug:
            print('Info: query data with joined condition from ' + self.table_name + ' completed')

        return result

    def create_table(self, parameter_list):
        first_code = 'CREATE TABLE IF NOT EXISTS ' + self.table_name + '('
        sql_code = ''
        last_code = ''
        for everyVar in parameter_list:
            if "primary" in everyVar:
                if "auto_inc" in everyVar:
                    sql_code = everyVar['var_name'] + ' ' + everyVar['varType'] +\
                               ' AUTO_INCREMENT PRIMARY KEY,' + sql_code
                else:
                    sql_code = everyVar['var_name'] + ' ' + everyVar['varType'] + ' PRIMARY KEY,' + sql_code
            else:
                sql_code = sql_code + everyVar['var_name'] + ' ' + everyVar['varType'] + ','

            if "foreign" in everyVar:
                last_code = last_code + 'FOREIGN KEY (' + everyVar['var_name'] + ') REFERENCES ' +\
                            everyVar['foreign']['table'] + '(' + everyVar['foreign']['var'] + '),'
        
        if len(last_code):
            sql_code = first_code + sql_code + last_code[0:-1] + ');'
        else:
            sql_code = first_code + sql_code[0:-1] + ');'

        del first_code
        del last_code

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
        self.dbConnection.commit()

        print('Info: create table ' + self.table_name + ' completed')

    def delete_table(self):
        sql_code = 'DROP TABLE ' + self.table_name + ';'

        if debug:
            print(sql_code)

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
        self.dbConnection.commit()

        print('Info: delete table ' + self.table_name + ' completed')

    def insert_data(self, data_dict):
        first_code = 'INSERT INTO ' + self.table_name + ' ('
        last_code = ') VALUES ('
        for everyKey in list(data_dict.keys()):
            first_code = first_code + everyKey + ','
            if isinstance(data_dict[everyKey], basestring):
                last_code = last_code + '\'' + data_dict[everyKey] + '\','
            else:
                last_code = last_code + str(data_dict[everyKey]) + ','
        sql_code = first_code[0:-1] + last_code[0:-1] + ');'

        del first_code
        del last_code

        with self.dbConnection.cursor() as cursor:
            cursor.execute(sql_code)
        self.dbConnection.commit()

        if debug:
            print(sql_code)
            print('Info: insert data to ' + self.table_name + ' completed')
