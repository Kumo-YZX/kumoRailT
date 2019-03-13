#
# Module Name: Process Picture
# Function: Catch dep. & arr. station & depot & type info of a train.
# Author: Kumo Lam(https://github.com/Kumo-YZX)
# Date: Mar/13/2019
#
#

from PIL import Image
import numpy
import time
import json

staPic = []

wordList = ['xin', 'CR', 'H', '1', '2', 
                '3', '5', '380', '400', 'A', 'B', 
                'C', 'D', 'E', 'G', 'F', 'L', 
                'A-A', 'tong', 'xing', 'chonglian', 'F-A']

chnList = [u'\u65b0', 'CR', 'H', '1', '2', 
                '3', '5', '380', '400', 'A', 'B', 
                'C', 'D', 'E', 'G', 'F', 'L', 
                'A-A', u'\u7edf', u'\u578b', u'\u91cd\u8054', 'F-A']

wordPic = []

depPic = []


def judgeSimilar(pic1, pic2):
    similar = 0
    for line in range(pic2.shape[0]):
        for column in range(pic2.shape[1]):
            if pic1[line, column] == pic2[line, column]:
                similar = similar + 1
    
    return similar, pic2.shape[0]*pic2.shape[1]


# load departure words(in pic)
def depPicInit():
    global depPic
    with open('amount.json','r') as fi:
        amount = json.load(fi)
    for depValue in range(1,amount['dep']+1):
        depPic.append(numpy.loadtxt('deps\\'+str(depValue)+'.txt', dtype=bool))
    return 1


def anaDep(array):
    global depPic
    existVal = judgeExistance(array[60:158, 81:96])
    if float(existVal[0])/existVal[1] < 0.97:
        depArea = [array[60:158, 81:96], array[60:158, 127:142]]
    else:
        depArea = [array[60:158, 103:118]]
    depList = []
    for every in depArea:
        getStatus = 0
        for everyArr in range(len(depPic)):
            simValue = judgeSimilar(every, depPic[everyArr])
            # print 'simValue:' + str(simValue[0]/simValue[1])
            if float(simValue[0])/simValue[1] > 0.96:
                print 'exist dep:' + str(everyArr+1)
                depList.append(everyArr+1)
                getStatus = 1
                break
        if not getStatus:
            depPic.append(every)
            savePic = Image.fromarray(numpy.uint8(every*255),'L')
            depAmount = 'deps\\' + str(len(depPic))
            numpy.savetxt(depAmount+'.txt', every, '%1d')
            savePic.save(depAmount+'.jpeg', 'jpeg')
            depList.append(len(depPic))
            print 'new dep:' + str(len(depPic))
    with open('amount.json','r') as fi:
        amount = json.load(fi)
        amount['dep'] = len(depPic)
    with open('amount.json','w') as fo:
        json.dump(amount, fo)
    return depList


def staPicInit():
    global staPic
    with open('amount.json','r') as fi:
        amount = json.load(fi)
    for staValue in range(1, amount['sta']+1):                #start form 1
        staPic.append(numpy.loadtxt('stas\\'+str(staValue)+'.txt', dtype=bool))
    return 1


def anaSta(array):
    staArea = [array[34:50, 7:69], array[134:150, 7:69]]
    global staPic
    staList = []
    for every in staArea:
        getStatus = 0
        for everyArr in range(len(staPic)):
            simValue = judgeSimilar(every, staPic[everyArr])
            # print 'simValue:' + str(simValue[0]/simValue[1])
            if float(simValue[0])/simValue[1] > 0.96:
                print 'exist sta:' + str(everyArr+1)
                staList.append(everyArr+1)
                getStatus = 1
                break
        if not getStatus:
            staPic.append(every)
            savePic = Image.fromarray(numpy.uint8(every*255),'L')
            staAmount = 'stas\\'+str(len(staPic))
            numpy.savetxt(staAmount+'.txt', every, '%1d')
            savePic.save(staAmount+'.jpeg', 'jpeg')
            staList.append(len(staPic))
            print 'new sta:' + str(len(staPic))
    with open('amount.json','r') as fi:
        amount = json.load(fi)
        amount['sta'] = len(staPic)
    with open('amount.json','w') as fo:
        json.dump(amount, fo)
    return staList
    # print 'done'
    # g15start = getStaPic('G15.bmp', 1)
    # g15pic = Image.fromarray(numpy.uint8(g15start*255),'L')
    # g15pic.show()
    # g16end = getStaPic('G16.bmp', 0)
    # g16pic = Image.fromarray(numpy.uint8(g16end*255),'L')
    # g16pic.show()


