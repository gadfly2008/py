#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json

def get_channels(logger, customers):
    res = {}
    for c in customers:
        api = "http://rcmsapi.chinacache.com:36000/customer/%s/channels" %(c,)
        opener = urllib2.urlopen(api)
        for recorder in json.loads(opener.read()):
            res[recorder[u"code"]] = c
    logger.debug(res)
    return res
    