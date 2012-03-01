#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import os
import sys
from datetime import datetime
from pymongo import Connection

def sync_channel(db):
    api = "http://rcmsapi.chinacache.com:36000/channels"
    opener = urllib2.urlopen(api)
    data = []
    for recorder in json.loads(opener.read()):
        try:
            data.append({"customer_id": recorder[u"customerCode"],
                         "name": recorder[u"channelName"].split("://")[1],
                         "channelId": recorder[u"channelCode"]})
        except Exception, e:
            print "%s %s" %(recorder, e)

    db.rcms_channel.remove()
    db.rcms_channel.insert(data)

def sync_customer(db):
    api = "http://rcmsapi.chinacache.com:36000/customers"
    opener = urllib2.urlopen(api)
    data = []
    for recorder in json.loads(opener.read()):
        data.append({"name": recorder[u"name"], "customerId": recorder[u"code"]})

    db.rcms_customer.remove()
    db.rcms_customer.insert(data)

def sync_device(db):
    data = []
    for app in ["NLA","FC"]:
        api = "http://rcmsapi.chinacache.com:36000/app/name/%s/devices" %(app,)
        opener = urllib2.urlopen(api)
        for recorder in json.loads(opener.read()):
            data.append({"name": recorder[u"devName"], "sn": recorder[u"devCode"], "app": app})

    db.rcms_device.remove()
    db.rcms_device.insert(data)

if __name__ == "__main__":
    res = os.popen("ps aux | grep -v grep | grep \'sync_rcms.py\'")
    if len(res.readlines()) > 2:
        print "sync_rcms.py has already run, exit at %s" %(datetime.today(), )
        sys.exit()

    print "App start at %s" %(datetime.now())
    connection = Connection()
    db = connection["eagleeye"]
    sync_customer(db)
    sync_channel(db)
    sync_device(db)
    connection.disconnect()
    print "App end at %s" %(datetime.now())