#----------------------------------------------------------------#
# Module Name: Parse #
# Function: Parse the sentence passed by front server & return reply. #
# Author: Kumo #
# Last Edit: Dec/24/2018 #
#----------------------------------------------------------------#

def getTime():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d %H%M%S")

class parseMsg(object):

    def __init__(self, user, word):
        print 'msg: {}, {}'.format(user, word)
        self.word = word
        self.user = user

    def judgeTrainFront(self):
        flag = 0
        try:
            int(self.word[0:4])
            self.trainFront = self.word[0:4]
            if len(self.word) == 4:
                self.queryType = 14
            else:
                self.queryType = 9
            return 1
        except ValueError:
            flag = 0

        try:
            if self.word[1] >= '0' and self.word[1] <= '9':
                if self.word[0].upper() in ['Z', 'T', 'K', 'G', 'D', 'C', 'Y', 'S', 'P']:
                    self.queryType = 6
                    for location in range(1, 4):
                        if self.word[location] >= '0' and self.word[location] <= '9':
                            self.queryType = self.queryType + 1
                        else:
                            break
                    return 2
        except TypeError:
            flag = 0

        return flag

    def judgeType(self):
        if self.judgeTrainFront():
            return 1

        typeKey = self.word[0:2].upper()
        if typeKey == 'JL':
            self.queryType = 14
        elif typeKey == 'PS':
            self.queryType = 13
        elif typeKey == 'SK':
            self.queryType = 18
        elif typeKey == 'DB':
            self.queryType = 15
        elif typeKey == 'AL':
            self.queryType = 1
        elif typeKey == 'TJ':
            self.queryType = 19
        elif typeKey == 'JK':
            self.queryType = 16
        else:
            self.queryType = 0
        return 0

def reply(user, word):
    return 'reply test, user:{}, word:{}, time:{}'.format(str(user), str(word), getTime())