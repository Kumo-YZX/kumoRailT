# Module Name: Server.py #
# Function: The main server process, handle requests and send replies. #
# Author: Kumo Lam (https://github.com/Kumo-YZX) #
# Last Edit: Mar/14/2019 #

import tornado.ioloop
import tornado.web
import config
from encrypt.WXBizMsgCrypt import WXBizMsgCrypt
from wx import reply2, receive


class WxHandler(tornado.web.RequestHandler):
    def get(self):
        """Handle the GET request.
           GET handler is used for the verification of WX server.
        """
        print 'server.py: Info: WxHandler: GET request from {}'.format(self.request.remote_ip)
        # Catch structures from request object.
        print 'Timestamp:[{}]'.format(self.get_query_argument('timestamp'))
        print 'Signature:[{}]'.format(self.get_query_argument('signature'))
        print 'Echostr:[{}]'.format(self.get_query_argument('echostr'))

        try:
            para_list = [config.token,
                         self.get_query_argument('timestamp'),
                         self.get_query_argument('nonce')]
            sign = self.get_query_argument('signature')
            echo = self.get_query_argument('echostr')
            para_list.sort()

            # Calculate hash to verify the signature.
            import hashlib
            sha1 = hashlib.sha1()
            map(sha1.update, para_list)
            hash_code = sha1.hexdigest()
            print 'server.py: hash_code, signature:' + hash_code, sign
            # Succeed to verify.
            if hash_code == sign:
                self.write(echo)
            # Failed to verify.
            else:
                self.write('server: Error: verify failed')
        except KeyError:
            self.write('server: Error: some query parameter missing')

    def post(self):
        """Handle the POST request.
           POST handler is used to format replies.
        """
        print 'server.py: Info: WxHandler: POST request from {}'.format(self.request.remote_ip)
        token = config.token
        encoding_key = config.encodingkey
        app_id = config.appid
        decrypt_obj = WXBizMsgCrypt(token, encoding_key, app_id)
        try:
            # Catch parameters from request object.
            stamp = self.get_query_arguments("timestamp")[0]
            nonce = self.get_query_arguments("nonce")[0]
            msg_sign = self.get_query_arguments("msg_signature")[0]

            # Decrypt the message.
            dec_status, wx_data = decrypt_obj.DecryptMsg(self.request.body, msg_sign, stamp, nonce)
            if dec_status:
                print 'server.py: Error: decrypt fail'
                self.write('server: Error: Decrypt fail')
            else:
                print 'server.py: Info: wx_data:', wx_data
                rec_data = receive.parse_xml(wx_data)
                from parse import parse, chnword
                if isinstance(rec_data, receive.Msg) and rec_data.MsgType == 'text':
                    to_user = rec_data.FromUserName
                    from_user = rec_data.ToUserName
                    word = rec_data.Content
                    # The parse object
                    parse_obj = parse.ParseMsg(to_user, word)
                    parse_obj.form_reply()
                    parse_obj.log_reply()
                    content = parse_obj.get_reply()
                else:
                    print 'server.py: Error: wrong format'
                    to_user = rec_data.FromUserName
                    from_user = rec_data.ToUserName
                    content = chnword.imageNotSupported.decode('hex')
                # Encrypt the message for reply.
                encrypt_obj = WXBizMsgCrypt(token, encoding_key, app_id)
                enc_status, reply_data =\
                    encrypt_obj.EncryptMsg(reply2.TextMsg(to_user, from_user, content), nonce, stamp)
                if enc_status:
                    self.write('server: Error: Encrypt fail:' + str(enc_status))
                else:
                    self.write(reply_data)
        except IndexError:
            self.write('server: error: some query parameter missing')


class PageHandler(tornado.web.RequestHandler):
    def get(self):
        """Handler for debugging the server.
        """
        print 'PageHandler: GET request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus": 200, "msg": "ok", "method": "get"})

    def post(self):
        """Handler for debugging the server.
        """
        print 'PageHandler: POST request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus": 200, "msg": "ok", "method": "post"})


def start_app():
    return tornado.web.Application([
        (config.pageHandlerUrl, PageHandler),
        (config.wxHandlerUrl, WxHandler)
    ])


if __name__ == "__main__":
    app = start_app()
    app.listen(address="0.0.0.0", port=config.listenPort)
    tornado.ioloop.IOLoop.current().start()


