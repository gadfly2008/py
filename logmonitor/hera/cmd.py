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

class Cmd(threading.Thread):
    def __init__(self, logger, queue, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.q = queue
        self.logger = logger
        
    def run(self):
        global success, fail, singlelock
        while True:
            if self.q.empty():
                break
            device = self.q.get()
            key = "%s: (%s)" %(device.hostname, device.ip)
            self.logger.debug("Do in %s" %(device.hostname,))
            try:
                conn = Connection(device.ip, int(device.port), device.user, device.password)
                try:
                    r = conn.execute(self.cmd)

                    if r.get("status") == "error":
                        singlelock.acquire()
                        fail[key] = r.get("output")
                        singlelock.release()
                    else:
                        singlelock.acquire()
                        success[key] = r.get("output")
                        singlelock.release()
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
        parser.add_option("-c", "--cmd", dest="cmd", help="shell commands")
        parser.add_option("-d", "--devices", dest="devices", help="devices list")
        parser.add_option("--nla", dest="nla", help="nla name, such as CNC-BJ-1-111;BGP-JN-2-222")
        (options, args) = parser.parse_args()
        
        if not options.cmd:
            parser.print_help()
            sys.exit(2)
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
            c = Cmd(logger, q, options.cmd)
            c.setDaemon(True)
            c.start()
        
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