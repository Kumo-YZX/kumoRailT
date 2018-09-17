#---#

#import json

def str2int(timeStr):
    hourStr, minStr = timeStr.split(':')
    return int(hourStr)*60 + int(minStr)