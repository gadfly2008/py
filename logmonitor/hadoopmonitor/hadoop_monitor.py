#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config
import os
import sys
import urllib
import urllib2
import json
import subprocess
import socket
from datetime import datetime

class TotalInfo(object):
    def __init__(self):
        pass

    def _set_configuredcapacity(self, value):
        self._configuredcapacity = value
    def _get_configuredcapacity(self):
        return self._configuredcapacity

    def _set_presentcapacity(self, value):
        self._presentcapacity = value
    def _get_presentcapacity(self):
        return self._presentcapacity

    def _set_dfsremaining(self, value):
        self._dfsremaining = value
    def _get_dfsremaining(self):
        return self._dfsremaining
    
    def _set_dfsused(self, value):
        self._dfsused = value
    def _get_dfsused(self):
        return self._dfsused

    def _set_dfsusedper(self, value):
        self._dfsusedper = value
    def _get_dfsusedper(self):
        return self._dfsusedper

    def _set_totaldatanode(self, value):
        self._totaldatanode = value
    def _get_totaldatanode(self):
        return self._totaldatanode

    def _set_deaddatanode(self, value):
        self._deaddatanode = value
    def _get_deaddatanode(self):
        return self._deaddatanode

    configuredcapacity = property(_get_configuredcapacity, _set_configuredcapacity)
    presentcapacity = property(_get_presentcapacity, _set_presentcapacity)
    dfsremaining = property(_get_dfsremaining, _set_dfsremaining)
    dfsused = property(_get_dfsused, _set_dfsused)
    dfsusedper = property(_get_dfsusedper, _set_dfsusedper)
    totaldatanode = property(_get_totaldatanode, _set_totaldatanode)
    deaddatanode = property(_get_deaddatanode, _set_deaddatanode)

class DeviceInfo(object):
    def __init__(self):
        pass

    def _set_name(self, value):
        self._name = value
    def _get_name(self):
        return self._name

    def _set_decommissionstatus(self, value):
        self._decommissionstatus = value
    def _get_decommissionstatus(self):
        return self._decommissionstatus

    def _set_configuredcapacity(self, value):
        self._configuredcapacity = value
    def _get_configuredcapacity(self):
        return self._configuredcapacity

    def _set_dfsremaining(self, value):
        self._dfsremaining = value
    def _get_dfsremaining(self):
        return self._dfsremaining

    def _set_dfsused(self, value):
        self._dfsused = value
    def _get_dfsused(self):
        return self._dfsused

    def _set_dfsusedper(self, value):
        self._dfsusedper = value
    def _get_dfsusedper(self):
        return self._dfsusedper

    def _set_nondfsused(self, value):
        self._nondfsused = value
    def _get_nondfsused(self):
        return self._nondfsused

    def _set_dfsremainingper(self, value):
        self._dfsremainingper = value
    def _get_dfsremainingper(self):
        return self._dfsremainingper

    def _set_lastcontact(self, value):
        self._lastcontact = value
    def _get_lastcontact(self):
        return self._lastcontact

    name = property(_get_name, _set_name)
    decommissionstatus = property(_get_decommissionstatus, _set_decommissionstatus)
    configuredcapacity = property(_get_configuredcapacity, _set_configuredcapacity)
    dfsremaining = property(_get_dfsremaining, _set_dfsremaining)
    dfsused = property(_get_dfsused, _set_dfsused)
    dfsusedper = property(_get_dfsusedper, _set_dfsusedper)
    nondfsused = property(_get_nondfsused, _set_nondfsused)
    dfsremainingper = property(_get_dfsremainingper, _set_dfsremainingper)
    lastcontact = property(_get_lastcontact, _set_lastcontact)

def check_run_pid(logger, app):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.debug("App has already run, exit at %s" %(datetime.today()))
        sys.exit()
    else:
       logger.debug("Begin to start %s in %s" %(app, datetime.today()))

