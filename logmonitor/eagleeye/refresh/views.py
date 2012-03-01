#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta
from pymongo import Connection
from models import Queue
from utilities import datetime_toString,string_toDatetime
from flashcharts import MSBar2D, Column3D
from rcms.views import get_channelMap
import logging
import urllib2
import json

logger = logging.getLogger("eagleeye")
API = "http://58.68.228.197:9919"
db = Connection("58.68.228.164:27017")["bermuda"]

@cache_page(60*2)
def summary(request):
    context = {"today": datetime.today().strftime("%m/%d"), "lastday": (datetime.today()-timedelta(days=1)).strftime("%m/%d")}
    today = datetime.strptime(datetime.today().strftime("%Y%m%d"), "%Y%m%d")
    context["lastday_count"] = db.url.find({"created_time": {"$gte": (today-timedelta(days=1)), "$lt": today}}).count()
    context["today_count"] = db.url.find({"created_time": {"$gte": today, "$lt": (today+timedelta(days=1))}}).count()

    queues = []
    opener = urllib2.urlopen("%s/queue/" %(API, ))
    reader = json.loads(opener.read())
    if reader:
        for r in reader:
            queues.append(Queue(r))
    context["queues"] = queues
    return render_to_response("refresh/summary.html", context, context_instance=RequestContext(request))

@cache_page(60*2)
def detail(request):
    context = {"beginDate": request.GET.get("beginDate", datetime.today().strftime("%Y-%m-%d"))}
    return render_to_response("refresh/detail.html", context, context_instance=RequestContext(request))

@cache_page(60*2)
def statistic(request):
    context = {"beginDate": request.GET.get("beginDate", datetime.today().strftime("%Y-%m-%d"))}
    return render_to_response("refresh/statistic.html", context, context_instance=RequestContext(request))

