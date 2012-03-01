#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from Queue import Queue
from os.path import join, getsize, exists
import os
import subprocess
import sys
import logging
import logging.config
import ConfigParser
import urllib
import urllib2
import threading
import time
import json

DATETYPE = "%Y%m%d"

def string_toDatetime(string):
    return datetime.strptime(string, DATETYPE)
    
def get_today(datestr=None):
    if datestr:
        today = datestr
    else:
        today = (date.today()-timedelta(days=1)).strftime(DATETYPE)
    return today

def update_data(logger, api, args):
    threshold = 200
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

def get_dayQueue(logger, cf, today):
    try:
        q = Queue()
        day_pubDir = cf.get("main", "day_publish")
        for u in os.listdir(day_pubDir):
            q.put({"uId": u.strip(), "dir": "%s/%s/%s/" %(day_pubDir, u.strip(), today)})
        
        return q
    except Exception, e:
        logger.error(e)
    
def get_hourQueue(logger, cf, today):
    try:
        q = Queue()
        sysconf = cf.get("main", "sysconf")
        cmd = "cat %s | grep \'log.hour.result.dir\' | gawk -F \'=\' \'{print $2}\'" %(sysconf,)
        p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        hour_pubDir = stdoutdata.split("\n")[0].strip()
        cmd = "cat %s | grep \'\<hour.publish.userids\>\' | gawk -F \'=\' \'{print $2}\'" %(sysconf,)
        p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        for u in stdoutdata.split("\n")[0].split(","):
            q.put({"uId": u.strip(), "dir": "%s/%s/%s/" %(hour_pubDir, u.strip(), today)})
            
        return q
    except Exception, e:
        logger.error(e)

class DayPublisher(threading.Thread):
    def __init__(self, logger, q, today):
        threading.Thread.__init__(self)
        self.q = q
        self.logger = logger
        self.today = today
        
    def run(self):
        global total, singlelock, args
        while True:
            if self.q.empty():
                break
            
            task = self.q.get()
            path = task.get("dir")
            if exists(path):
                for f in os.listdir(path):
                    try:
                        cId = f.split("_")[0]
                        fsize = getsize(join(path, f))
                        singlelock.acquire()
                        total = total + fsize
                        singlelock.release()
                        args.append({"cId": cId, "uId": task.get("uId"), "datetime": self.today,"size": fsize})
                    except Exception, e:
                        self.logger.error(e)
            time.sleep(2)
            self.q.task_done()
        
class HourPublisher(threading.Thread):
    def __init__(self, logger, q, today, channels):
        threading.Thread.__init__(self)
        self.q = q
        self.logger = logger
        self.today = today
        self.channels = channels
        
    def run(self):
        global total, singlelock, args
        while True:
            if self.q.empty():
                break
            task = self.q.get()
            path = task.get("dir")
            if exists(path):
                temp = {}
                for f in os.listdir(path):
                    try:
                        cName = f.split("-")[0]
                        fsize = getsize(join(path, f))
                        singlelock.acquire()
                        total = total + fsize
                        singlelock.release()
                        cmd = "cat %s | grep \'%s\' | gawk \'{print $2}\'" %(self.channels, cName)
                        p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdoutdata, stderrdata = p.communicate()
                        cId = stdoutdata.split("\n")[0].strip()
                        singlelock.acquire()
                        if not temp.has_key(cId):
                            temp[cId] = 0
                        temp[cId] = temp.get(cId) + fsize
                        singlelock.release()
                    except Exception, e:
                        self.logger.error(e)
                for key,value in temp.items():
                    args.append({"cId": key, "uId": task.get("uId"), "datetime": self.today,"size": value})
            time.sleep(2)
            self.q.task_done()

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.info("%s has already run, exit at %s" %(app, datetime.today()))
        sys.exit()
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("publishmonitor")
    try:
        check_run_pid("publishmonitor.py", logger)
        cfp = ConfigParser.ConfigParser()
        cfp.read("conf/app.cfg")
        
        api = cfp.get("main", "api_total").strip()
        if len(sys.argv) > 1:
            today = get_today(sys.argv[1])
        else:
            today = get_today()
            
        dayQ = get_dayQueue(logger, cfp, today)
        hourQ = get_hourQueue(logger, cfp, today)
        global total, singlelock, args
        singlelock = threading.Lock()
        total = 0
        args = []
        
        for i in range(5):
            d = DayPublisher(logger, dayQ, today)
            d.setDaemon(True)
            d.start()
        for i in range(2):
            h = HourPublisher(logger, hourQ, today, cfp.get("main", "channel"))
            h.setDaemon(True)
            h.start()
        
        time.sleep(3)
        dayQ.join()
        hourQ.join()

        logger.debug(("Add spublish."))
        update_data(logger, cfp.get("main", "api_detail"), args)

        logger.debug("Storage-0 %s size %s" %(today, total))
        update_data(logger, cfp.get("main", "api_total"), [{"today": today, "size": total, "source": "storage-0"}])
    except Exception, e:
        logger.error(e)