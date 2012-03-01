#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
import time
import os
import sys
import logging
import logging.config
import ConfigParser
import threading
from Queue import Queue
from datetime import datetime, timedelta
from os.path import join, exists
from sendmail import SendMail

def parser_path(path):
    if path:
        if path.endswith("/") or path.endswith("\\"):
            path = path[0:-1]
    else:
        path = os.getcwd()
    return path

def parser_switch(switch):
    if switch:
        if switch == "true":
            return True
        elif switch == "false":
            return False
        else:
            return False
    else:
        return True

def get_log_urls(username, password, dt, logger):
    api = "http://logcenter.chinacache.com/URLGetter?username=%s&password=%s&date=%s" %(username, password, dt)
    try:
        opener = urllib2.urlopen(api)
        urls = opener.read().split()
        return urls
    except Exception, e:
        logger.error("Get urls failed with error %s, in %s" %(e, dt))
        return []

def parser_url(url):
    info = url.split("/")
    return {"area": info[3],"cid": info[5], "fname": info[-1]}

def get_abroad_fname(cid, dt, fname, fileNum):
    if len(fname.split("-")) > 2:
        ftype = fname.split("-")[0].split(".")[1].split("_")[0]
    else:
        ftype = fname.split(".")[0].split("_")[-1]
    if not fileNum.has_key(cid):
        fileNum[cid] = 0
    else:
        fileNum[cid] += 1
    return "%s_%s_%s_%s.gz" %(cid, dt, fileNum[cid], ftype)

def get_download_path(localpath):
    if not exists(localpath):
        os.makedirs(localpath)
    return localpath

class ParserCfg():
    def __init__(self):
        cp = ConfigParser.ConfigParser()
        cp.read(join(os.getcwd(), "conf", "main.cfg"))
        self.cp = cp
    def _get_username(self):
        return self.cp.get("auth", "username").strip()
    def _get_password(self):
        return self.cp.get("auth", "password").strip()
    def _get_threads(self):
        threads = self.cp.get("auth", "threads").strip()
        if not threads:
            return 5
        else:
            return int(threads)
    def _get_abroad_delayTime(self):
        delay_time = self.cp.get("delayTime", "abroadLogDelayTime").strip()
        return int(delay_time) if delay_time else 3
    def _get_mainland_delayTime(self):
        delay_time = self.cp.get("delayTime", "mainlandLogDelayTime").strip()
        return int(delay_time) if delay_time else 1
    def _get_abroad_downloadPath(self):
        path = self.cp.get("downloadPath", "abroadDownloadPath").strip()
        return parser_path(path)
    def _get_mainland_downloadPath(self):
        path = self.cp.get("downloadPath", "mainlandDownloadPath").strip()
        return parser_path(path)
    def _get_needDownload_abroad(self):
        switch = self.cp.get("downloadSwitch", "downloadAbroad").strip()
        return parser_switch(switch)
    def _get_needDownload_mainland(self):
        switch = self.cp.get("downloadSwitch", "downloadMainland").strip()
        return parser_switch(switch)

    name = property(_get_username)
    password = property(_get_password)
    threads = property(_get_threads)
    abroadDelayTime = property(_get_abroad_delayTime)
    mainlandDelayTime = property(_get_mainland_delayTime)
    abroadDownloadPath = property(_get_abroad_downloadPath)
    mainlandDownloadPath = property(_get_mainland_downloadPath)
    needDownloadAbroad = property(_get_needDownload_abroad)
    needDownloadMainland = property(_get_needDownload_mainland)