def get_total_info(obj, line):
    if line.startswith("Configured Capacity"):
        obj.configuredcapacity = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("Present Capacity"):
        obj.presentcapacity = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("DFS Remaining"):
        obj.dfsremaining = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("DFS Used:"):
        obj.dfsused = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("DFS Used%s:" %("%")):
        obj.dfsusedper = line.split(":")[1].strip().split("%")[0].strip()
    elif line.startswith("Datanodes"):
        obj.totaldatanode = line.split("(")[1].strip().split(",")[0].strip().split()[0].strip()
        obj.deaddatanode = line.split("(")[1].strip().split(",")[1].strip().split()[0].strip()

def get_device_info(obj, line):
    if line.startswith("Name:"):
        obj.name = socket.gethostbyaddr(line.split(":")[1].strip())[0]
    elif line.startswith("Decommission Status"):
        obj.decommissionstatus = line.split(":")[1].strip()
    elif line.startswith("Configured Capacity"):
        obj.configuredcapacity = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("Non DFS Used"):
        obj.nondfsused = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("DFS Remaining:"):
        obj.dfsremaining = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("DFS Used:"):
        obj.dfsused = line.split(":")[1].strip().split("(")[0].strip()
    elif line.startswith("DFS Used%s:" %("%", )):
        obj.dfsusedper = line.split(":")[1].strip().split("%")[0].strip()
    elif line.startswith("DFS Remaining%s:" %("%", )):
        obj.dfsremainingper = line.split(":")[1].strip().split("%")[0].strip()
    elif line.startswith("Last contact"):
        obj.lastcontact = datetime.strptime(line.split("Last contact:")[1].strip(), "%a %b %d %H:%M:%S %Z %Y")

def post_namenode_info(total_info, logger):
    api = "http://logmonitor.chinacache.net:8888/hadoop/monitor/namenode/add/"
    try:
        args = {
                "configuredcapacity": total_info.configuredcapacity,
                "presentcapacity": total_info.presentcapacity,
                "dfsremaining": total_info.dfsremaining,
                "dfsused": total_info.dfsused,
                "dfsusedper": total_info.dfsusedper,
                "totaldatanode": total_info.totaldatanode,
                "deaddatanode": total_info.deaddatanode,
        }
        res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)

def post_datanode_info(devices, logger):
    api = "http://logmonitor.chinacache.net:8888/hadoop/monitor/datanode/add/"
    args = []
    for device in devices:
        args.append({
            "name": device.name,
            "decommissionstatus": device.decommissionstatus,
            "configuredcapacity": device.configuredcapacity,
            "nondfsused": device.nondfsused,
            "dfsremaining": device.dfsremaining,
            "dfsused": device.dfsused,
            "dfsusedper": device.dfsusedper,
            "dfsremainingper": device.dfsremainingper,
            "lastcontact": device.lastcontact.strftime("%Y-%m-%d %H:%M:%S"),
        })
    try:
        res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)

def message_sender(content, logger):
    api = "http://logmonitor.chinacache.net:8888/mobile/"
    content = u"\n".join(content.values())

    phonenums = "13910840138;13488770992;13910001730;13801289719"
    try:
        res = urllib2.urlopen(api, urllib.urlencode({"content": content.encode("utf-8"), "phonenum": phonenums})).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("monitor")
    try:
        check_run_pid(logger, "hadoop_monitor.py")

        total_info = TotalInfo()
        total_info_end = False
        devices = []
        device_end = False

        p = subprocess.Popen("hadoop dfsadmin -report", shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        if p.returncode:
            logger.error("Error %s" %(stderrdata,))
        else:
            for line in stdoutdata.split("\n"):
                line = line.strip()
                if line:
                    if not total_info_end:
                        get_total_info(total_info, line)
                    else:
                        if line.startswith("Name:"):
                            devices.append(DeviceInfo())
                        get_device_info(devices[-1], line)
                    if line.startswith("Datanodes"):
                        total_info_end = True

        content = {}
        for device in devices:
            if not int(device.configuredcapacity):
                content[device.name] = u"设备[%s]宕机" %(device.name, )
            elif float(device.dfsusedper) > 80.0:
                content[device.name] = u"设备[%s]磁盘使用率大于80%s" %(device.name, "%")
        if content:
            message_sender(content, logger)

        post_namenode_info(total_info, logger)
        post_datanode_info(devices, logger)
    except Exception, e:
        logger.error(e)