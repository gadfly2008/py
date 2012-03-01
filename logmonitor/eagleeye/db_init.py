#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from pymongo import Connection
from pymongo import ASCENDING, DESCENDING
from datetime import datetime, timedelta

if __name__ == "__main__":
    conn = Connection()
    db = conn["eagleeye"]

    start = datetime.strptime("20111201", "%Y%m%d")

    for i in range(180):
        c = db["nla_process_%s" %((start+timedelta(days=i)).strftime("%Y%m%d"))]
        c.ensure_index([("hostname", ASCENDING)])
        #c.drop_index("datetime_1_hostname_1")