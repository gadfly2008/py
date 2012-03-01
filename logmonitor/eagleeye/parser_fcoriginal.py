#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import json
import urllib2
import urllib

def update_data(data, dt):
    try:
        api = "http://logmonitor.chinacache.net:8888/fc/fcoriginal/add/"
        urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4),
                                               "dt": dt}), 60).read()
    except Exception, e:
        print e

if __name__ == "__main__":
    try:
        data = []
        dt = ""
        for content in open("logs/fclog_static/data.txt").readlines():
            content = content.strip()
            dt = content.split()[0]
            data.append({"fc": content.split()[1], "count": content.split()[2]})
        update_data(data, dt)
    except Exception, e:
        print e