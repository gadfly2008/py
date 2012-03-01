#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config
import ConfigParser
import socket
import os
from datetime import datetime
from os.path import exists
from controller import get_systemload, get_cpu, get_memory, get_io, check_run_pid, update_data

def update_cache(logger, cfile, data):
    try:
        f = open(cfile, "a")
        try:
            s = ""
            for key, value in data.items():
                s += "%s=%s|" %(key, value)

            f.write(s)
            f.write("\n")
        finally:
            f.close()
    except Exception, e:
        logger.error(e)

def performance_monitor(logger, hostname, dtime):
    systemload = get_systemload(logger)
    cpu = get_cpu(logger)
    memory = get_memory(logger)
    io = get_io(logger)
    
    param = dict(systemload.items()+cpu.items()+memory.items()+io.items())
    param["hostname"] = hostname
    param["datetime"] = dtime

    logger.debug("Get perfromance complete.")
    return {"performance": param}

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("nlamonitor")
    try:
        check_run_pid("performance.py", logger)
        cp = ConfigParser.ConfigParser()
        cp.read("conf/app.cfg")
        api = cp.get("main", "api").strip()
        dtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        cfile = "cache.txt"

        if exists(cfile) and len(open(cfile).readlines()) >= 10:
            data = []
            for each in open(cfile).readlines():
                temp = {}
                for kv in each.split("|"):
                    if kv.strip():
                        key, value = kv.strip().split("=")
                        temp[key] = value
                data.append(temp)

            logger.debug("Begin to update data.")
            update_data(logger, api, {"performance": data})

            logger.debug("Remove cache file.")
            os.remove(cfile)
        
        performances = performance_monitor(logger, socket.gethostname(), dtime)
        update_cache(logger, cfile, performances["performance"])

    except Exception, e:
        logger.error(e)