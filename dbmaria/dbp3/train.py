# Module Name: Train #
# Function: Define commands to control items in TRAIN table. #
# Author: Kumo(https://github.com/Kumo-YZX) #
# Last Edit: Feb/19/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('dbmaria', '../dbmaria2.py')

from dbmaria import DbBase
import json

webClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'O']
actualClass = ['G', 'D', 'C', 'Z', 'T', 'K', 'S', 'Y', 'P']


class Table(DbBase):

    def __init__(self):
        DbBase.__init__(self, 'train')

    def create(self, definition_file='train_definition.json'):
        with open(definition_file) as fi:
            self.create_table(json.load(fi))

# ImportFile function is already moved to trainHook
#   def importFile(self, date, trainFile='trainData.json'):

    def insert_base(self, train_num0, train_num1, train_class, train_str, status):
        """Insert a train to the table.
           All parameters are required.
        """
        self.insert_data({"train_num0": train_num0,
                          "train_num1": train_num1,
                          "train_class": train_class,
                          "train_str": train_str,
                          "status": status
                          })
    
    def insert_dict(self, parameter_dict):
        """Insert data formatted in dict to database directly.
        """
        self.insert_data(parameter_dict)

    def update_base(self, original_train, present_train, train_class):
        """Update the train_num1 value of a train.
           All parameters are required.
           TrainNum1 value of the item that original_train matches will be updated to present_train.
        """
        self.update_data({"train_num1": present_train},
                         [{"train_num0": original_train,
                          "train_class": train_class}])

    def update_status(self, train_num, train_class, status):
        """Change the status of a train.
           All parameters are required.
        """
        self.update_data({"status": status},
                         [{"train_class": train_class},
                         {"train_num0": train_num,
                          "train_num1": train_num}],
                         oa_sequence=1)

    def update_seq(self, train_str, seq_id, seq_rank):
        """Change the seq value of a train.
           All parameters are required.
           SeqId is the serial number of the sequence they subordinated.
           SeqRank is the sort in this sequence.
        """
        self.update_data({"seq_id": seq_id,
                         "seq_rank": seq_rank},
                         [{"train_str": train_str}])

    def verify_train(self, train_class, train_num):
        """Count the trains that match the condition.
           The train_class must be a character and train_num must be a integer less than 10k.
           Result is a single number.
        """
        res = self.verify_existence([{"train_class": train_class},
                                    {"train_num0": train_num,
                                     "train_num1": train_num}],
                                    oa_sequence=1)
        return res[0]['COUNT(1)']
    
    def verify_str(self, train_str):
        """Verify the existence of a train.
           You should provide the train_str of this item.
        """
        res = self.verify_existence([{"train_str": train_str}])
        return res[0]['COUNT(1)']

    def verify_single(self, train_class, train_num0):
        """Verify the existence of a train, using only the train_num0 value.
           Parameters are all required.
        """
        res = self.verify_existence([{"train_class": train_class,
                                     "train_num0": train_num0}])
        return res[0]['COUNT(1)']

    def verify_2nums(self, train_str):
        """
        To know if the train_num1 has been updated.
        If the 2 train_num differ, the function will return true.
        :param train_str:
        :return: bool
        """
        this_train = self.search("train_str", train_str)
        if this_train[0]["train_num0"] == this_train[0]["train_num1"]:
            return True
        else:
            return False

# Edited Dec/14/2018: Change Meaningless default value to NONE #
    def delete(self, key=None, value=None):
        """Delete a train.
           Parameters are not essential, causing all data deleted.
           If provided, only designed item will be deleted.
        """
        if key is None:
            self.delete_data([])
        else:
            self.delete_data([{key: value}])

    def search(self, key=None, value=None):
        """Search for train(s).
           Parameters are not essential, and all trains will be returned.
           If provided, the item they marked will be returned.
        """
        if key is None:
            res = self.query_data([])
        else:
            res = self.query_data([{key: value}])
        
        return len(res), res

    def search_list(self, start, end, train_class):
        """Search for trains with train_num in a particular range.
           The start & end parameter must be integers mark the button and top of range.
           The train_class must be a character.
           Only the list of train_strs and amount will be returned.
        """
        res = self.query_data([{"train_num0": {"judge": "between", "start": start, "end": end},
                                "train_class": train_class,
                                "status": True}],
                              ['train_str'])

        return len(res), res

    def search_single(self, train_class, train_num, status=True):
        """Search for a train with particular train_num0.
           The train_class must be a character and train_num must be a integer.
           Amount of the train and list of results will be returned.
        """
        res = self.query_data([{"train_num0": train_num,
                               "train_class": train_class,
                                "status": status}])

        return len(res), res

    def search_dual(self, train_class, train_num, status=True):
        """Search for a train having train_num0 or train_num1 ???????
           The train_class must be a character and train_num must be a integer.
           Amount of the train and list of results will be returned.
        """
        res = self.query_data([{"train_num0": train_num, "train_num1": train_num},
                              {"train_class": train_class},
                              {"status": status}],
                              oa_sequence=1)

        return len(res), res


def initialize():
    obj = Table()
    obj.create()


if __name__ == "__main__":
    initialize()
