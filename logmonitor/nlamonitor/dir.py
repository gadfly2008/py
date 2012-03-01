#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import time
from controller import start_vsftp, stop_vsftp, get_vsftp_status
from os.path import getsize, join
from glob import glob

class DirMonitor(object):
    def __init__(self, logger, task, hostname, dtime):
        self.logger = logger
        self.task = task
        self.hostname = hostname
        self.dtime = dtime
        
    def run(self):
        global master_dir, isTempWarning, args
        try:
            files = glob("%s/*.%s" %(self.task.get("path"), self.task.get("suffix")))
            count = len(files)
            size = 0
            for fname in files:
                try:
                    size += getsize(join(self.task.get("path"), fname))
                except Exception, e:
                    self.logger.error(e)
            arg = {"hostname": self.hostname, "name": self.task.get("path"), "count": count,"size": size, "datetime": self.dtime}

            if self.task.get("path") == "/proclog/loganalysis/begin":
                master_dir = size
                
            if size > self.task.get("threshold"):
                arg["level"] = "3"
                if self.task.get("path") == "/proclog/2nd_edition/temp":
                    isTempWarning = 1
            else:
                arg["level"] = "0"
            args.append(arg)
        except Exception, e:
            self.logger.error(e)
        finally:
            time.sleep(3)
    
def dir_monitor(logger, hostname, dirs, cp, dtime):
    global master_dir, isTempWarning, args
    master_dir = 0
    isTempWarning = 0
    args = []
    
    for d in dirs.split(","):
        task = {"path": cp.get("%s" %(d,), "dir").strip(),
               "threshold": cp.getint("%s" %(d,), "threshold"),
               "suffix": cp.get("%s" %(d,), "suffix").strip()}
        logger.debug("Parser dir %s" %(task["path"]))
        d = DirMonitor(logger, task, hostname, dtime)
        d.run()

    time.sleep(3)

    vsftp_status = get_vsftp_status()

    if master_dir > 4294967296:
        if vsftp_status == "running":
            logger.debug("stop vsftp")
            stop_vsftp()
    elif master_dir < 3221225472:
        if vsftp_status == "stop":
            logger.debug("start vsftp")
            start_vsftp()

    logger.debug("Get dirs complete.")
    return {"dir": args, "masterdir": master_dir, "isTempWarning": isTempWarning}