#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2

class SendMessage(object):
    def __init__(self, content):
        self._api = "http://logmonitor.chinacache.net:8888/mobile/"
        self._mobiles = "13910840138;13488770992;13910001730;13801289719"
        self._content = content
    
    def sendmessage(self):
        res = urllib2.urlopen(self._api, urllib.urlencode({"content": self._content.encode("utf-8"),
                                                           "phonenum": self._mobiles})).read()
        return res.read()