class DownloadClient(threading.Thread):
    def __init__(self, queue, logger, isRetry=False):
        threading.Thread.__init__(self)
        self.q = queue
        self.logger = logger
        self.isRetry = isRetry

    def run(self):
        global failedQueue
        while True:
            if self.q.empty():
                break
            task = self.q.get()
            try:
                opener = urllib2.urlopen(task["url"], timeout=60)
                f = open(join(task["path"], "%s.bak" %(task["fname"])), "wb")
                try:
                    begin = time.time()
                    while True:
                        content = opener.read(1024*1024)
                        if content == "":
                            break
                        f.write(content)
                    f.close()
                    if exists(join(task["path"], task["fname"])):
                        os.remove(join(task["path"], task["fname"]))
                    os.rename(join(task["path"], "%s.bak" %(task["fname"])), join(task["path"], task["fname"]))
                    end = time.time()
                    if self.isRetry:
                        self.logger.debug("Retried to download file %s, used %.2fs" %(task["url"], float(end - begin)))
                    else:
                        self.logger.debug("Finished to download file %s, used %.2fs" %(task["url"], float(end - begin)))
                finally:
                    f.close()
            except Exception, e:
                failedQueue.append(task)
                if self.isRetry:
                    sendMail = SendMail(u"重试下载日志文件 %s 出错, 请检查, 出错信息: %s" %(task["url"], e))
                else:
                    sendMail = SendMail(u"下载日志文件 %s 出错, 正在重试下载, 出错信息: %s" %(task["url"], e))
                sendMail.send_with_normal()
                self.logger.error("Download file %s failed with error %s" %(task["url"], e))
            finally:
                time.sleep(2)
                self.q.task_done()

if __name__ == "__main__":
    logging.config.fileConfig(join(os.getcwd(), "conf", "logging.conf"))
    logger = logging.getLogger("dl_client")
    try:
        print "App begin..."
        cfg = ParserCfg()
        fileNum = {}
        if not cfg.name or not cfg.password:
            logger.error("Username or password cannot be empty. Set them in conf/main.cfg file!")
            print "Username or password cannot be empty. Set them in conf/main.cfg file!"
            sys.exit(1)

        logger.debug("App process begin at %s" %(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        begin = time.time()
        global failedQueue
        failedQueue = []
        queue = Queue()
        if cfg.needDownloadMainland:
            count = 0
            dt = (datetime.today() - timedelta(days=cfg.mainlandDelayTime)).strftime("%Y%m%d")
            urls = get_log_urls(cfg.name, cfg.password, dt, logger)
            for url in urls:
                try:
                    info = parser_url(url)
                    if info["area"] == "ftpDown":
                        download_path = get_download_path(join(cfg.mainlandDownloadPath, info["cid"], dt[0:-2]))
                        queue.put({"url": url, "path": download_path, "fname": info["fname"]})
                        count += 1
                except Exception, e:
                    logger.error("Parser url: %s error: %s" %(url, e))

            print "Need to download %s mainland log" %(count,)
            
        if cfg.needDownloadAbroad:
            count = 0
            dt = (datetime.today() - timedelta(days=cfg.abroadDelayTime)).strftime("%Y%m%d")
            urls = get_log_urls(cfg.name, cfg.password, dt, logger)
            for url in urls:
                try:
                    info = parser_url(url)
                    if info["area"] != "ftpDown":
                        fname = get_abroad_fname(info["cid"], dt, info["fname"], fileNum)
                        download_path = get_download_path(join(cfg.abroadDownloadPath, info["cid"], dt[0:-2]))
                        queue.put({"url": url, "path": download_path, "fname": fname})
                        count += 1
                except Exception, e:
                    logger.error("Parser url: %s error: %s" %(url, e))

            print "Need to download %s abroad log" %(count,)

        for i in range(cfg.threads):
            t = DownloadClient(queue, logger)
            t.setDaemon(True)
            t.start()
        time.sleep(2)
        queue.join()

        if failedQueue:
            fq = Queue()
            for t in failedQueue:
                fq.put(t)

            for i in range(cfg.threads):
                t = DownloadClient(fq, logger, isRetry=True)
                t.setDaemon(True)
                t.start()
            time.sleep(2)
            fq.join()

        end = time.time()
        logger.debug("App process complete, used %.2fs" %(end - begin))

        sendMail = SendMail("%s\n\n" %(datetime.today().strftime("%Y-%m-%d")))
        sendMail.send_with_attachment()
    except Exception, e:
        logger.error(e)