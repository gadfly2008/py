#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

VIPS = ["196", "384", "2230", "2247", "237", "781", "2712", "618", "2112", "114", "2985", 
"238", "701", "738", "2039", "2324", "295", "210", "867", "3300"]

SOURCE = {"storage-0": u"特殊发布", "storage-1": u"济南", "storage-2": u"兆维", "storage-3": u"上地"}
   
def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d")
    
def string_toDatetime(string):
    return datetime.strptime(string, "%Y-%m-%d")

def data_format(data):
    KB = 1024
    MB = 1024*1024
    GB = 1024*1024*1024
    TB = 1024*1024*1024*1024

    if not data:
        return "0"
    if data < KB:
        return "%s" %(data, )
    elif float(data)/KB < KB:
        return "%.2f %s" %(float(data)/KB, "K")
    elif float(data)/MB < KB:
        return "%.2f %s" %(float(data)/MB, "M")
    elif float(data)/GB < KB:
        return "%.2f %s" %(float(data)/GB, "G")
    elif float(data)/TB < KB:
        return "%.2f %s" %(float(data)/TB, "T")
        
def format_column(beginDate, data, field="total"):
    temp = []
    labels = set([datetime_toString(beginDate-timedelta(days=i)) for i in range(7)])
    datalabels = set([datetime_toString(d.get("datetime")) for d in data])

    for l in list(labels - datalabels):
        temp.append({"%s" %(field, ): 0, "datetime": l})
    for d in data:
        temp.append({"%s" %(field, ): d.get(field) if d.get(field) else 0, "datetime": datetime_toString(d.get("datetime"))})

    return temp