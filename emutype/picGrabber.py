#
# Module Name: Pic Getter.
# Function: Grab pictures of source program on the screen.
# Author: Kumo Lam(https://github.com/Kumo-YZX)
# Date: Mar/13/2019
# Warning: Please check the checklist first!
#


import win32api
import win32con
import time
import json

def query(str):
    win32api.SetCursorPos((1001,604))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0,0,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0,0,0,0)
    time.sleep(0.1)

    win32api.SetCursorPos((38,211))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0,0,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0,0,0,0)
    time.sleep(0.1)

    pressDel(4)
    time.sleep(0.1)

    keyInput(str)
    time.sleep(0.1)

    win32api.SetCursorPos((38,240))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0,0,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0,0,0,0)
    time.sleep(0.3)


def keyInput(str):
    for every in str:
        win32api.keybd_event(ord(every), 0,0,0)
        win32api.keybd_event(ord(every), 0,win32con.KEYEVENTF_KEYUP,0)
        time.sleep(0.1)


def pressDel(bit):
    for i in range(bit):
        win32api.keybd_event(8, 0,0,0)
        win32api.keybd_event(8, 0,win32con.KEYEVENTF_KEYUP,0)
        win32api.keybd_event(46, 0,0,0)
        win32api.keybd_event(46, 0,win32con.KEYEVENTF_KEYUP,0)
        time.sleep(0.1)


def savePic(fileName):
    from PIL import ImageGrab
    pic = ImageGrab.grab((0,0,1028,626)).convert('1',None)
    pic.save('D:\\emupic\\'+fileName+'.bmp', 'bmp')


def getPic(trainName):
    from PIL import ImageGrab
    pic = ImageGrab.grab((0,0,1028,626)).convert('1',None)
    return pic


if __name__ == '__main__':
    startSeq = int(raw_input('start:'))
    endSeq = int(raw_input('end:'))
    time.sleep(3)
    with open('out.json') as fi:
        traList = json.load(fi)
    for i in range(startSeq,endSeq):
        trainNo = traList[i]
        # tarinNo = 'G' + str(tra)
        query(trainNo)
        savePic(trainNo)
        print 'info '+str(i)+':'+'save '+trainNo
        print '-'*16
