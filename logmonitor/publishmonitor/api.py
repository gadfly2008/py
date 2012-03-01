#!/usr/local/bin/ python
# -*- coding: utf-8 -*-

import os
os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"

def publish_by_channel(conn, channel, begin, end):
    try:
        cursor = conn.cursor()
        try:
            sql = "select sum(file_size) from logpub.pub_url where channel_id = :cid \
            and pub_date >= :b and pub_date < :e"
            cursor.execute(sql, cid=channel, b=begin, e=end)
            conn.commit()
            res = cursor.fetchone()[0]
            return int(res)
        finally:
            cursor.close()
    except Exception, e:
        print e
        return 0

def get_channelinfo(conn, channel):
    try:
       cursor = conn.cursor()
       try:
           sql = "select user_id, user_name, channel_name from logpub.pub_url where channel_id = :cid"
           cursor.execute(sql, cid=channel)
           conn.commit()
           res = cursor.fetchone()
           return "%s,%s,%s" %(res[0], res[1], res[2])
       finally:
           cursor.close()
    except Exception, e:
        return e

def get_channels(conn, begin, end):
    try:
       cursor = conn.cursor()
       try:
           sql = "select channel_id from logpub.pub_url where \
           pub_date >= :b and pub_date < :e group by channel_id"
           cursor.execute(sql, b=begin, e=end)
           conn.commit()
           res = cursor.fetchall()
           return [c[0] for c in res]
       finally:
           cursor.close()
    except Exception, e:
        return e

def get_total_publish(conn, source, begin, end):
    try:
        cursor = conn.cursor()
        try:
            sql = "select sum(file_size) from logpub.pub_url where \
            pub_date >= :b and pub_date < :e and \
            pub_url like 'http://storage-%s%s'" %(source, "%")
            cursor.execute(sql, b=begin, e=end)
            conn.commit()
            res = cursor.fetchone()[0]
            return int(res)
        finally:
            cursor.close()
    except Exception, e:
        print e
        return 0