def wordPicInit():
    global wordPic
    for words in wordList:
        wordMatrix = numpy.load('words\\'+words+'.npy')
        wordPic.append(wordMatrix)
    return 1


def recoEmutype(array):
    nowPix = [86, 102]
    resList = []
    step = 0
    cycAmount = 0
    while step < 88:
        if step in [0, 1]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            # print bits
            for every in range(2):
                # print every
                simRes, area = judgeSimilar(bits, wordPic[every])
                # print simRes, area
                # print str(simRes) + '-' + str(area) + '-' + str(float(simRes)/area)
                if float(simRes)/area > 0.97:
                    resList.append(every)
                    # print '0'
                    if every:
                        # print '1'
                        if step == 1:
                            step = 3
                        else:
                            step = 2
                        nowPix[0] = nowPix[0] + 16
                        nowPix[1] = nowPix[0] + 24
                    else:
                        # print '2'
                        step = 1
                        nowPix[0] = nowPix[0] + 16
                        nowPix[1] = nowPix[0] + 16
                    break
                else:
                    pass
        elif step in [2, 3]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            for every in [2,8]:
                simRes, area = judgeSimilar(bits, wordPic[every])
                if float(simRes)/area > 0.95:
                    resList.append(every)
                    if every == 2:
                        step = 4
                        nowPix[0] = nowPix[0] + 9
                        nowPix[1] = nowPix[0] + 23
                    else:
                        step = 5
                        nowPix[0] = nowPix[0] + 24   #location of A/B in CR400A/BF
                        nowPix[1] = nowPix[0] + 8
                    break
                else:
                    pass
        elif step in [5]:                                               #CR400 judge A/B
            bits = array[600:616, nowPix[0]:nowPix[1]]
            for every in [9, 10]:
                simRes, area = judgeSimilar(bits, wordPic[every])
                if float(simRes)/area > 0.95:
                    resList.append(every)
                    #resList.append(15)
                    step = 14
                    nowPix[0] = nowPix[0] + 8
                    nowPix[1] = nowPix[0] + 24
                else:
                    pass
        elif step in [4]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            for every in [7, 3, 4, 5, 6]:
                simRes, area = judgeSimilar(bits, wordPic[every])
                if float(simRes)/area > 0.95:
                    resList.append(every)
                    if every == 7:
                        step = 6
                        nowPix[0] = nowPix[0] + 23
                        nowPix[1] = nowPix[0] + 8
                    else:
                        step = 7
                        nowPix[0] = nowPix[0] + 7
                        nowPix[1] = nowPix[0] + 24
                    break
                else:
                    pass
        elif step in [6]:                                               #CRH380 judge A/B/C/D
            bits = array[600:616, nowPix[0]:nowPix[1]]
            for every in [9, 10, 11, 12]:
                simRes, area = judgeSimilar(bits, wordPic[every])
                if float(simRes)/area > 0.95:
                    resList.append(every)
                    step = 8
                    nowPix[0] = nowPix[0] + 8
                    nowPix[1] = nowPix[0] + 16
                    break
                else:
                    pass
        elif step in [7]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            for every in [17, 9, 10, 11, 13, 14, 15]:
                simRes, area = judgeSimilar(bits, wordPic[every])
                if float(simRes)/area > 0.95:
                    resList.append(every)
                    step = 12
                    if every == 17:
                        nowPix[0] = nowPix[0] + 24
                    else:
                        nowPix[0] = nowPix[0] + 8
                    nowPix[1] = nowPix[0] + 16
                    break
                else:
                    pass
        elif step in [8, 10, 11, 12, 22]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            for every in [19, 18, 16, 15]:
                simRes, area = judgeSimilar(bits, wordPic[every])
                if float(simRes)/area > 0.95:
                    resList.append(every)
                    if every == 19:
                        step = 9
                        nowPix[0] = nowPix[0] + 16
                        nowPix[1] = nowPix[0] + 32
                    elif every == 18:
                        step = 10
                        nowPix[0] = nowPix[0] + 16
                        nowPix[1] = nowPix[0] + 16
                    else:
                        step = 11
                        nowPix[0] = nowPix[0] + 8
                        nowPix[1] = nowPix[0] + 16
                    break
                else:
                    pass
        elif step in [9]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            simRes, area = judgeSimilar(bits, wordPic[20])
            if float(simRes)/area > 0.95:
                resList.append(20)
                step = 99
            else:
                step = 98

        elif step in [14]:
            bits = array[600:616, nowPix[0]:nowPix[1]]
            simRes, area = judgeSimilar(bits, wordPic[21])
            if float(simRes)/area > 0.95:
                resList.append(21)
                resList.append(19)
                step = 99
            else:
                resList.append(15)
                #resList.append(19)
                nowPix[0] = nowPix[0] + 8
                nowPix[1] = nowPix[0] + 16
                step = 22
                
        else:
            print 'Error'

        cycAmount = cycAmount + 1
        if cycAmount > 12:
            return 'emu type analysis error'
        # print resList
        # print step
        # time.sleep(2)
    resChn = ''
    for every in resList:
        resChn = resChn + chnList[every]
    print resChn
    return resChn
    # print 'Done'


