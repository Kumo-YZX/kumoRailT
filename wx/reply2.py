#----written by tencent WeChat group----#
import time

def TextMsg(toUser, fromUser, content):
    return '<xml><ToUserName><![CDATA['+ toUser +']]></ToUserName><FromUserName><![CDATA['+ fromUser +']]></FromUserName><CreateTime>'+ str(int(time.time())) +'</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA['+ content +']]></Content></xml>'