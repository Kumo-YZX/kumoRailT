#----------------------------------------------------------------#
# Module Name: Parse #
# Function: Parse the sentence passed by front server & return reply. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Jan/02/2019 #
#----------------------------------------------------------------#

import hlsearch, chnword


class ParseMsg(object):

    def __init__(self, user, word):
        print('parse/parse.py: Info: Message from {}, {}'.format(user, word))
        self.word = word
        self.user = user
        self.query_type = 0
        self.train_front = ''

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
                else:
                    self.query_type = 11
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
                    for location in range(1, len(self.word)):
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
        elif type_key == 'AL':
            self.query_type = 1
        # Add a train to late-monitor.
        elif type_key == 'TJ':
            self.query_type = 19
        # To view all the arrivals in late-monitor.
        elif type_key == 'JK':
            self.query_type = 16
        # Match nothing.
        else:
            self.query_type = 0
        return 0

    def reply_word(self):
        """Format a reply based on provided query word.
           Query-type will be checked by judge_type and judge_train_front function.
           Return value will be in chn format and can be replied to the entype process.
        """
        self.judge_type()
        high_level_search = hlsearch.hls()
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

        # Format replies.
        if self.query_type == 14:
            return high_level_search.seqs(train_num, train_class)
        elif self.query_type == 18:
            return high_level_search.arrs(train_num, train_class)
        elif self.query_type ==  15:
            return high_level_search.dbs(self.word[2:])
        elif self.query_type == 1:
            return high_level_search.seqs(train_num, train_class) +\
                   '\n' + high_level_search.arrs(train_num, train_class)
        elif self.query_type == 12 or self.query_type == 6:
            return high_level_search.seqs(train_num, train_class) +\
                   '\n' + high_level_search.arrs(train_num, train_class)
        elif self.query_type == 13:
            return chnword.depotQueryNotReady.decode('hex')
        elif self.query_type == 19:
            return chnword.addtoLateMonitorNotReady.decode('hex')
        elif self.query_type == 16:
            return chnword.viewLateMonitorNotReady.decode('hex')
        elif 7 <= self.query_type <= 11:
            return chnword.searchLateHistoryNotReady.decode('hex')
        else:
            return chnword.conditionNotExist.decode('hex')


def test(query_word):
    parse_object = ParseMsg('testUser', query_word)
    return parse_object.reply_word()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(test(sys.argv[1]))
    else:
        print(test('0'))
