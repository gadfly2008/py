#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from api import get_channels
from Queue import Queue
from datetime import datetime, date
from os.path import getsize, exists
import os
import sys
import time
import logging
import logging.config
import threading
import socket
import subprocess
import urllib
import urllib2
import json

VIPS = ["xinhua","gov","qidian","aobi","people","chinanews","china","chinadaily","icbc","ifeng","chinabroadcast","chinataiwan","cenc","rayli","mozilla","cipg","fund","gaopeng","sohu"]
SOURCE = {"BGP-BJ-2-5A1": "storage-3", "CCN-BJ-5-5I9": "storage-2"}

def get_hour():
    hour = datetime.now().hour - 1
    if hour < 10:
        return "0%s" %(hour,)
    return "%s" %(hour,)
    
def get_today():
    return date.today().strftime("%Y%m%d")

def post_result(result, datestr, logger):
    api = "http://logmonitor.chinacache.net:8888/publisher/publishdelay/add/"
    args = []
    for key,value in result.items():
        args.append({"datetime": datestr, "size": value, "source": SOURCE[socket.gethostname()], "user_name": key})
    try:
        res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.info("%s has already run, exit at %s" %(app, datetime.today()))
        sys.exit()
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

class FindDelayLog(threading.Thread):
    def __init__(self, logger, queue, channels, today):
        threading.Thread.__init__(self)
        self.logger = logger
        self.q = queue
        self.channels = channels
        self.today = today
        
    def run(self):
        global mutex, res
        while True:
            if self.q.empty():
                break
            path = self.q.get()
            self.logger.debug(path)
            if exists(path):
                cmd = "find %s -type f" %(path,)
                p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdoutdata, stderrdata = p.communicate()
                for each in stdoutdata.split("\n"):
                    f = each.strip()
                    try:
                        if f:
                            user = self.channels.get(f.split("/")[6])
                            filename = f.split("/")[-1]
                            filetime = filename.split(".")[0].split("_")[-1]
                            if filetime != self.today:
                                mutex.acquire()
                                res[user] += getsize(f)
                                self.logger.debug("Log %s delay" %(f,))
                                mutex.release()
                    except Exception, e:
                        self.q.task_done()
                        self.logger.error("%s %s" %(f, e))
            time.sleep(2)
            self.logger.debug("%s complete." %(path,))
            self.q.task_done()

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("monitor")
    try:
        check_run_pid("delaymonitor.py", logger)
        q = Queue()
        channels = get_channels(logger, VIPS)
        
        hour = get_hour()
        today = get_today()
        root_dir = "/data/Data/logpub/logpublish_begin/%s%s" %(today, hour)
        for key,value in channels.items():
            path = "%s/%s" %(root_dir, key)
            q.put(path)
        
        global mutex, res
        res = {}
        for vip in VIPS:
            res[vip] = 0
        mutex = threading.Lock()
        for i in range(28):
            delay = FindDelayLog(logger,q,channels,today)
            delay.setDaemon(True)
            delay.start()
        
        time.sleep(3)
        q.join()
        post_result(res, "%s%s" %(today, hour), logger)
        logger.debug("App complete.")
    except Exception, e:
        logger.error(e)