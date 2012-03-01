#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import threading
import subprocess
import time
import os
import sys
import logging
import logging.config
from Queue import Queue
from ssh import Connection
from device import get_devices, get_device_by_file
from mail import SendMail
from datetime import datetime
from os.path import exists

def get_md5(f):
    cmd = "md5sum %s" %(f,)
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()

    return stdoutdata.split("\n")[0].split()[0]

def sync_python(conn, logger):
    svn = "Python 2.7.1"
    local = conn.execute("/usr/local/bin/python -V").get("output")[0].strip()
    
    if svn != local:
        logger.debug("Device %s need sync python" %(conn._host,))
        conn.put("./packages/Python-2.7.1.tgz", "/root/Python-2.7.1.tgz")
        conn.execute("cd /root; tar zxvf Python-2.7.1.tgz")
        conn.execute("cd /root/Python-2.7.1; ./configure;make;make install")
        new_local = conn.execute("/usr/local/bin/python -V").get("output")[0].strip()
        
        if svn != new_local:
            return {"fname": "python", "local": local, "svn": svn, "status": u"同步失败"}
        else:
            return {"fname": "python", "local": local, "svn": svn, "status": u"同步成功"}
    return {}

def sync_monitor(conn, check, logger):
    if not conn.has_path("/Application/nlamonitor"):
        logger.debug("Device %s need init env" %(conn._host,))
        conn.mkdir("/Application/nlamonitor")
        conn.mkdir("/Application/nlamonitor/logs")
        conn.mkdir("/Application/nlamonitor/conf")

    if not conn.has_content("nlamonitor.py", "/var/spool/cron/root"):
        logger.debug("Device %s need init nlamonitor crond" %(conn._host,))
        conn.execute("echo '*/10 * * * * . /etc/profile; cd /Application/nlamonitor/; /usr/local/bin/python nlamonitor.py >> /Application/nlamonitor/logs/run.log 2>&1' >> /var/spool/cron/root")
    if not conn.has_content("performance.py", "/var/spool/cron/root"):
        logger.debug("Device %s need init performance crond" %(conn._host,))
        conn.execute("echo '*/2 * * * * . /etc/profile; cd /Application/nlamonitor/; /usr/local/bin/python performance.py >> /Application/nlamonitor/logs/run.log 2>&1' >> /var/spool/cron/root")
    if not conn.has_content("process_speed.py", "/var/spool/cron/root"):
        logger.debug("Device %s need init process_speed crond" %(conn._host,))
        conn.execute("echo '*/15 * * * * . /etc/profile; cd /Application/nlamonitor/; /usr/local/bin/python process_speed.py >> /Application/nlamonitor/logs/run.log 2>&1' >> /var/spool/cron/root")
    conn.execute("/etc/init.d/crond restart")

    cmd = "md5sum %s | gawk \'{print $1}\'" %(check.get("remote"))
    local = conn.execute(cmd).get("output")[0].strip()
    if check.get("svn") != local:
        logger.debug("Device %s need sync %s" %(conn._host, check.get("fname")))
        conn.put(check.get("local"), check.get("remote"))
        new_local = conn.execute(cmd).get("output")[0].strip()

        if check.get("svn") != new_local:
            return {"fname": check.get("fname"), "local": local, "svn": check.get("svn"), "status": u"同步失败"}
        else:
            return {"fname": check.get("fname"), "local": local, "svn": check.get("svn"), "status": u"同步成功"}
    return {}

class NLAMonitorSync(threading.Thread):
    def __init__(self, logger, queue, checks):
        threading.Thread.__init__(self)
        self.q = queue
        self.logger = logger
        self.checks = checks
        
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
                    syncPython = sync_python(conn, self.logger)
                    if syncPython:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncPython)
                    for check in self.checks:
                        syncMonitor = sync_monitor(conn, check, self.logger)
                        if syncMonitor:
                            if not result.has_key(device.hostname):
                                result[device.hostname] = []
                            result[device.hostname].append(syncMonitor)
                    self.logger.debug("Check nla monitor on device %s complete." %(device.ip,))
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

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.info("App has already run, exit at %s" %(datetime.today()))
        sys.exit()
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("monitor")
    try:
        check_run_pid("nlamonitor_sync.py", logger)
        if exists("testlist.txt"):
            devices = get_devices("http://rcmsapi.chinacache.com:36000/app/name/NLA/OPEN/devices", "testlist.txt")
        else:
            devices = get_devices("http://rcmsapi.chinacache.com:36000/app/name/NLA/OPEN/devices")

        if exists("otherlist.txt"):
            devices = devices + get_device_by_file("otherlist.txt")
        
        logger.debug("There are %s devices." %(len(devices)))
        q = Queue()
    
        global result
        result = {}
        for d in devices:
            q.put(d)

        checks = [
              {"fname": "nlamonitor.py", "svn": get_md5("packages/nlamonitor/nlamonitor.py"), "local": "packages/nlamonitor/nlamonitor.py", "remote": "/Application/nlamonitor/nlamonitor.py"},
              {"fname": "block.py", "svn": get_md5("packages/nlamonitor/block.py"), "local": "packages/nlamonitor/block.py", "remote": "/Application/nlamonitor/block.py"},
              {"fname": "controller.py", "svn": get_md5("packages/nlamonitor/controller.py"), "local": "packages/nlamonitor/controller.py", "remote": "/Application/nlamonitor/controller.py"},
              {"fname": "dir.py", "svn": get_md5("packages/nlamonitor/dir.py"), "local": "packages/nlamonitor/dir.py", "remote": "/Application/nlamonitor/dir.py"},
              {"fname": "mail_message.py", "svn": get_md5("packages/nlamonitor/mail_message.py"), "local": "packages/nlamonitor/mail_message.py", "remote": "/Application/nlamonitor/mail_message.py"},
              {"fname": "performance.py", "svn": get_md5("packages/nlamonitor/performance.py"), "local": "packages/nlamonitor/performance.py", "remote": "/Application/nlamonitor/performance.py"},
              {"fname": "process_speed.py", "svn": get_md5("packages/nlamonitor/process_speed.py"), "local": "packages/nlamonitor/process_speed.py", "remote": "/Application/nlamonitor/process_speed.py"},
              {"fname": "app.cfg", "svn": get_md5("packages/nlamonitor/conf/app.cfg"), "local": "packages/nlamonitor/conf/app.cfg", "remote": "/Application/nlamonitor/conf/app.cfg"},
              {"fname": "logging.conf", "svn": get_md5("packages/nlamonitor/conf/logging.conf"), "local": "packages/nlamonitor/conf/logging.conf", "remote": "/Application/nlamonitor/conf/logging.conf"},
        ]
        for i in range(8):
            n = NLAMonitorSync(logger, q, checks)
            n.setDaemon(True)
            n.start()
        
        time.sleep(3)
        q.join()
        
        logger.debug("%s" %(result,))
        if result:
            sm = SendMail("zhigang.li@chinacache.com", "zhigang.li@chinacache.com,gen.li@chinacache.com,peng.xu@chinacache.com", u"NLA monitor同步检查", result)
            sm.sendmail()
            logger.debug("Send mail.")
    except Exception, e:
        logger.error(e)