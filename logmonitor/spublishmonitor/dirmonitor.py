#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import socket
import logging
import logging.config
import ConfigParser
import os
import json
import sys
import subprocess
import urllib
import urllib2
from os.path import join, getsize
from datetime import datetime
from glob import glob
from mail_message import SendMail, SendMessage

def data_format(data):
    KB = 1024
    MB = 1024*1024
    GB = 1024*1024*1024
    
    if data < KB:
        return "%s" %(data,)
    elif float(data)/KB < KB:
        return "%.2f%s" %(float(data)/KB, "KB")
    elif float(data)/MB < KB:
        return "%.2f%s" %(float(data)/MB, "MB")
    elif float(data)/GB < KB:
        return "%.2f%s" %(float(data)/GB, "GB")

def update_data(logger, api, args):
    try:
        res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)
    
def get_blocks(logger):
    cmd = "df | sed \'1d\' | gawk \'{print $4,$5,$6}\'"
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get blocks info error")
        return ""
    else:
        return stdoutdata

def waring(logger, body):
    mail = SendMail(body)
    mail.sendmail()
    logger.debug("Send mail.")
    message = SendMessage(body)
    message_result = message.sendmessage()
    logger.debug("Send message %s" %(message_result, ))

def get_dirinfo(logger, path, suffix):
    files = glob("%s/*.%s" %(path, suffix))
    count = len(files)
    size = 0
    for fname in files:
        try:
            size += getsize(join(path, fname))
        except Exception, e:
            logger.error(e)
    return {"count": count, "size": size}
    
class DirMonitor(object):
    def __init__(self, logger, task, body, current):
        self.logger = logger
        self.task = task
        self.body = body
        self.current = current
        
    def run(self):
        self.logger.debug("Monitor path %s" %(self.task.get("path")))
        try:
            res = get_dirinfo(self.logger, self.task.get("path"), self.task.get("suffix"))
            if res.get("count") > self.task.get("threshold"):
                self.body["dirs"][self.task.get("path")] = u"目录大小: %s 文件数: %s" %(data_format(res.get("size")), res.get("count"))
                
            return {"hostname": self.body.get("hostname"), "name": self.task.get("path"), "count": res.get("count"),
                    "size": res.get("size"), "datetime": self.current}
        except Exception, e:
            self.logger.error(e)
            return {"hostname": self.body.get("hostname"), "name": self.task.get("path"), "count": 0, "size": 0, "datetime": self.current}

def blockMonitor(logger, body):
    blocks = [b.strip() for b in get_blocks(logger).split("\n")]
    args = []
    for b in blocks:
        if b:
            avaiable, used, name = b.split(" ")
            used = int(used.split("%")[0])
            if used > 85:
                body["blocks"][name] = used
            args.append({"hostname": body.get("hostname"), "used": used, "name": name})
    return args

def check_run_pid(logger, app):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.debug("App has already run, exit at %s" %(datetime.today()))
        sys.exit()
    else:
       logger.debug("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("publishmonitor")
    try:
        check_run_pid(logger, "dirmonitor.py")
        cp = ConfigParser.ConfigParser()
        cp.read("conf/app.cfg")
        
        current = datetime.now().strftime("%Y-%m-%d %H:%M")
        body = {"hostname": socket.gethostname(), "dirs": {}, "blocks": {}}
        api = cp.get("main","api_lc").strip()

        dirs = []
        for d in cp.get("main","dirs").strip().split(","):
            task = {"path": cp.get(d, "path").strip(),"threshold": cp.getint(d, "threshold"),"suffix": cp.get(d, "suffix").strip()}
            d = DirMonitor(logger, task, body, current)
            dirs.append(d.run())
        
        blocks = blockMonitor(logger, body)

        update_data(logger, api, {"dir": dirs, "block": blocks})
        logger.debug("Update data ok.")
        
        if body["dirs"] or body["blocks"]:
            waring(logger, body)
    except Exception, e:
        logger.error(e)