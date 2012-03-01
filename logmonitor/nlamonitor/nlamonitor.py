#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config
import ConfigParser
import socket
import time
import random
from dir import dir_monitor
from block import block_monitor
from datetime import datetime
from controller import get_cpu_count, get_vsftp_status, get_max_block, stop_vsftp, check_run_pid, get_systemload, update_data

def get_nla_health(logger, block_names, isTempWarning):
    ftp_status = get_vsftp_status()
    load = float(get_systemload(logger)["load_average"])
    if isTempWarning:
        return 0
    elif ftp_status == "running" and get_max_block(logger) > 90:
        stop_vsftp()
        return 0
    elif ftp_status == "running":
        for block_name in block_names:
            try:
                open("%s/test.txt" %(block_name,), "w")
            except Exception, e:
                logger.error("Error in block %s" %(e,))
                stop_vsftp()
                return 0

        cpu_count = get_cpu_count(logger)
        if cpu_count == 1:
            max = 50
        else:
            max = 100
        if load > 0.00 and load <= 3.00:
            return max*1
        elif load > 3.00 and load <=8.00:
            return int(max*0.5)
        else:
            return 0
    else:
        return 0

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("nlamonitor")
    try:
        check_run_pid("nlamonitor.py", logger)
        cp = ConfigParser.ConfigParser()
        cp.read("conf/app.cfg")
        api = cp.get("main", "api").strip()

        hostname = socket.gethostname()
        dtime = datetime.now().strftime("%Y-%m-%d %H:%M")

        dirs = dir_monitor(logger, hostname, cp.get("main", "dirs").strip(), cp, dtime)
        blocks = block_monitor(logger, hostname)

        health = get_nla_health(logger, blocks["names"], dirs["isTempWarning"])
        logger.debug("NLA health is %s." %(health,))
        f = open("/var/run/nla_health.conf", "w")
        f.write("health=%s\n" %(health,))
        f.close()

        vsftp_status = get_vsftp_status()
        dir_data = []
        for arg in dirs["dir"]:
            arg["vsftp"] = vsftp_status
            arg["health"] = health
            dir_data.append(arg)
        args = {"block": blocks["block"], "dir": dir_data,
                "masterdir": {"datetime": dtime, "size": dirs["masterdir"], "hostname": hostname}}
        
        time.sleep(random.randint(1, 60))
        logger.debug("Begin to update data.")
        update_data(logger, api, args)
        logger.debug("Update data complete.")

    except Exception, e:
        logger.error(e)