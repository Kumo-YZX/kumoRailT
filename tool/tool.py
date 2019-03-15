# File Name: tool.py
# Some useful tools.
# Author: Kumo Lam (https://github.com/Kumo-YZX)
# Date: Mar/15/2019


def str2int(timeStr):
    hourStr, minStr = timeStr.split(':')
    return int(hourStr)*60 + int(minStr)


def int2str(timeInt):
    hourStr = '{:0>2}'.format(timeInt/60)
    minStr = '{:0>2}'.format(timeInt%60)
    return str(hourStr)+':'+str(minStr)


def correctClass(trainClass):
    if trainClass[0] == 'h':
        return '0G'
    elif trainClass[0] == 'e':
        return '0D'
    elif trainClass[0] == 'b':
        return '0C'
    elif trainClass[0] == 'j':
        return 'DJ'
    else:
        return trainClass[0]
