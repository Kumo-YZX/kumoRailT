# Module Name: Process Sequence
# Catch sequence data from pictures.
# Author: Kumo Lam(https://github.com/Kumo-YZX)
# Date: Mar/14/2019
# Note: Format problem and other bugs will be fixed later.

from PIL import Image
import numpy, time, json


def embedValue(sample, refer):
    diff =0
    if numpy.sum(sample) > 60:
        return 3
    for line in range(sample.shape[0]):
        for column in range(sample.shape[1]):
            if not refer[line, column]:
                if not sample[line, column]:
                    pass
                else:
                    diff = diff +1
            if diff >=2:
                break
        if diff>=2:
            break
    return diff


class seqObj(object):

    def __init__(self,fileName):
        self._wordList =['D','G','C','J','1','2','8','4',
                         '5','6','7','3','9','0','slash']
        self._imageArray =numpy.array(Image.open(fileName))[260:593, 2:1028]
        for column in range(1,1024):
            for line in range(1,331):
                partArray = self._imageArray[line-1:line+2, column-1:column+2]
                if numpy.sum(partArray) == 8 and self._imageArray[line, column] == 0:
                    self._imageArray[line, column] = 1
                if numpy.sum(partArray) ==0:
                    self._imageArray[line-1:line+2, column-1:column+2].fill(1)

        print 'read:' +fileName +':done'
    
    def loadFont(self, path ='seqWords\\'):
        self._fontList =[]
        for every in self._wordList:
            wordMartix =numpy.loadtxt(path +every+'.txt', dtype =bool)
            self._fontList.append(wordMartix)
        print 'load font done'

    def walkOver(self):
        self._trainList =[]
        for column in range(1012):
            for line in range(323):
                sampleBlock =self._imageArray[line:line+10, column:column+7]
                state =0
                nowColumn =column
                trainWord =[]
                while(state<99):
                    
                    if state ==2:
                        flag =0
                        if len(sampleBlock[0]) <6: #end of page, have train
                            self._trainList.append(trainWord)
                            state =99
                            break
                        for word in range(4,15):
                            if embedValue(sampleBlock, self._fontList[word]) <2:
                                flag =1
                                self._imageArray[line:line+10, nowColumn:nowColumn+7].fill(1)
                                nowColumn =nowColumn +7
                                trainWord.append(word)
                                break
                        if not flag:
                            self._trainList.append(trainWord)
                            state =99
                            break
                    elif state ==1:
                        if embedValue(sampleBlock, self._fontList[3]) <2: #J
                            self._imageArray[line:line+10, nowColumn:nowColumn+7].fill(1)
                            nowColumn =nowColumn +7
                            trainWord.append(3)
                        state =2
                    elif state <=0:
                        flag =0
                        if len(sampleBlock[0]) <6: #end of page, no train
                            state =99
                            break
                        for word in [0,1,2,13]: #D G C 0
                            if embedValue(sampleBlock, self._fontList[word]) <2:
                                flag =1
                                self._imageArray[line:line+10, nowColumn:nowColumn+7].fill(1)
                                nowColumn =nowColumn +7
                                if word in [1,2]:# G C
                                    print 'find one Train Num at:' ,line, column
                                    state =2
                                    trainWord.append(word)
                                elif word in [0]:#D
                                    print 'find one Train Num at:' ,line, column
                                    state =1
                                    trainWord.append(word)
                                else:#0
                                    if not state:
                                        trainWord.append(word)
                                    state =state -1
                                break
                        if (not flag) or state< -2:
                            break
                    else:
                        break
                    if state ==99: #useless
                        print 'useless break'
                        break
                    sampleBlock =self._imageArray[line:line+10, nowColumn:nowColumn+7]
        print 'analyse done'
    
    def printTrainList(self):
        allTrainNum =[]
        for every in self._trainList:
            trainNum =''
            i =0
            while i < len(every):
                if every[i] ==14:
                    allTrainNum.append(trainNum)
                    trainNum =trainNum[0: 2*i+1-len(every)]
                else:
                    trainNum =trainNum +self._wordList[every[i]]
                i =i +1
            allTrainNum.append(trainNum)
        print allTrainNum
        return allTrainNum


if __name__=="__main__":
    start =raw_input()
    end =raw_input()
    with open('seq.json', 'r') as fi1:
        res =json.load(fi1)
    with open('emuinfo.json', 'r') as fi:
        trainList =json.load(fi)
    # with open('trainNotExist.json') as fi2:
    #     notExistList = json.load(fi2)
    for i in range(int(start), int(end)):
        print 'No:'+ str(i)
        if not trainList[i]['haveData']:
            print trainList[i]['trainNo'] +\
             'do not have seq data, maybe a IC train'
        else:
            flag =1 #is a new seq(train)?
            for every in res:
                if trainList[i]['trainNo'] in every['seqTrains']:
                    flag =0
                    break
            if flag:
                myseq =seqObj('bmps\\'+ trainList[i]['trainNo']+'.bmp')
                myseq.loadFont()
                myseq.walkOver()
                allTrainList = myseq.printTrainList()
                if len(allTrainList):
                    res.append({'seqNum': len(res), 'seqTrains': allTrainList})
                else:
                    res[0]['seqTrains'].append(trainList[i]['trainNo'])
    with open('seq.json', 'w') as fo:
        json.dump(res, fo)
        print 'output done'
