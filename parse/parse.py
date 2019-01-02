#----------------------------------------------------------------#
# Module Name: Parse #
# Function: Parse the sentence passed by front server & return reply. #
# Author: Kumo Lam(github.com/Kumo-YZX) #
# Last Edit: Jan/02/2019 #
#----------------------------------------------------------------#

import hlsearch, chnword

class parseMsg(object):

    def __init__(self, user, word):
        print 'parse/parse.py: Info: Message from {}, {}'.format(user, word)
        self.word = word
        self.user = user

    def judgeTrainFront(self):
        """To determine whether the query word is a single trainNumber(e.g 'G1001').
           If that, All message of this train will be returned.
           No need to provide parameter, the judgement is based on the self.word variable.
           The return value is the judgement, with 0 marks that word is not single.
           And 1 marks the local train condition, with 2 means other trains.
           And self.queryType will also be set in some conditions.
        """
        # Initialize the flag
        flag = 0
        # Using transfromation to judge whether the first 4 bits of the query word can #
        # mark a local train. if Not, set flag to 0.
        try:
            # The length must be more than 4.
            if len(self.word) >= 4:
                int(self.word[0:4])
                self.trainFront = self.word[0:4]
                # The query word have only 4 bits, it is a query-all word.
                if len(self.word) == 4:
                    self.queryType = 12
                # The query word have more than 4 bits of number, it is a late-query word.
                else:
                    self.queryType = 11
                return 1
        # Transformation failed.
        except ValueError:
            flag = 0

        # Check if the query word contains a non-local trainNumber.
        # If so, return value will be 2.
        try:
            # The second bit of 
            if self.word[1] >= '0' and self.word[1] <= '9':
                # The first bit must be a trainClass.
                if self.word[0].upper() in ['Z', 'T', 'K', 'G', 'D', 'C', 'Y', 'S', 'P']:
                    # OK, the word head contains a non-local trainNumber.
                    self.queryType = 6
                    # Find out if the query word has a station name on the end.
                    for location in range(1, len(self.word)):
                        if self.word[location] < '0' or self.word[location] > '9':
                            self.queryType = self.queryType + location
                            break
                    if self.queryType > 10:
                        self.queryType = 10
                    return 2
        # Failed to transform.
        except TypeError:
            flag = 0

        return flag

    def judgeType(self):
        """Find out the type of the query word.
           Parameter is not contained.
        """
        # Illegal word.
        if len(self.word) < 2:
            self.queryType = 0
            return 0
        # If the query word is query-all or late-query model, return 1 directly.
        if self.judgeTrainFront():
            return 1

        # Or... the first 2 bits of the query word must be a typeKey.
        typeKey = self.word[0:2].upper()
        # Query for the sequence.
        if typeKey == 'JL':
            self.queryType = 14
        # Query for the depot of a EMU with its number.
        elif typeKey == 'PS':
            self.queryType = 13
        # Query for the arrivals of a train.
        elif typeKey == 'SK':
            self.queryType = 18
        # Query for the telecode and staInfo of a station.
        elif typeKey == 'DB':
            self.queryType = 15
        # Query for all, including sequence & arrival infomations.
        elif typeKey == 'AL':
            self.queryType = 1
        # Add a train to late-monitor.
        elif typeKey == 'TJ':
            self.queryType = 19
        # To view all the arrivals in late-monitor.
        elif typeKey == 'JK':
            self.queryType = 16
        # Match nothing.
        else:
            self.queryType = 0
        return 0

    def replyWord(self):
        """Format a reply based on provided query word.
           Query-type will be checked by judgeType and judgeTrainFront function.
           Return value will be in chn format and can be replied to the entype process.
        """
        self.judgeType()
        highLevelSearch = hlsearch.hls()
        # To catch the trainClass for some trainNumber-included queries.
        if self.queryType in [14, 18, 1]:
            if self.word[2] >= '0' and self.word[2] <= '9':
                trainClass = 'A'
                trainNum = self.word[2:]
            else:
                trainClass = self.word[2]
                trainNum = self.word[3:]
        elif self.queryType in [12, 6]:
            if self.word[0] >= '0'and self.word[0] <= '9':
                trainClass = 'A'
                trainNum = self.word
            else:
                trainClass = self.word[0]
                trainNum = self.word[1:]

        # Format replies.
        if self.queryType == 14:
            return highLevelSearch.seqs(trainNum, trainClass)
        elif self.queryType == 18:
            return highLevelSearch.arrs(trainNum, trainClass)
        elif self.queryType ==  15:
            return highLevelSearch.dbs(self.word[2:])
        elif self.queryType == 1:
            return highLevelSearch.seqs(trainNum, trainClass) +\
                   '\n' + highLevelSearch.arrs(trainNum, trainClass)
        elif self.queryType == 12 or self.queryType == 6:
            return highLevelSearch.seqs(trainNum, trainClass) +\
                   '\n' + highLevelSearch.arrs(trainNum, trainClass)
        elif self.queryType == 13:
            return chnword.depotQueryNotReady.decode('hex')
        elif self.queryType == 19:
            return chnword.addtoLateMonitorNotReady.decode('hex')
        elif self.queryType == 16:
            return chnword.viewLateMonitorNotReady.decode('hex')
        elif self.queryType >= 7 and self.queryType <= 11:
            return chnword.searchLateHistoryNotReady.decode('hex')
        else:
            return chnword.conditionNotExist.decode('hex')

def test(queryWord):
    parseObject = parseMsg('testUser', queryWord)
    return parseObject.replyWord()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print test(sys.argv[1])
    else:
        print test('0')