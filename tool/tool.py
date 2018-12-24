#---#

#import json

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

def processEmuno(msg):
    import httplib
    import re
    
    connUrl = httplib.HTTPConnection('emu.passearch.info')
    siteUrl = '/emu.php?type=number&keyword=' + msg
    connUrl.request('GET', siteUrl)
    resMsg = connUrl.getresponse()
    recText = resMsg.read()
    recForm = re.findall(r'<table border="0" align="center">(.*?)</table>', recText)
    if len(recForm) == 0:
        reText = u'\u6ca1\u6709\u627e\u5230\u52a8\u8f66\u7ec4\u914d\u5c5e\u4fe1\u606f'
    else:
        recCount = len(re.findall(r'<tr>', recForm[0])) - 1
        recTd = re.findall(r'<td>(.*?)</td>', recForm[0])
        emuModel = re.findall(r'<a href=emu.php\?type=model&keyword=.*?>(.*?)</a>', recForm[0])
        emuBureau = re.findall(r'<a href=emu.php\?type=bureau&keyword=.*?>(.*?)</a>', recForm[0])
        emuDepartment = re.findall(r'<a href=emu.php\?type=department&keyword=.*?>(.*?)</a>', recForm[0])
        reText = u'\u67e5\u8be2\u5230' + str(recCount) + u'\u6761\uff1a'
        for every in range(recCount):
            emuManufacturer = recTd[7*every+4]
            emuRemark = recTd[7*every+5]
            reText = reText + u'\n\u7b2c' + str(every+1) + u'\u6761\uff1a\n\u8f66\u578b\uff1a' + emuModel[every] + u'\n\u8def\u5c40\uff1a' + emuBureau[every].decode('utf8') + u'\n\u52a8\u8f66\u6240\uff1a' + emuDepartment[every].decode('utf8') + u'\n\u5382\u5bb6\uff1a' + emuManufacturer.decode('utf8') + u'\n\u5907\u6ce8\uff1a' + emuRemark.decode('utf8')
    # print reText
    return reText