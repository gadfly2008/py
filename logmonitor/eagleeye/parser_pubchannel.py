#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import urllib2
import json
import os
import sys
import subprocess
from xml.dom import minidom
from datetime import datetime, timedelta

PriotiryDict = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 4, "6": 5, "7": 5, "8": 5, "9": 5}

def get_transfer_channels():
    channels = []
    api = "http://rcmsapi.chinacache.com:36000/channels"
    opener = urllib2.urlopen(api)
    for recorder in json.loads(opener.read()):
        if recorder["state"] == "TRANSFER":
            channels.append(recorder["channelCode"])

    return channels

def get_pubchannels_id():
    cmd = "cat /Application/hera/packages/NLA_Pick/conf/channels.txt"
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        print "Get pubchannel id error %s" %(stderrdata,)
        sys.exit(2)
    else:
        return stdoutdata.strip().split("\n")

def parseChannel(xmlf, db):
    transfer_channels = get_transfer_channels()
    pub_channels = get_pubchannels_id()
    job_day = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
    xmldoc = minidom.parse(xmlf)
    channellist = xmldoc.getElementsByTagName("channel")
    c = db.cursor()
    for element in channellist:
        try:
            channel_id = element.attributes["channelId"].value
            if channel_id in pub_channels and channel_id not in transfer_channels:
                user_id = element.attributes["userId"].value
                priority = PriotiryDict[element.attributes["pubPriority"].value.split("P")[1]]
                c.execute("""
                insert into hadoop_channeljob(user_id,user_name,channel_id,channel_name,priority,source_path,source_fline,
                    source_fsize,target_path,target_fline,target_fsize,job_execute_time,status,job_day,update_time,
                    pub_mime_filter,pub_url_filter,pub_way,pub_is_filter,pub_format_type,pub_ftp_ip,pub_ftp_port,
                    pub_ftp_dir,pub_ftp_user,pub_ftp_passwd)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (user_id,element.attributes["userName"].value,channel_id,element.attributes["channelName"].value,priority,
                 "/fc/src/%s/*/%s/%s" %(job_day, user_id, channel_id),0,0,"/fc/pub/%s/%s/%s" %(job_day, user_id, channel_id),0,0,0,0,
                 datetime.strptime(job_day, "%Y%m%d"), datetime.now(), element.attributes["pubMimeFilter"].value,
                 element.attributes["pubUrlFilter"].value,element.attributes["pubWay"].value,
                 element.attributes["pubIsFilter"].value,element.attributes["pubFormatType"].value,
                 element.attributes["pubFtpIp"].value, element.attributes["pubFtpPort"].value,
                 element.attributes["pubFtpDir"].value, element.attributes["pubFtpUser"].value,
                 element.attributes["pubFtpPassword"].value)
                )
        except Exception, e:
            print e
    c.close()

if __name__ == "__main__":
    res = os.popen("ps aux | grep -v grep | grep \'parser_pubchannel.py\'")
    if len(res.readlines()) > 2:
        print "parser_pubchannel.py has already run, exit at %s" %(datetime.today(), )
        sys.exit()
    
    print "App start at %s" %(datetime.now())
    db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="eagleeye", charset="utf8")
    parseChannel("LogPubChannelConfig.xml", db)
    print "App end at %s" %(datetime.now())