def getAdjust(array):
    for mov in [0,1,-1,2,-2,3,-3]:
        bits = array[60:126, 38+mov]
        if numpy.sum(bits) < 8:
            print 'adjValue:' + str(mov)
            return mov
    print 'notfound'
    return 0


def judgeExistance(array):
    amount = 0
    for line in range(array.shape[0]):
        for column in range(array.shape[1]):
            amount = amount + array[line, column]
    # print 'JudgeExistanceValue: White:'+str(amount)+' All:'+str(array.shape[0]*array.shape[1])
    return amount, array.shape[0]*array.shape[1]


def anaPic(pic, con):
    if con:
        picRaw = Image.open('bmps\\'+pic+'.bmp')
        picArray = numpy.array(picRaw)
    else:
        picArray = numpy.array(pic)

    # print picArray[0,2]

    for column in range(1,1027):
        for line in range(1,625):
            partArray = picArray[line-1:line+2, column-1:column+2]
            if numpy.sum(partArray) == 8 and picArray[line, column] == 0:
                picArray[line, column] = 1

    adjValue = getAdjust(picArray[0:126, 0:76])
    if adjValue > 0:
        picArray = picArray[0:1028, adjValue:626]
    elif adjValue < 0:
        picArray = numpy.block([numpy.ones((1028,0),int), picArray])
    else:
        pass

    existVal = judgeExistance(picArray[134:150, 7:69])
    if float(existVal[0])/existVal[1] > 0.96:
        res = {'trainNo':pic, 'haveData':0, 'startSta':0, 'endSta':0,
               'vehicleDep':0, 'staffDep':0, 'emuType':'',
               'sequence':'', 'remark':''}
    else:
        staRes = anaSta(picArray)
        depRes = anaDep(picArray)
        res = {'trainNo':pic, 'haveData':1, 'startSta':staRes[0], 'endSta':staRes[1],
               'vehicleDep':depRes[0], 'staffDep':depRes[-1], 'emuType':recoEmutype(picArray),
               'sequence':'', 'remark':''}
    
    return res


def main():
    time.sleep(1)
    # import random
    # from emugetter import query, getPic
    with open('out.json') as fi:
        traList = json.load(fi)
    depPicInit()
    staPicInit()
    wordPicInit()
    resList = []
    start = raw_input()
    end = raw_input()
    for i in range(int(start), int(end)):
        trainNo = traList[i]
        # query(trainNo)
        print trainNo + ' result:'
        resList.append(anaPic(trainNo, 1))
        print '---- ---- ---- ----'
    with open(start+'-'+end+'.json', 'w') as fo:
        json.dump(resList, fo)


def readFromFile():
    with open('result.json') as fi:
        resList = json.load(fi)
    for every in resList:
        print every['trainNo']+'-'+str(every['staffDep'])+'-'+every['emuType']


if __name__ == "__main__":
    main()

