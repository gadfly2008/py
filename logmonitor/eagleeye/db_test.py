#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import time
from datetime import datetime, timedelta
from pymongo import Connection

def init_data():
    mysql_conn = MySQLdb.connect(host="127.0.0.1", db="eagleeye", charset="utf8")
    mongo_conn = Connection()
    mongo_db = mongo_conn.dbtest

    try:
        mysql_cursor = mysql_conn.cursor()
        db_results_dict = {}
        db_results_list = {}
        try:
            mysql_cursor.execute("""select * from nla_channelnla""")

            print "Get mysql data"
            for each in mysql_cursor.fetchall():
                try:
                    mongo_db.db_normal.insert({"channelId": each[1], "userId": each[2], "datetime": each[4],
                                               "nlasn": each[3], "size": each[5], "output_count": each[6], "upload_count": each[7]
                                               })

                    key = "%s_%s" %(each[1], each[4])
                    if not db_results_dict.has_key(key):
                        db_results_dict[key] = {"channelId": each[1], "userId": each[2], "datetime": each[4], "nlas": {}}
                    if not db_results_list.has_key(key):
                        db_results_list[key] = {"channelId": each[1], "userId": each[2], "datetime": each[4], "nlas": []}

                    db_results_dict[key]["nlas"][each[3]] = {"size": each[5], "output_count": 0 if not each[6] else each[6], "upload_count": 0 if not each[7] else each[7]}
                    db_results_list[key]["nlas"].append({"deviceSn": each[3], "size": each[5], "output_count": 0 if not each[6] else each[6], "upload_count": 0 if not each[7] else each[7]})
                except Exception, e:
                    print "%s %s" %(e, each)

            print "Insert into dict data"
            for key, value in db_results_dict.items():
                try:
                    mongo_db.db_dict.insert(value)
                except Exception, e:
                    print "%s %s" %(e, key)

            print "Insert into list data"
            for key, value in db_results_list.items():
                try:
                    mongo_db.db_list.insert(value)
                except Exception, e:
                    print "%s %s" %(e, key)
        finally:
            mysql_cursor.close()
            mongo_conn.disconnect()
    except Exception, e:
        print e

def get_data(db):
    try:
        c = db.cursor()
        try:
            c.execute("""select * from nla_channelnla limit 10000""")

            return c.fetchall()
        finally:
            c.close()
    except Exception, e:
        print e

def update_mysql(db, data):
    try:
        c = db.cursor()
        try:
            for d in data:
                c.execute("""update nla_channelnla set size=size+%s where
                datetime=%s and channelId=%s and nlasn=%s""", (d[5], d[4], d[1], d[3]))
        finally:
            db.commit()
            c.close()
    except Exception, e:
        print e
        db.rollback()

def update_mongodb_normal(db, data):
    try:
        for d in data:
            db.db_normal.update({"channelId": d[1], "datetime": d[4], "nlasn": d[3]}, {"$inc": {"size": d[5]}}, upsert=True)
    except Exception, e:
        print e

def update_mongodb_dict(db, data):
    try:
        for d in data:
            db.db_dict.update({"channelId": d[1], "datetime": d[4]}, {"$inc": {"nlas.%s.size" %(d[3], ): d[5]}}, upsert=True)
    except Exception, e:
        print e

def update_mongodb_list(db, data):
    try:
        for d in data:
            db.db_list.update({"channelId": d[1], "datetime": d[4], "nlas.deviceSn": d[5]}, {"$inc": {"nlas.$.size": d[5]}}, upsert=True)
    except Exception, e:
        print e

def test_db_speed():
    mysql_conn = MySQLdb.connect(host="127.0.0.1", db="eagleeye", charset="utf8")
    print "Begin to get data"
    data = get_data(mysql_conn)
    print "End to get data"
    mongo_conn = Connection()
    mongo_db = mongo_conn.dbtest

    btime = time.time()
    print "Update mongodb normal begin at %s" %(btime, )
    update_mongodb_normal(mongo_db, data)
    etime = time.time()
    print "Update mongodb normal end at %s" %(etime, )
    print "Need %s" %(etime-btime)

    btime = time.time()
    print "Update mongodb dict begin at %s" %(btime, )
    update_mongodb_dict(mongo_db, data)
    etime = time.time()
    print "Update mongodb dict end at %s" %(etime, )
    print "Need %s" %(etime-btime)

    btime = time.time()
    print "Update mongodb list begin at %s" %(btime, )
    update_mongodb_list(mongo_db, data)
    etime = time.time()
    print "Update mongodb list end at %s" %(etime, )
    print "Need %s" %(etime-btime)

    btime = time.time()
    print "Update mysql begin at %s" %(btime, )
    update_mysql(mysql_conn, data)
    etime = time.time()
    print "Update mysql end at %s" %(etime, )
    print "Need %s" %(etime-btime)

def init_mongodb():
    db = Connection()["bermuda"]
    r_id = db.request.insert({"username": "163web", "created_time": datetime.now()-timedelta(days=1)})
    for i in range(10):
        db.url.insert({"r_id": r_id, "url": "http://www.163.com/%s.html" %(i, ), "status": "PROGRESS", "channel_code": 12231,
                       "created_time": datetime.now()-timedelta(days=1)})
        db.url.insert({"r_id": r_id, "url": "http://www.163.com/%s.html" %(i, ), "status": "PROGRESS", "channel_code": 12231,
                       "created_time": datetime.now()-timedelta(days=1)})

    r_id = db.request.insert({"username": "163web", "created_time": datetime.now()})
    for i in range(10):
        db.url.insert({"r_id": r_id, "url": "http://www.163.com/%s.html" %(i, ), "status": "PROGRESS", "channel_code": 12231,
                       "created_time": datetime.now()})
        db.url.insert({"r_id": r_id, "url": "http://www.163.com/%s.html" %(i, ), "status": "PROGRESS", "channel_code": 12231,
                       "created_time": datetime.now()})

    r_id = db.request.insert({"username": "163web", "created_time": datetime.now()+timedelta(days=1)})
    for i in range(10):
        db.url.insert({"r_id": r_id, "url": "http://www.163.com/%s.html" %(i, ), "status": "PROGRESS", "channel_code": 12231,
                       "created_time": datetime.now()+timedelta(days=1)})
        db.url.insert({"r_id": r_id, "url": "http://www.163.com/%s.html" %(i, ), "status": "PROGRESS", "channel_code": 12231,
                       "created_time": datetime.now()+timedelta(days=1)})

def insert_channel():
    mongodb = Connection()["eagleeye"]
    mysqldb = MySQLdb.connect(host="127.0.0.1",user="root", passwd="root", db="eagleeye", charset="utf8")
    mysql_cursor = mysqldb.cursor()
    mysql_cursor.execute("""select * from rcms_channel""")
    channels = mysql_cursor.fetchall()
    for channel in channels:
        mongodb.channel.insert({"customer": str(channel[1]), "name": channel[2], "channel_id": str(channel[3])})

    mysql_cursor.close()

if __name__ == "__main__":
    #init_data()
    #test_db_speed()
    #init_mongodb()
    insert_channel()