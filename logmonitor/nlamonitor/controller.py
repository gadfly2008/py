#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import json
import urllib2
import urllib
import sys
import subprocess
from datetime import datetime

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app, ))
    if len(res.readlines()) > 2:
        logger.debug("App has already run, kill it.")
        cmd= "ps aux | grep -v grep | grep \'%s\' | awk \'{print $2}\' | xargs kill -9" %(app, )
        p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
        if p.returncode:
            logger.error("Kill app failed, exists app. return code is %s" %(p.returncode, ))
            sys.exit()

        logger.info("kill app success, new app run at %s" %(datetime.today()))
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

def update_data(logger, api, args):
    try:
        res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)}), 60).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)

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

def get_systemload(logger):
    result = {"load_user": "0", "load_average": "0"}
    load_user = "uptime | gawk -F \',\' \'{print $3}\' | gawk \'{print $1}\'"
    p = subprocess.Popen(load_user, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get system load_user error %s" %(stderrdata,))
    else:
        result["load_user"] = stdoutdata.split("\n")[0]

    load_average = "uptime | gawk -F \',\' \'{print $4}\' | gawk -F \':\' \'{print $2}\' | gawk \'{print $1}\'"
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

def get_io_await(logger, block="b"):
    cmd = "iostat -d -x 1 2 | sed -n \'/[0-9]/p\' | sed -n \'/[%s]/p\'|sed -n \'2p\'| gawk \'{print $10}\'" %(block, )
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get io await error %s" %(stderrdata,))
        result = ""
    else:
        result = stdoutdata.split("\n")[0].strip()

    return result

def get_io_idle(logger, block="b"):
    cmd = "iostat -d -x 1 2 | sed -n \'/[0-9]/p\' | sed -n \'/[%s]/p\'|sed -n \'2p\'| gawk \'{print $12}\'" %(block, )
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get io idle error %s" %(stderrdata,))
        result = ""
    else:
        result = stdoutdata.split("\n")[0].strip()

    return result

def get_io(logger):
    result = {"io_await": "0.00", "io_idle": "0.00"}

    io_await = get_io_await(logger)
    if not io_await:
        io_await = get_io_await(logger, block="a")
    if io_await:
        result["io_await"] = io_await
        
    io_idle = get_io_idle(logger)
    if not io_idle:
        io_idle = get_io_idle(logger, block="a")
    if io_idle:
        result["io_idle"] = io_idle

    return result

def get_cpu_count(logger):
    cmd = "cat /proc/cpuinfo | grep process"
    count = 2
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get cpu count error %s" %(stderrdata,))
    else:
        count = len(stdoutdata.split("\n").pop())

    return count

def get_max_block(logger):
    cmd = "df | awk 'BEGIN{Max=0}{if (NR!=1) {sub(/%/,\"\",$5); Max=$5>Max?$5:Max}}END{print Max}'"
    count = 1
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get cpu count error %s" %(stderrdata,))
    else:
        count = int(stdoutdata.split("\n")[0])

    return count

def stop_vsftp():
    p = subprocess.Popen("/etc/init.d/vsftpd stop", shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

def get_vsftp_status():
    p = subprocess.Popen("/etc/init.d/vsftpd status", shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if stdoutdata.split("\n")[0].find("running") > 0:
        return "running"
    else:
        return "stop"

def start_vsftp():
    p = subprocess.Popen("/etc/init.d/vsftpd start", shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

def get_blocks(logger):
    cmd = "df | sed \'1d\' | gawk \'{print $5,$6}\'"
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get blocks info error %s" %(stderrdata,))
        return ""
    else:
        return stdoutdata.split("\n")

def get_process_speed(logger):
    cmd = "cat /Application/LogAnalysis/logs/core.log | grep 'src directory'| tail -n 1 | gawk -F \'<\' \'{print $2}\' | awk -F \'>\' \'{print $1}\'"
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Get process speed error %s" %(stderrdata,))
        return ""
    else:
        return stdoutdata.split("\n")[0]