def detail_top_data(request):
    beginDate = request.GET.get("beginDate")
    ifilter = {"created_time": {"$gte": string_toDatetime(beginDate), "$lt": (string_toDatetime(beginDate)+timedelta(days=1))}}

    customer = db.url.group(["username"],ifilter,{"count": 0},"function(doc,prev){prev.count++;}")
    customer = sorted(customer, key=lambda d:d.get("count"), reverse=True)[0:10]
    
    msbar2d = MSBar2D(u"刷新次数前10的客户", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [
        {"seriesname": beginDate, "color": "667c92", "data": []},
    ]
    for d in customer:
        msbar2d.categories[0]["category"].append({"label": "%s" %(d["username"],)})
        msbar2d.dataset[0]["data"].append({"value": "%s" %(d["count"],)})

    msbar2d.chart["showLegend"] = "1"
    msbar2d.chart["formatNumber"] = "0"
    msbar2d.chart["formatNumberScale"] = "0"
    msbar2d.chart["maxLabelWidthPercent"] = "48"
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def detail_total_data(request):
    beginDate = string_toDatetime(request.GET.get("beginDate"))
    customer = request.GET.get("customer")

    data1 = get_total(customer, beginDate)
    data2 = get_total(customer, beginDate - timedelta(days=1))
    data3 = get_total(customer, beginDate - timedelta(days=2))
    col3d = Column3D(u"总刷新趋势", u"总和")
    values = [
            {"label": "%s" %(datetime_toString(beginDate - timedelta(days=2))), "value": "%s" %(data3,)},
            {"label": "%s" %(datetime_toString(beginDate - timedelta(days=1))), "value": "%s" %(data2,)},
            {"label": "%s" %(datetime_toString(beginDate)), "value": "%s" %(data1,)},
    ]
    col3d.data = values
    col3d.chart["formatNumber"] = 0
    col3d.chart["formatNumberScale"] = 0
    res = json.dumps(col3d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def detail_channeltop_data(request):
    beginDate = request.GET.get("beginDate")
    customer = request.GET.get("customer")
    channelMap = get_channelMap()

    ifilter = {"created_time": {"$gte": string_toDatetime(beginDate), "$lt": (string_toDatetime(beginDate)+timedelta(days=1))}, "username": customer}
    urls = db.url.group(["channel_code"],ifilter,{"count": 0},"function(doc,prev){prev.count++;}")
    urls = sorted(urls, key=lambda d:d.get("count"), reverse=True)[0:10]

    msbar2d = MSBar2D(u"刷新次数前10的频道", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [
        {"seriesname": beginDate, "color": "667c92", "data": []},
    ]
    for d in urls:
        if channelMap.has_key(d["channel_code"]):
            msbar2d.categories[0]["category"].append({"label": "%s" %(channelMap[d["channel_code"]],)})
        else:
            msbar2d.categories[0]["category"].append({"label": "%s" %(d["channel_code"])})
        msbar2d.dataset[0]["data"].append({"value": "%s" %(d["count"],)})

    msbar2d.chart["showLegend"] = "1"
    msbar2d.chart["formatNumber"] = "0"
    msbar2d.chart["formatNumberScale"] = "0"
    msbar2d.chart["maxLabelWidthPercent"] = "48"
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def detail_urltop_data(request):
    beginDate = request.GET.get("beginDate")
    customer = request.GET.get("customer")

    data = get_urls(customer, beginDate)
    msbar2d = MSBar2D(u"刷新次数前10的URL", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [
        {"seriesname": beginDate, "color": "667c92", "data": []},
    ]
    for d in data[0:10]:
        msbar2d.categories[0]["category"].append({"label": "%s" %(d["url"],)})
        msbar2d.dataset[0]["data"].append({"value": "%s" %(d["count"],)})

    msbar2d.chart["showLegend"] = "1"
    msbar2d.chart["formatNumber"] = "0"
    msbar2d.chart["formatNumberScale"] = "0"
    msbar2d.chart["maxLabelWidthPercent"] = "48"
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def get_total(user, dt):
    ckey = "count_%s_%s" %(user, datetime_toString(dt))
    if cache.has_key(ckey):
        return cache.get(ckey)
    else:
        ifilter = {"created_time": {"$gte": dt, "$lt": (dt+timedelta(days=1))}, "username": user}
        data = db.url.find(ifilter).count()
        cache.set(ckey, data, 60*2)
        return data

@cache_page(60*2)
def detail_url_data(request):
    beginDate = request.GET.get("beginDate")
    customer = request.GET.get("customer")
    url = request.GET.get("url")

    ifilter = {"created_time": {"$gte": datetime.strptime(beginDate, "%Y-%m-%d"),
                                "$lt": (datetime.strptime(beginDate, "%Y-%m-%d")+timedelta(days=1))},
               "username": customer, "url": {"$regex": url}}

    sort_res = sorted([u for u in db.url.find(ifilter, {"url": 1, "status": 1, "finish_time": 1, "created_time": 1, "_id": 1})], key=lambda d:d["created_time"], reverse=True)[0:50]
    data = [{"finish_time": d["finish_time"].strftime("%m/%d %H:%M:%S") if d.has_key("finish_time") else "", "created_time": d["created_time"].strftime("%m-%d %H:%M:%S"), "status": d["status"], "url": d["url"], "id": str(d["_id"])} for d in sort_res]
    res = json.dumps({"data": data}, ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*2)
def detail_url_devices(request, urlId):
    context = {"total_devices": 0, "unprocess_devices": 0, "devices": [], "urlId": urlId}
    datas = get_devices(urlId)
    if datas:
        context["total_devices"] = len(datas["devices"].keys())
        context["unprocess_devices"] = datas["unprocess"]

        for key, value in datas["devices"].items():
            context["devices"].append([value["name"], value["status"], value["code"], value["host"], value["firstLayer"]])
        context["devices"] = sorted(context["devices"], key=lambda d:d[2], reverse=True)
    return render_to_response("refresh/url_devices.html", context, context_instance=RequestContext(request))

@cache_page(60*2)
def detail_url_devices_sort(request):
    sortType = request.GET.get("sortType")
    urlId = request.GET.get("urlId")
    devices = get_devices(urlId)["devices"]

    if sortType == "hostname":
        devices = sorted(devices.items(), key=lambda d:d[1]["name"])
    elif sortType == "status":
        devices = sorted(devices.items(), key=lambda d:d[1]["status"])
    elif sortType == "code":
        devices = sorted(devices.items(), key=lambda d:d[1]["code"])
    elif sortType == "isfirstlayer":
        devices = sorted(devices.items(), key=lambda d:d[1]["firstLayer"])
    else:
        devices = sorted(devices.items(), key=lambda d:d[1]["code"])
 
    res = json.dumps({"data": [{"name": d[1]["name"], "code": d[1]["code"], "status": d[1]["status"], "ip": d[1]["host"], "firstLayer": d[1]["firstLayer"]} for d in devices]}, ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def get_devices(urlId):
    if cache.has_key(urlId):
        return cache.get(urlId)
    else:
        datas = db.device.find_one({"url_id": urlId})
        cache.set(urlId, datas, 60*2)
        return datas

def get_urls(user, dt, channel=None):

    if channel:
        ckey = "%s_%s_%s" %(user, channel, dt)
        ifilter = {"created_time": {"$gte": datetime.strptime(dt, "%Y-%m-%d"), "$lt": (datetime.strptime(dt, "%Y-%m-%d")+timedelta(days=1))}, "username": user, "channel_code": channel}
    else:
        ifilter = {"created_time": {"$gte": datetime.strptime(dt, "%Y-%m-%d"), "$lt": (datetime.strptime(dt, "%Y-%m-%d")+timedelta(days=1))}, "username": user}
        ckey = "%s_%s" %(user, dt)

    if cache.has_key(ckey):
        return cache.get(ckey)
    else:
        urls = db.url.group(["url"],ifilter,{"count": 0},"function(doc,prev){prev.count++;}")
        urls = sorted(urls, key=lambda d:d.get("count"), reverse=True)[0:100]
        cache.set(ckey, urls, 60*2)
        return urls