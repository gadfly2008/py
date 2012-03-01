#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import threading
import time
import os
import logging
import subprocess
import sys
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

def sync_java(conn, logger):
    svn = "Jdk 1.6.0_21"
    path = "/usr/java/jdk1.6.0_26"
    if not conn.has_path(path):
        logger.debug("Device %s need sync java" %(conn._host,))
        conn.put("./packages/jdk-6u26-linux-i586.rpm", "/root/jdk-6u26-linux-i586.rpm")
        conn.execute("cd /root; rpm -ih jdk-6u26-linux-i586.rpm")

        if not conn.has_path(path):
            return {"fname": "java", "local": "none", "svn": svn, "status": u"同步失败"}
        else:
            return {"fname": "java", "local": svn, "svn": svn, "status": u"同步成功"}
    return {}

def sync_hadoop(conn, logger):
    svn = "0.20.2-cdh3u1"
    path = "/Application/hadoop/hadoop-%s" %(svn,)
    if not conn.has_path(path):
        logger.debug("Device %s need sync hadoop" %(conn._host,))
        conn.execute("mkdir -p /Application/hadoop")
        conn.execute("chown -R hadoop:fromcf /Application/hadoop/")
        conn.put("./packages/hadoop-0.20.2-cdh3u1.tgz", "/Application/hadoop/hadoop-0.20.2-cdh3u1.tgz")
        conn.execute("cd /Application/hadoop; tar zxf hadoop-0.20.2-cdh3u1.tgz")

        if not conn.has_path(path):
            return {"fname": "hadoop", "local": "none", "svn": svn, "status": u"同步失败"}
        else:
            return {"fname": "hadoop", "local": svn, "svn": svn, "status": u"同步成功"}
    return {}

def sync_lzop(conn, logger):
    svn = "1.03"
    cmd = "lzop --version | head -1"
    local = conn.execute(cmd).get("output")[0].strip().split()[1]
    if local != svn:
        logger.debug("Device %s need sync lzop" %(conn._host,))
        conn.put("./packages/lzop-1.03-i386_linux.tar.gz", "/root/lzop-1.03-i386_linux.tar.gz")
        conn.execute("cd /root; tar zxf lzop-1.03-i386_linux.tar.gz; cd /root/lzop-1.03-i386_linux; cp lzop /usr/bin")
        new_local = conn.execute(cmd).get("output")[0].strip().split()[1]

        if svn != new_local:
            return {"fname": "lzop", "local": local, "svn": svn, "status": u"同步失败"}
        else:
            return {"fname": "lzop", "local": local, "svn": svn, "status": u"同步成功"}
    return {}

def sync_crond(conn, logger):
    if not conn.has_path("/var/spool/cron/hadoop"):
        conn.execute("echo '5 * * * * /Application/nla/NLA_Pick/startup.sh >> /Application/nla/NLA_Pick/logs/run.log 2>&1' >> /var/spool/cron/hadoop")
        conn.execute("echo '*/10 * * * * /Application/nla/HDFS_Client/startup.sh >> /Application/nla/HDFS_Client/logs/run.log 2>&1' >> /var/spool/cron/hadoop")

    else:
        if not conn.has_content("/NLA_Pick/startup.sh", "/var/spool/cron/hadoop"):
            logger.debug("Device %s need init nlapick crond" %(conn._host,))
            conn.execute("echo '5 * * * * /Application/nla/NLA_Pick/startup.sh >> /Application/nla/NLA_Pick/logs/run.log 2>&1' >> /var/spool/cron/hadoop")

        if not conn.has_content("/HDFS_Client/startup.sh", "/var/spool/cron/hadoop"):
            logger.debug("Device %s need init hdfsclient crond" %(conn._host,))
            conn.execute("echo '*/10 * * * * /Application/nla/HDFS_Client/startup.sh >> /Application/nla/HDFS_Client/logs/run.log 2>&1' >> /var/spool/cron/hadoop")
    conn.execute("/etc/init.d/crond restart")

def sync_file(conn, check, logger):
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

def sync_initAppEnv(conn, logger):
    path = "/Application/nla"
    if not conn.has_path(path):
        logger.debug("Device %s need sync init app env" %(conn._host,))

        conn.execute("useradd hadoop -g fromcf")
        conn.execute("mkdir -p /data/cache1/nla/original_log/index/")
        conn.execute("mkdir -p /data/cache1/nla/original_log/temp/")
        conn.execute("mkdir -p /data/cache1/nla/original_log/src/")
        conn.execute("mkdir -p /data/cache1/nla/original_log/dest/")
        conn.execute("mkdir -p /data/cache1/nla/hadoop/tmp/")
        conn.execute("mkdir -p /Application/nla")
        
        conn.execute("ln -s /data/cache1/nla/original_log /Application/nla/original_log")
        conn.execute("ln -s /data/cache1/nla/hadoop /data/hadoop")

        conn.execute("chmod 777 /data/cache1/nla/original_log/*")
        conn.execute("chown -R hadoop:fromcf /data/cache1/nla/")
        conn.execute("chown -R hadoop:fromcf /Application/nla/")

        hostname = conn.execute("hostname").get("output")[0].strip()
        if not conn.execute("cat /etc/hosts | grep \'127.0.0.1\' | grep \'%s\'" %(hostname,)).get("output")[0].strip():
            conn.execute("echo '127.0.0.1    %s' >> /etc/hosts" %(hostname,))

        if not conn.has_path(path):
            return {"fname": "appenv", "local": "none", "svn": "new", "status": u"同步失败"}
        else:
            return {"fname": "appenv", "local": "new", "svn": "new", "status": u"同步成功"}
    return {}

