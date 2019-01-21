#--------------------------------------------------------------------------------#
# Module Name: Server.py #
# Function: The main server process, handle requests and send replies. #
# Author: Kumo #
# Last Edit: Jan/07/2019 #
#--------------------------------------------------------------------------------#

import tornado.ioloop
import tornado.web
import config
from encrypt.WXBizMsgCrypt import WXBizMsgCrypt
from wx import reply2, receive

import ptvsd

ptvsdDebug = config.loadPtvsd

# Load the debug progress
def loadDebug():
    # Allow other computers to attach to ptvsd at this IP address and port.
    ptvsd.enable_attach(address=(config.ptvsdDebugAddress, config.ptvsdDebugPort), redirect_output=True)

    # Pause the program until a remote debugger is attached
    ptvsd.wait_for_attach()

class WxHandler(tornado.web.RequestHandler):
    def get(self):
        """Handle the GET request.
           GET handler is used for the verification of WX server.
        """
        import json
        print 'server.py: Info: WxHandler: GET request from {}'.format(self.request.remote_ip)
        # Catch structures from request object.
        print 'Timestamp:[{}]'.format(self.get_query_argument('timestamp'))
        print 'Signature:[{}]'.format(self.get_query_argument('signature'))
        print 'Echostr:[{}]'.format(self.get_query_argument('echostr'))

        try:
            paraList = [config.token, self.get_query_argument('timestamp'), self.get_query_argument('nonce')]
            sign = self.get_query_argument('signature')
            echo = self.get_query_argument('echostr')
            paraList.sort()

            # Conculate hash to verify the signature.
            import hashlib
            sha1 = hashlib.sha1()
            map(sha1.update, paraList)
            hashCode = sha1.hexdigest()
            print 'hashCode, signature:' + hashCode, sign
            # Succeed to verify.
            if hashCode == sign:
                self.write(echo)
            # Failed to verify.
            else:
                self.write('server: Error: verify failed')
        except KeyError:
            self.write('server: Error: some query parameter missing')

    def post(self):
        """Handle the POST request.
           POST handler is used for formating replies.
        """
        print 'server.py: Info: WxHandler: POST request from {}'.format(self.request.remote_ip)
        token = config.token
        encodingKey = config.encodingkey
        appid = config.appid
        encodingkey = config.encodingkey
        decryptObj = WXBizMsgCrypt(token, encodingKey, appid)
        try:
            # Catch parameters from request object.
            stamp = self.get_query_arguments("timestamp")[0]
            nonce = self.get_query_arguments("nonce")[0]
            msgSign = self.get_query_arguments("msg_signature")[0]

            # Decrypt the message.
            decStatus, wxData = decryptObj.DecryptMsg(self.request.body, msgSign, stamp, nonce)
            if decStatus:
                print 'server.py: Error: decrypt fail'
                self.write('server: Error: Decrypt fail')
            else:
                print 'server.py: Info: wxData:', wxData
                recData = receive.parse_xml(wxData)
                from parse import parse, chnword
                if isinstance(recData, receive.Msg) and recData.MsgType == 'text':
                    toUser = recData.FromUserName
                    fromUser = recData.ToUserName
                    word = recData.Content
                    # The parse object
                    parseObj = parse.parseMsg(toUser, word)
                    content = parseObj.replyWord()
                else:
                    print 'server.py: Error: wrong format'
                    toUser = recData.FromUserName
                    fromUser = recData.ToUserName
                    content = chnword.imageNotSupported.decode('hex')
                # Encrypt the message for reply.
                encryptObj = WXBizMsgCrypt(token, encodingkey, appid)
                encStatus, replyData = encryptObj.EncryptMsg(reply2.TextMsg(toUser, fromUser, content), nonce, stamp)
                if encStatus:
                    self.write('server: Error: Encrypt fail:' + str(encStatus))
                else:
                    self.write(replyData)
        except IndexError:
            self.write('server: error: some query parameter missing')

class PageHandler(tornado.web.RequestHandler):
    def get(self):
        """Handler for debugging the server.
        """
        print 'PageHandler: GET request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"ok", "method":"get"})

    def post(self):
        """Handler for debugging the server.
        """
        print 'PageHandler: POST request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"ok", "method":"post"})

def startApp():
    return tornado.web.Application([
        (config.pageHandlerUrl, PageHandler),
        (config.wxHandlerUrl, WxHandler)
    ])

if __name__ == "__main__":
    if ptvsdDebug:
        loadDebug()
    app = startApp()
    app.listen(address = "0.0.0.0", port = config.listenPort)
    tornado.ioloop.IOLoop.current().start()


