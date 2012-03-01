#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from api import get_total_publish
from datetime import datetime, date, timedelta
import cx_Oracle
import os
import sys
import logging
import logging.config
import ConfigParser
import urllib
import urllib2
import json
os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"

DATETYPE = "%Y%m%d"
    
def get_today(datestr=None):
    if datestr:
        today = datestr
    else:
        today = date.today().strftime(DATETYPE)
    return datetime.strptime(today, DATETYPE)

def update_data(logger, args, api):
    try:
        res = urllib2.urlopen(api, urllib.urlencode({"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})).read()
        logger.debug(res)
    except Exception, e:
        logger.error(e)

def check_run_pid(app, logger):
    res = os.popen("ps aux | grep -v grep| grep \'%s\'" %(app,))
    if len(res.readlines()) > 2:
        logger.info("%s has already run, exit at %s" %(app, datetime.today()))
        sys.exit()
    else:
        logger.info("Begin to start %s in %s" %(app, datetime.today()))

if __name__ == "__main__":
    logging.config.fileConfig("conf/logging_total.conf")
    logger = logging.getLogger("totalmonitor")
    try:
        check_run_pid("publishtotal.py", logger)
        cfp = ConfigParser.ConfigParser()
        cfp.read("conf/app.cfg")
        
        a_dhost = cfp.get("active_db", "host").strip()
        a_duser = cfp.get("active_db", "username").strip()
        a_dpassword = cfp.get("active_db", "password").strip()
        s_dhost = cfp.get("standby_db", "host").strip()
        s_duser = cfp.get("standby_db", "username").strip()
        s_dpassword = cfp.get("standby_db", "password").strip()

        aconn = cx_Oracle.connect(a_duser, a_dpassword, cx_Oracle.makedsn(a_dhost, 1521, "logpub"))
        sconn = cx_Oracle.connect(s_duser, s_dpassword, cx_Oracle.makedsn(s_dhost, 1521, "logpub"))
        
        api = cfp.get("main", "api_total").strip()
        if len(sys.argv) > 1:
            begin = get_today(sys.argv[1]) - timedelta(days=1)
        else:
            begin = get_today() - timedelta(days=1)
        end = begin + timedelta(days=1)

        args = []
        for i in range(4):
            try:
                current_begin = begin - timedelta(days=i)
                current_end = end - timedelta(days=i)
                
                total = get_total_publish(sconn, "1", current_begin, current_end)
                logger.debug("Storage-1 %s size %s" %(current_begin, total))
                args.append({"today": current_begin.strftime(DATETYPE), "size": total, "source": "storage-1"})
            
                total = get_total_publish(sconn, "2", current_begin, current_end)
                logger.debug("Storage-2 %s size %s" %(current_begin, total))
                args.append({"today": current_begin.strftime(DATETYPE), "size": total, "source": "storage-2"})
            
                total = get_total_publish(aconn, "3", current_begin, current_end)
                logger.debug("Storage-3 %s size %s" %(current_begin, total))
                args.append({"today": current_begin.strftime(DATETYPE), "size": total, "source": "storage-3"})
            except Exception, e:
                logger.error(e)
        aconn.close()
        sconn.close()
        update_data(logger, args, api)
    except Exception, e:
        logger.error(e)