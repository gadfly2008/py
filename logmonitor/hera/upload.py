#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import threading
import time
import sys
import logging
import logging.config
from Queue import Queue
from ssh import Connection
from device import get_devices, get_device_by_file, get_nlaDevices
from optparse import OptionParser

class Upload(threading.Thread):
    def __init__(self, logger, queue, package, path):
        threading.Thread.__init__(self)
        self.package = package
        self.path = path
        self.q = queue
        self.logger = logger
        
    def run(self):
        global success, fail, singlelock
        while True:
            if self.q.empty():
                break
            device = self.q.get()
            self.logger.debug("Do in %s" %(device.hostname,))
            key = "%s: (%s)" %(device.hostname, device.ip)
            try:
                conn = Connection(device.ip, int(device.port), device.user, device.password)
                try:
                    if not conn.has_path(self.path):
                        cmd = "mkdir -p %s" %(self.path,)
                        r = conn.execute(cmd)
                        if r.get("status") == "error":
                            conn.close()
                            time.sleep(2)
                            singlelock.acquire()
                            fail[key] = r.get("output")
                            singlelock.release()
                            self.q.task_done()
                    conn.put("./packages/%s" %(self.package,), "%s/%s" %(self.path, self.package))
                    self.logger.debug("Host %s execute seccusss." %(device.hostname,))
                except Exception, e:
                    self.logger.error("Hostname:%s Error:%s" %(device.hostname, e))
                    singlelock.acquire()
                    fail[key] = ["%s" %(e,)]
                    singlelock.release()
                finally:
                    conn.close()
                    time.sleep(2)
                    self.q.task_done()
            except Exception, e:
                self.logger.error(e)
                self.q.task_done()
            
if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("tool")
    try:
        usage = "Usage: %prog [options]"
        parser = OptionParser(usage=usage)
        parser.add_option("-f", "--file", dest="package", help="file needs to upload")
        parser.add_option("-p", "--path", dest="path", help="remote path, default is \'/root\'")
        parser.add_option("-d", "--devices", dest="devices", help="devices list")
        parser.add_option("--nla", dest="nla", help="nla name, such as CNC-BJ-1-111;BGP-JN-2-222")
        (options, args) = parser.parse_args()
        
        if not options.package:
            parser.print_help()
            sys.exit(2)
        if not options.path:
            path = "/root"
        else:
            path = options.path
        if options.nla:
            devices = get_nlaDevices(options.nla.strip())
        elif options.devices:
            devices = get_device_by_file(options.devices.strip())
        else:
            devices = get_devices("http://rcmsapi.chinacache.com:36000/app/name/NLA/OPEN/devices")
        
        logger.debug("There are %s devices." %(len(devices)))
        q = Queue()
    
        global success, fail, singlelock
        singlelock = threading.Lock()
        success = {}
        fail = {}
        for d in devices:
            q.put(d)
    
        for i in range(16):
            u = Upload(logger, q, options.package, path)
            u.setDaemon(True)
            u.start()
        
        time.sleep(3)
        q.join()
        
        f = open("result/success.txt", "w")
        for key,value in success.items():
            f.write("%s\n" %(key,))
            for each in value:
                f.write("\t%s\n" %(each.strip()))
        f.close()
        f = open("result/fail.txt", "w")
        for key,value in fail.items():
            f.write("%s\n" %(key,))
            for each in value:
                f.write("\t%s\n" %(each.strip()))
        f.close()
    except Exception, e:
        logger.error(e)