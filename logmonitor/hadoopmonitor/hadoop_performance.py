#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
import socket
import subprocess
import os
import sys
import logging
import logging.config
import urllib
import urllib2

def get_systemload(logger):
    result = {"load_user": "0", "load_average": "0"}
    load_user = "uptime | gawk -F \',\' \'{print $3}\' | gawk \'{print $1}\'"
    p = subprocess.Popen(load_user, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get system load_user error %s" %(stderrdata,))
    else:
        result["load_user"] = stdoutdata.split("\n")[0]

    load_average = "uptime | gawk -F \',\' \'{print $5}\' | gawk \'{print $1}\'"
    p = subprocess.Popen(load_average, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get system load_average error %s" %(stderrdata, ))
    else:
        result["load_average"] = stdoutdata.split("\n")[0]

    return result

def get_cpu(logger):
    result = {"cpu_us": "0", "cpu_idle": "0"}
    cpu_us = "vmstat 1 2| sed -n \'/[0-9]/p\' | sed -n \'2p\' | gawk \'{print $13}\'"
    p = subprocess.Popen(cpu_us, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get cpu use error %s" %(stderrdata,))
    else:
        result["cpu_us"] = stdoutdata.split("\n")[0]

    cpu_idle = "vmstat 1 2| sed -n \'/[0-9]/p\' | sed -n \'2p\' | gawk \'{print $15}\'"
    p = subprocess.Popen(cpu_idle, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get cpu idle error %s" %(stderrdata,))
    else:
        result["cpu_idle"] = stdoutdata.split("\n")[0]

    return result

def get_memory(logger):
    result = {"memory_free": "0"}
    memory_free = "vmstat 1 2| sed -n \'/[0-9]/p\' | sed -n \'2p\' | gawk \'{print $4}\'"
    p = subprocess.Popen(memory_free, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get memory free error %s" %(stderrdata,))
    else:
        result["memory_free"] = stdoutdata.split("\n")[0]

    return result

def get_io(logger):
    result = {"io_await": "0.00", "io_idle": "0.00"}
    io_await = "iostat -d -x 1 2 | sed -n \'/[0-9]/p\' | sed -n \'/[b]/p\'|sed -n \'2p\'| gawk \'{print $10}\'"
    p = subprocess.Popen(io_await, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get io await error %s" %(stderrdata,))
    else:
        result["io_await"] = stdoutdata.split("\n")[0]
        if not result["io_await"].strip():
            result["io_await"] = "0.00"

    io_idle = "iostat -d -x 1 2 | sed -n \'/[0-9]/p\' | sed -n \'/[b]/p\'|sed -n \'2p\'| gawk \'{print $12}\'"
    p = subprocess.Popen(io_idle, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get io idle error %s" %(stderrdata,))
    else:
        result["io_idle"] = stdoutdata.split("\n")[0]
        if not result["io_idle"].strip():
            result["io_idle"] = "0.00"

    return result

def performance_monitor(logger, hostname, dtime):
    systemload = get_systemload(logger)
    cpu = get_cpu(logger)
    memory = get_memory(logger)
    io = get_io(logger)

    param = dict(systemload.items()+cpu.items()+memory.items()+io.items())
    param["hostname"] = hostname
    param["datetime"] = dtime

    logger.debug("Get perfromance complete.")
    return param

def check_run_pid(logger, app):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.debug("App has already run, exit at %s" %(datetime.today()))
        sys.exit()
    else:
       logger.debug("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("monitor")
    try:
        check_run_pid(logger, "hadoop_performance.py")
        api = "http://logmonitor.chinacache.net:8888/hadoop/monitor/datanode/performance/add/"

        data = performance_monitor(logger, socket.gethostname(), datetime.now().strftime("%Y-%m-%d %H:%M"))

        try:
            res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)}), 60).read()
            logger.debug(res)
        except Exception, e:
            logger.error(e)
    except Exception, e:
        logger.error(e)