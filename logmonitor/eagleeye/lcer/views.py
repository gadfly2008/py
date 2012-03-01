#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Count
from models import Directory, Block
from utilities import datetime_toString,string_toDatetime
from flashcharts import Column3D, MSCombiDY2D
from datetime import timedelta, datetime
import logging
import json

logger = logging.getLogger("eagleeye")

@cache_page(60*20)
def lcer_summary(request):
    res = {"bgp": 0, "ccn": 0, "cnc": 0}
    bgps = set()
    ccns = set()
    cncs = set()
    beginDate = request.GET.get("beginDate")
    endDate = string_toDatetime(beginDate)+timedelta(days=1)
    devices = Directory.objects.filter(time__lt=endDate,time__gte=beginDate).values("hostname")
    for d in devices:
        if d.get("hostname").startswith("BGP"):
            bgps.add(d.get("hostname"))
        elif d.get("hostname").startswith("CCN"):
            ccns.add(d.get("hostname"))
        elif d.get("hostname").startswith("CNC"):
            cncs.add(d.get("hostname"))
    
    res["bgp"] = len(bgps)
    res["ccn"] = len(ccns)
    res["cnc"] = len(cncs)
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*60)
def get_lcDirs(request, lc):
    beginDate = string_toDatetime(request.GET.get("beginDate"))
    context = {"dirs": [each.get("name") for each in Directory.objects.filter(time=beginDate, hostname=lc).values("name").annotate(count=Count("name"))]}
    return render_to_response("dirs.html", context, context_instance=RequestContext(request))

def block_monitor(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(datetime.today()))}
    if cache.get("lcs"):
        context["lcs"] = cache.get("lcs")
    else:
        context["lcs"] = get_lcs()
    return render_to_response("lcer/block_monitor.html", context, context_instance=RequestContext(request))

def get_lcs():
    lcs = [each.get("hostname") for each in Block.objects.order_by("hostname").values("hostname").annotate(count=Count("hostname"))]
    cache.set("lcs", lcs, 600)
    return lcs

@cache_page(60*10)
def block_detail(request):
    beginDate = request.GET.get("beginDate")
    endDate = string_toDatetime(beginDate)+timedelta(days=1)
    mtype = request.GET.get("mtype")
    hostname = request.GET.get("hostname")
    
    if mtype == "dir":
        data = Directory.objects.filter(time__gte=string_toDatetime(beginDate),time__lt=endDate,hostname=hostname,name=request.GET.get("dir")).order_by("time")
        mscombidy2d = MSCombiDY2D("%s" %(request.GET.get("dir")), beginDate)
        mscombidy2d.categories = {"category": [{"name": d.time.strftime("%H:%M")} for d in data]}
        mscombidy2d.dataset = [
            {"seriesname": u"目录大小", "parentyaxis": "P", "color": "5a885e",
             "data": [{"value": "%s" %(d.size,)} for d in data]
            },
            {"seriesname": u"目录文件数", "parentyaxis": "S", "renderas": "Line", "color": "dca657", "anchorbgcolor": "dca657",
             "data": [{"value": "%s" %(d.count,)} for d in data]
            }
        ]
        res = json.dumps(mscombidy2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
        return HttpResponse(res)
    elif mtype == "mount":
        col3d = Column3D(u"%s" %(hostname,), beginDate)
        col3d.chart["formatNumber"] = "0"
        col3d.chart["formatNumberScale"] = "0"
        col3d.chart["numberSuffix"] = "%"
        col3d.chart["yAxisMaxValue"] = "100"
        data = Block.objects.filter(hostname=hostname)
        values = [{"label": d.name, "value": d.used} for d in data]
        col3d.data = values
        res = json.dumps(col3d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
        return HttpResponse(res)

def add_lc_data(request):
    if request.method == "POST":
        datas = json.loads(request.POST.get("data"))

        for data in datas.get("dir"):
            args = {}
            try:
                args["hostname"] = data.get("hostname")
                args["name"] = data.get("name")
                args["count"] = data.get("count")
                args["size"] = data.get("size")
                args["time"] = datetime.strptime(data.get("datetime"), "%Y-%m-%d %H:%M")

                Directory.objects.create(**args)
            except Exception, e:
                logger.error("%s,%s" %(data,e))

        for data in datas.get("block"):
            args = {}
            try:
                args["hostname"] = data.get("hostname")
                args["name"] = data.get("name")
                args["used"] = data.get("used")

                block = Block.objects.get(hostname=args["hostname"],name=args["name"])
                Block.objects.filter(id=block.id).update(used=args["used"])
            except Exception, e:
                logger.error(e)
                Block.objects.create(**args)
        return HttpResponse("Add lc data ok.")
    else:
        return HttpResponse("Http method wrong.")