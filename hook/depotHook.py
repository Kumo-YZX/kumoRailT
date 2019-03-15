# Module Name: Depot Hook
# Function: Catch EMU depot info online.
# Author: Kumo Lam (https://github.com/Kumo-YZX)
# Date: Mar/15/2019
#


def load_module(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))


load_module('config', '../config.py')
load_module('chnword', '../parse/chnword.py')

from bs4 import BeautifulSoup
import urllib2


class EMUinfo(BeautifulSoup):

    def __init__(self, number):
        import config
        res = ""
        status = 1
        request_url = config.emudepot_url.format(number)
        request = urllib2.Request(request_url,
                                  headers=config.header)
        try:
            res = urllib2.urlopen(request, timeout=5).read()
            status = 1
        except Exception as error:
            print("hook/depotHook.py: Error: Request error occurs")
            print(error)
            status = 0
        BeautifulSoup.__init__(self, res, features="html.parser")

    def get_status(self):
        return self.status

    def print_info(self):
        td_list = self.find_all('td')
        print("Results: ")
        print((len(td_list) - 8)/6)

        for td_index in range(3, len(td_list)-4):
            print(td_list[td_index].get_text())
            print '- '*36

    def form_reply(self):
        import chnword
        td_list = self.find_all('td')
        item_count = (len(td_list) - 8)/6
        if item_count and len(td_list[4].get_text()) > 4:
            reply = chnword.depotResultAmount.decode('hex') +\
                    str(item_count) +\
                    '\n'
            for item_index in range(item_count):
                reply = reply +\
                        chnword.depotEMUType.decode('hex') +\
                        td_list[item_index*8+4].get_text().encode('utf8') +\
                        '\n' +\
                        chnword.depotNumber.decode('hex') + \
                        td_list[item_index*8+5].get_text().encode('utf8') +\
                        '\n' +\
                        chnword.depotBureau.decode('hex') +\
                        td_list[item_index*8+6].get_text().encode('utf8') +\
                        '\n' +\
                        chnword.depotDepot.decode('hex') +\
                        td_list[item_index*8+7].get_text().encode('utf8') +\
                        '\n' +\
                        chnword.depotManufacturer.decode('hex') +\
                        td_list[item_index*8+8].get_text().encode('utf8') +\
                        '\n' +\
                        chnword.depotComment.decode('hex') +\
                        td_list[item_index*8+9].get_text().encode('utf8') +\
                        '\n- - - - - -\n'
        else:
            reply = chnword.depotNoData.decode('hex')

        return reply


def test():
    my_obj = EMUinfo(1001)
    if my_obj.get_status():
        print("hook/depotHook.py: Info: Load successfully")
    my_obj.print_info()
    print my_obj.form_reply()


if __name__ == "__main__":
    test()

