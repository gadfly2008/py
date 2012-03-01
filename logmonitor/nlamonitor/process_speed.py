#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config
import ConfigParser
import socket
from datetime import datetime
from controller import get_process_speed, check_run_pid, update_data

def process_monitor(logger, hostname, dtime):
    speed = get_process_speed(logger)
    size = speed.split("size")[1].split()[0].split("[")[1]
    count = speed.split("count")[1].split()[0].split("[")[1].split("]")[0]
    use_time = speed.split("time")[1].split()[0].split("[")[1]

    logger.debug("Get process speed complete.")
    return {"size": size, "count": count, "use_time": use_time, "hostname": hostname, "datetime": dtime}

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging.conf")
    logger = logging.getLogger("nlamonitor")
    try:
        check_run_pid("process_speed.py", logger)
        cp = ConfigParser.ConfigParser()
        cp.read("conf/app.cfg")
        api = cp.get("main", "api").strip()

        hostname = socket.gethostname()
        dtime = datetime.now().strftime("%Y-%m-%d %H:%M")

        process = process_monitor(logger, hostname, dtime)

        logger.debug("Begin to update data.")
        update_data(logger, api, {"process": process})

    except Exception, e:
        logger.error(e)