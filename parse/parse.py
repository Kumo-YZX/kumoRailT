# Module Name: Parse #
# Function: Parse the sentence passed by front server & return reply. #
# Author: Kumo Lam (https://github.com/Kumo-YZX) #
# Last Edit: Mar/16/2019 #


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('log', '../dbmaria/dblog/log.py')
load_module('user', '../dbmaria/dblog/user.py')
import hlsearch, chnword


class ParseMsg(object):

    def __init__(self, user, word):
        print('parse/parse.py: Info: Message from {}, {}'.format(user, word))
        self.word = word
        self.user = user
        self.query_type = 0
        self.train_front = ''
        self.reply = ''

    def judge_train_front(self):
        """To determine whether the query word is a single train_number(e.g 'G1001').
           If that, All message of this train will be returned.
           No need to provide parameter, the judgement is based on the self.word variable.
           The return value is the judgement, with 0 marks that word is not single.
           And 1 marks the local train condition, with 2 means other trains.
           And self.query_type will also be set in some conditions.
        """
        # Initialize the flag
        flag = 0
        # Using transfromation to judge whether the first 4 bits of the query word can #
        # mark a local train. if Not, set flag to 0.
        try:
            # The length must be more than 4.
            if len(self.word) >= 4:
                int(self.word[0:4])
                self.train_front = self.word[0:4]
                # The query word have only 4 bits, it is a query-all word.
                if len(self.word) == 4:
                    self.query_type = 12
                # The query word have more than 4 bits of number, it is a late-query word.
                # 10-6=4 marks the First byte of the station name of the late-query word.
                else:
                    self.query_type = 10
                return 1
        # Transformation failed.
        except ValueError:
            flag = 0

        # Check if the query word contains a non-local train_number.
        # If so, return value will be 2.
        try:
            # The second bit of 
            if '0' <= self.word[1] <= '9':
                # The first bit must be a train_class.
                if self.word[0].upper() in ['Z', 'T', 'K', 'G', 'D', 'C', 'Y', 'S', 'P']:
                    # OK, the word head contains a non-local train_number.
                    self.query_type = 6
                    # Find out if the query word has a station name on the end.
                    # self.query_type-6 marks the First byte of the station name.
                    # Range: 8-6=2 ~ 11-6=5
                    for location in range(1, len(self.word)):
                        # If the query word is query-all word, if will match nothing.
                        if self.word[location] < '0' or self.word[location] > '9':
                            self.query_type = self.query_type + location
                            break
                    if self.query_type > 10:
                        self.query_type = 10
                    return 2
        # Failed to transform.
        except TypeError:
            flag = 0

        return flag

    def judge_type(self):
        """Find out the type of the query word.
           Parameter is not contained.
        """
        # Illegal word.
        if len(self.word) < 2:
            self.query_type = 0
            return 0
        # If the query word is query-all or late-query model, return 1 directly.
        if self.judge_train_front():
            return 1

        # Or... the first 2 bits of the query word must be a type_key.
        type_key = self.word[0:2].upper()
        # Query for the sequence.
        if type_key == 'JL':
            self.query_type = 14
        # Query for the depot of a EMU with its number.
        elif type_key == 'PS':
            self.query_type = 13
        # Query for the arrivals of a train.
        elif type_key == 'SK':
            self.query_type = 18
        # Query for the telecode and staInfo of a station.
        elif type_key == 'DB':
            self.query_type = 15
        # Query for all, including sequence & arrival information.
        # elif type_key == 'AL':
        #     self.query_type = 1
        # Add a train to late-monitor.
        elif type_key == 'TJ':
            self.query_type = 19
        # To view all the arrivals in late-monitor.
        elif type_key == 'JK':
            self.query_type = 16
        # View latest Actual Arrival data of a train.
        elif type_key == 'WA':
            self.query_type = 20
        # View Actual Arrival of specified station.
        elif type_key == 'WZ':
            self.query_type = 21
        # Match nothing.
        else:
            self.query_type = 0
        return 0

    def form_reply(self):
        """Format a reply based on provided query word.
           Query-type will be checked by judge_type and judge_train_front function.
           To get the reply word, please use get_reply() method.
        """
        self.judge_type()
        high_level_search = hlsearch.Hls()
        # To catch the train_class for some train_number-included queries.
        if self.query_type in [14, 18, 1]:
            if '0' <= self.word[2] <= '9':
                train_class = 'A'
                train_num = self.word[2:]
            else:
                train_class = self.word[2]
                train_num = self.word[3:]
        elif self.query_type in [12, 6]:
            if '0' <= self.word[0] <= '9':
                train_class = 'A'
                train_num = self.word
            else:
                train_class = self.word[0]
                train_num = self.word[1:]
            if train_class.upper() not in ['G', 'D', 'C']:
                self.query_type = 18

        # Format replies.
        if self.query_type == 14:
            self.reply = high_level_search.seqs(train_num, train_class)
        elif self.query_type == 18:
            self.reply = high_level_search.arrs(train_num, train_class)
        elif self.query_type == 15:
            self.reply = high_level_search.dbs(self.word[2:])
        elif self.query_type == 1:
            self.reply = high_level_search.seqs(train_num, train_class) +\
                   '\n' + high_level_search.arrs(train_num, train_class)
        # Seq and Arr.
        elif self.query_type == 12 or self.query_type == 6:
            self.reply = high_level_search.seqs(train_num, train_class) +\
                   '\n' + high_level_search.arrs(train_num, train_class)
        elif self.query_type == 13:
            self.reply = high_level_search.pss(int(self.word[2:6]))
        elif self.query_type == 19:
            self.reply = chnword.addtoLateMonitorNotReady.decode('hex')
        elif self.query_type == 16:
            self.reply = high_level_search.jks()
        elif self.query_type == 20:
            self.reply = high_level_search.was(self.word[2:7])
        elif self.query_type == 21:
            self.reply = chnword.searchLateHistoryNotReady.decode('hex')
        elif 7 <= self.query_type <= 11:
            self.reply = high_level_search.wzs(self.word[0:self.query_type-6],
                                               self.word[self.query_type-6:])
        else:
            self.reply = chnword.conditionNotExist.decode('hex')

    def get_reply(self):
        """
        Get the reply word.
        :return: string
        """
        return self.reply

    def log_reply(self):
        """
        Log the chat message and reply.
        Make sure that they are ready.
        :return:
        """
        import log, user
        import datetime
        time_mark = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        user_name_here = self.user[0:27]
        user_table = user.Table()
        if not user_table.verify(user_name_here):
            user_table.insert(user_name_here, comment=time_mark+'added')
            print("parse/parse.py: Info: New user: {} added".format(user_name_here))
        log_table = log.Table()
        log_table.insert(user_name_here,
                         self.word[0:8000].encode('hex'),
                         self.reply[0:8000].encode('hex'),
                         time_mark)
        print("parse/parse.py: Info: New log added with mark: {}".format(time_mark))


def test(query_word):
    parse_object = ParseMsg('testUser', query_word)
    parse_object.form_reply()
    parse_object.log_reply()
    return parse_object.get_reply()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(test(sys.argv[1]))
    else:
        print(test('0'))
