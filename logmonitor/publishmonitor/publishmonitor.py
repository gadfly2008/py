#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from api import publish_by_channel, get_channels, get_channelinfo
from mail import SendMail
from datetime import datetime, date, timedelta
from Queue import Queue
import cx_Oracle
import os
import threading
import sys
import logging
import logging.config
import ConfigParser
import urllib
import urllib2
import time
import json
os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"

DATETYPE = "%Y%m%d"
    
def get_today(datestr=None):
    if datestr:
        today = datestr
    else:
        today = date.today().strftime(DATETYPE)
    return datetime.strptime(today, DATETYPE)

def update_data(logger, api, args):
    threshold = 180
    if not len(args) % threshold:
        page_count = len(args)/threshold
    else:
        page_count = (len(args)/threshold) + 1
    
    for i in range(1,page_count+1,1):
        try:
            res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args[(threshold*i-threshold):threshold*i], ensure_ascii=False, sort_keys=True, indent=4)})).read()
            logger.debug(res)
        except Exception, e:
            logger.error(e)

def get_rate(today_size, lastweek_size):
    if today_size > lastweek_size or lastweek_size == 0:
        return float(0)
    else:
        return (float(lastweek_size - today_size)/lastweek_size)*100

def sort_body(body):
    temp = {}
    for key, value in body.items():
        temp[key] = sorted(value, key=lambda d:d.get("rate"), reverse=True)
        
    return temp

def warning_mail(logger, cf, body, begin):
    if body:
        from_addr = cf.get("mail", "from_addr").strip()
        to_addr = cf.get("mail", "to_addr").strip()
        try:
            body = sort_body(body)
            mail = SendMail(from_addr, to_addr, body, "%s" %(begin,), "%s" %(begin-timedelta(days=1)))
            mail.sendmail()
            logger.debug("Send warning mail.")
        except Exception, e:
            logger.error(e)

def db_conn():
    a_dhost = "172.16.21.203"
    a_duser = "logpub"
    a_dpassword = "IUdaga867Wba"
    
    conn = cx_Oracle.connect(a_duser, a_dpassword, cx_Oracle.makedsn(a_dhost,1521,"logpub"))
    return conn

class Publisher(threading.Thread):
    def __init__(self, logger, q, begin, end, rate, users):
        threading.Thread.__init__(self)
        self.logger = logger
        self.q = q
        self.begin = begin
        self.end = end
        self.rate = rate
        self.users = users
        
    def run(self):
        global body, args, singlelock
        while True:
            if self.q.empty():
                break
            try:
                conn = db_conn()
                try:
                    task = self.q.get()
                    channel_id = task.get("cId")
                    userId, userName, channelName = get_channelinfo(conn, channel_id).split(",")
                    today_size = publish_by_channel(conn,channel_id,self.begin,self.end)
                    self.logger.debug("Channel %s(%s) date %s size %s" %(channelName, channel_id, self.begin, today_size))

                    lastday_size = publish_by_channel(conn,channel_id,(self.begin-timedelta(days=1)),self.begin)
                    self.logger.debug("Channel %s(%s) date %s size %s" %(channelName, channel_id, (self.begin-timedelta(days=1)), lastday_size))

                    actual = get_rate(today_size, lastday_size)
                    if actual > self.rate and lastday_size > 1*1024*1024:
                        if userName in self.users:
                            singlelock.acquire()
                            if not body.has_key(userName):
                                body[userName] = []
                            body[userName].append({"channelname": channelName, "today_size": today_size, "lastday_size": lastday_size, "rate": actual})
                            singlelock.release()

                    if lastday_size > 1*1024*1024:
                        args.append({"cId": channel_id, "uId": userId, "datetime": self.begin.strftime(DATETYPE), "size": today_size})
                        args.append({"cId": channel_id, "uId": userId, "datetime": (self.begin-timedelta(days=1)).strftime(DATETYPE), "size": lastday_size})
                finally:
                    time.sleep(2)
                    self.q.task_done()
            except Exception, e:
                self.logger.error(e)

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.info("%s has already run, exit at %s" %(app, datetime.today()))
        sys.exit()
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("monitor")
    try:
        check_run_pid("publishmonitor.py", logger)
        cfp = ConfigParser.ConfigParser()
        cfp.read("conf/app.cfg")
        
        rate = cfp.getfloat("main", "rate")
        users = cfp.get("main", "users").strip().split(",")
        api = cfp.get("main","api_detail")
        if len(sys.argv) > 1:
            begin = get_today(sys.argv[1]) - timedelta(days=1)
        else:
            begin = get_today() - timedelta(days=1)
        end = begin + timedelta(days=1)
        
        q = Queue()
        global body, args, singlelock
        singlelock = threading.Lock()
        body = {}
        args = []
        
        conn = db_conn()
        for c in get_channels(conn, begin, end):
            q.put({"cId": c})
        conn.close()
        
        for i in range(12):
            p = Publisher(logger, q, begin, end, rate, users)
            p.setDaemon(True)
            p.start()
        
        time.sleep(5)
        q.join()
        
        logger.debug("Begin to update data.")
        update_data(logger, api, args)

        logger.debug("Get channel size complete.")
        warning_mail(logger, cfp, body, begin)
    except Exception, e:
        logger.error(e)