#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import threading
import subprocess
import time
import sys
import os
import logging
import logging.config
import ConfigParser
from Queue import Queue
from os.path import join, exists
from datetime import datetime
from ssh import Connection
from device import get_devices, get_device_by_file
from mail import SendMail

def sync_file(conn, checkpoint, logger):
    cmd = "md5sum %s | gawk \'{print $1}\'" %(checkpoint.get("remote_file"))
    local = conn.execute(cmd).get("output")[0].strip()

    if checkpoint.get("svn") != local:
        logger.debug("Device %s need sync %s" %(conn._host, checkpoint.get("fname")))
        conn.put(checkpoint.get("local_file"), checkpoint.get("remote_file"))
        conn.execute("chown fromcf.fromcf %s" %(checkpoint.get("remote_file")))
        if checkpoint.get("fname").endswith("sh"):
            conn.execute("chmod +x %s" %(checkpoint.get("remote_file")))
        new_local = conn.execute(cmd).get("output")[0].strip()

        if checkpoint.get("svn") != new_local:
            return {"fname": checkpoint.get("fname"), "local": local, "svn": checkpoint.get("svn"), "status": u"同步失败"}
        else:
            return {"fname": checkpoint.get("fname"), "local": local, "svn": checkpoint.get("svn"), "status": u"同步成功"}
    return {}

def sync_movelog(conn, logger):
    cmd = "md5sum /Application/move_log/move_log.sh | gawk \'{print $1}\'"
    local = conn.execute(cmd).get("output")[0].strip()
    svn = get_md5("packages/move_log/move_log.sh")

    if svn != local:
        logger.debug("Device %s need sync movelog" %(conn._host,))
        conn.put("packages/move_log/move_log.sh", "/Application/move_log/move_log.sh")
        conn.execute("chown fromcf.fromcf /Application/move_log/move_log.sh")
        conn.execute("chmod +x /Application/move_log/move_log.sh")

        new_local = conn.execute(cmd).get("output")[0].strip()

        if svn != new_local:
            return {"fname": "move_log.sh", "local": local, "svn": svn, "status": u"同步失败"}
        else:
            return {"fname": "move_log.sh", "local": local, "svn": svn, "status": u"同步成功"}
    return {}

class NLACheck(threading.Thread):
    def __init__(self, logger, q, checkpoint):
        threading.Thread.__init__(self)
        self.logger = logger
        self.q = q
        self.checkpoint = checkpoint

    def run(self):
        global result
        while True:
            if self.q.empty():
                break
            try:
                device = self.q.get()
                self.logger.debug("Do in %s" %(device.hostname,))
                conn = Connection(device.ip, int(device.port), device.user, device.password)
                try:
                    for each in self.checkpoint:
                        syncResult = sync_file(conn, each, self.logger)
                        if syncResult:
                            if not result.has_key(device.hostname):
                                result[device.hostname] = []
                            result[device.hostname].append(syncResult)

                    syncMovelog = sync_movelog(conn, self.logger)
                    if syncMovelog:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncMovelog)
                    
                    self.logger.debug("Host %s check complete." %(device.hostname,))
                except Exception, e:
                    self.logger.error("Hostname:%s Error:%s" %(device.hostname, e))
                    if not result.has_key(device.hostname):
                        result[device.hostname] = []
                    result[device.hostname].append({"error": "%s" %(e,)})
                finally:
                    conn.close()
                    time.sleep(2)
                    self.q.task_done()
            except Exception, e:
                self.logger.error(e)
                self.q.task_done()

def get_md5(f):
    cmd = "md5sum %s" %(f,)
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()

    return stdoutdata.split("\n")[0].split()[0]

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.info("App has already run, exit at %s" %(datetime.today()))
        sys.exit()
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("nla")
    try:
        check_run_pid("nla_sync.py", logger)
        cp = ConfigParser.ConfigParser()
        cp.read("conf/app.cfg")
        checkpoint = []

        localpath = cp.get("nla_check", "localpath")
        remotepath = cp.get("nla_check", "remotepath")
        for target in cp.get("nla_check", "targets").split(","):
            checkpoint.append({
                "fname": cp.get("nla_check", target).strip().split("/")[-1],
                "svn": get_md5(join(localpath, cp.get("nla_check", target).strip())),
                "local_file": join(localpath, cp.get("nla_check", target).strip()),
                "remote_file": join(remotepath, cp.get("nla_check", target).strip())
            })

        q = Queue()
        global result
        result = {}
        if exists("testlist.txt"):
            devices = get_devices("http://rcmsapi.chinacache.com:36000/app/name/NLA/OPEN/devices", "testlist.txt")
        else:
            devices = get_devices("http://rcmsapi.chinacache.com:36000/app/name/NLA/OPEN/devices")

        if exists("otherlist.txt"):
            devices = devices + get_device_by_file("otherlist.txt")

        for d in devices:
            q.put(d)

        logger.debug("There are %s devices." %(len(devices)))
        for i in range(8):
            n = NLACheck(logger, q, checkpoint)
            n.setDaemon(True)
            n.start()

        time.sleep(3)
        q.join()

        logger.debug("%s" %(result,))
        if result:
            sm = SendMail("zhigang.li@chinacache.com", "log@chinacache.com", u"NLA 程序同步检查", result)
            sm.sendmail()
            logger.debug("Send mail.")
    except Exception, e:
        logger.error(e)