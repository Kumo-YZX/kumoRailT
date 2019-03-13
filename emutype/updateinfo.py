# Module Name: updateinfo
# Combine seq and emu-info data.
# Author: Kumo Lam(https://github.com/Kumo-YZX)
# Date: Mar/14/2019
# Note: Format problem and other bugs will be fixed later.
#

import json


def update():
    with open('seq.json', 'r') as f1:
        seqList =json.load(f1)
    with open('emuinfo.json', 'r') as f2:
        infoList =json.load(f2)
    for every in seqList:
        for everyTrain in every['seqTrains']:
            for everyInfo in infoList: #search for trains
                if everyInfo['trainNo'] ==everyTrain:
                    everyInfo['sequence'] =every['seqNum']
                    break
        print every['seqNum'] 
    with open('seq_data.json', 'w') as f3:
        json.dump(infoList, f3)


if __name__=="__main__":
    update()