def sync_hdfsClient(conn, logger):
    hdfs_client = "/Application/nla/HDFS_Client"
    if not conn.has_path(hdfs_client):
        logger.debug("Device %s need sync hdfsclient app" %(conn._host,))
        conn.put("./packages/HDFS_Client.tgz", "/Application/nla/HDFS_Client.tgz")
        conn.execute("cd /Application/nla; tar zxf HDFS_Client.tgz")
        conn.execute("chown -R hadoop:fromcf /Application/nla/HDFS_Client")

        if not conn.has_path(hdfs_client):
            return {"fname": "hdfsclient", "local": "none", "svn": "new", "status": u"同步失败"}
        else:
            return {"fname": "hdfsclient", "local": "new", "svn": "new", "status": u"同步成功"}
    return {}

def sync_nlaPick(conn, logger):
    nla_pick = "/Application/nla/NLA_Pick"
    if not conn.has_path(nla_pick):
        logger.debug("Device %s need sync nlapick app" %(conn._host,))
        conn.put("./packages/NLA_Pick.tgz", "/Application/nla/NLA_Pick.tgz")
        conn.execute("cd /Application/nla; tar zxf NLA_Pick.tgz")
        conn.execute("chown -R hadoop:fromcf /Application/nla/NLA_Pick")

        if not conn.has_path(nla_pick):
            return {"fname": "nlapick", "local": "none", "svn": "new", "status": u"同步失败"}
        else:
            return {"fname": "nlapick", "local": "new", "svn": "new", "status": u"同步成功"}
    return {}

class NLAHadoopSync(threading.Thread):
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
                    syncInitAppEnv = sync_initAppEnv(conn, self.logger)
                    if syncInitAppEnv:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncInitAppEnv)

                    syncJava = sync_java(conn, self.logger)
                    if syncJava:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncJava)

                    syncHadoop = sync_hadoop(conn, self.logger)
                    if syncHadoop:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncHadoop)

                    syncLzop = sync_lzop(conn, self.logger)
                    if syncLzop:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncLzop)

                    syncHdfsClient = sync_hdfsClient(conn, self.logger)
                    if syncHdfsClient:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncHdfsClient)

                    syncNlaPick = sync_nlaPick(conn, self.logger)
                    if syncNlaPick:
                        if not result.has_key(device.hostname):
                            result[device.hostname] = []
                        result[device.hostname].append(syncNlaPick)

                    sync_crond(conn, self.logger)

                    for check in self.checks:
                        syncFile = sync_file(conn, check, self.logger)
                        if syncFile:
                            if not result.has_key(device.hostname):
                                result[device.hostname] = []
                            result[device.hostname].append(syncFile)

                    self.logger.debug("Check nla hadoop on device %s complete." %(device.ip,))
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
    logger = logging.getLogger("hadoop")
    try:
        check_run_pid("nlahadoop_sync.py", logger)
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
            {"fname": "NLA_Pick.jar", "svn": get_md5("packages/NLA_Pick/NLA_Pick.jar"), "local": "packages/NLA_Pick/NLA_Pick.jar", "remote": "/Application/nla/NLA_Pick/NLA_Pick.jar"},
            {"fname": "startup.sh", "svn": get_md5("packages/NLA_Pick/startup.sh"), "local": "packages/NLA_Pick/startup.sh", "remote": "/Application/nla/NLA_Pick/startup.sh"},
            {"fname": "system.properties", "svn": get_md5("packages/NLA_Pick/conf/system.properties"), "local": "packages/NLA_Pick/conf/system.properties", "remote": "/Application/nla/NLA_Pick/conf/system.properties"},
            {"fname": "spring-pick.xml", "svn": get_md5("packages/NLA_Pick/conf/spring-pick.xml"), "local": "packages/NLA_Pick/conf/spring-pick.xml", "remote": "/Application/nla/NLA_Pick/conf/spring-pick.xml"},
            {"fname": "log4j.properties", "svn": get_md5("packages/NLA_Pick/conf/log4j.properties"), "local": "packages/NLA_Pick/conf/log4j.properties", "remote": "/Application/nla/NLA_Pick/conf/log4j.properties"},
            {"fname": "HDFS_Client.jar", "svn": get_md5("packages/HDFS_Client/HDFS_Client.jar"), "local": "packages/HDFS_Client/HDFS_Client.jar", "remote": "/Application/nla/HDFS_Client/HDFS_Client.jar"},
            {"fname": "startup.sh", "svn": get_md5("packages/HDFS_Client/startup.sh"), "local": "packages/HDFS_Client/startup.sh", "remote": "/Application/nla/HDFS_Client/startup.sh"},
            {"fname": "channels.txt", "svn": get_md5("packages/NLA_Pick/conf/channels.txt"), "local": "packages/NLA_Pick/conf/channels.txt", "remote": "/Application/nla/NLA_Pick/conf/channels.txt"},
        ]
        for i in range(8):
            n = NLAHadoopSync(logger, q, checks)
            n.setDaemon(True)
            n.start()

        time.sleep(3)
        q.join()

        logger.debug("%s" %(result,))
        if result:
            sm = SendMail("zhigang.li@chinacache.com", "zhigang.li@chinacache.com,gen.li@chinacache.com,bo.chen@chinacache.com,peng.xu@chinacache.com,yue.zhang@chinacache.com", u"NLA hadoop同步检查", result)
            sm.sendmail()
            logger.debug("Send mail.")
    except Exception, e:
        logger.error(e)