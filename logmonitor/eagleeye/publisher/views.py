#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.db.models import Sum
from models import LogPublish, LogPublishTotal, LogPublishDelay
from utilities import data_format,datetime_toString,string_toDatetime,format_column,VIPS,SOURCE
from flashcharts import Column3D, MSBar2D, MSColumn3D, MSLine2D
from datetime import date, timedelta, datetime
from rcms.views import get_customerMap,get_channelMap
import logging
import json

logger = logging.getLogger("eagleeye")

def day_warning(request):
    context = {}
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))
    context["beginDate"] = beginDate
    return render_to_response("publisher/day_warning.html", context, context_instance=RequestContext(request))

def get_daywarn_data(beginDate):
    today = {}
    lastweek = {}
    result = []
    for each in LogPublish.objects.filter(datetime=string_toDatetime(beginDate),customer_id__in=VIPS,size__gt=1024*1024).values_list("channel_id", "size"):
        today[each[0]] = each[1]
    for each in LogPublish.objects.filter(datetime=(string_toDatetime(beginDate)-timedelta(days=7)),customer_id__in=VIPS,size__gt=1024*1024).values_list("channel_id", "size"):
        lastweek[each[0]] = each[1]

    for key, value in today.items():
        if key in lastweek and (float(lastweek[key]-value)/lastweek[key]) > 0.25:
            result.append({"channel_id": key, "today_size": value, "lastweek_size": lastweek[key], "rate": float(lastweek[key]-value)/lastweek[key]})

    return sorted(result, key=lambda d:d["rate"], reverse=True)

@cache_page(60*60)
def get_chartSize(request):
    length = len(get_daywarn_data(request.GET.get("beginDate")))
    return HttpResponse("%s" %(length*50 if length != 0 else 520))

@cache_page(60*60)
def daywarn_detail(request):
    beginDate = request.GET.get("beginDate")
    datas = get_daywarn_data(beginDate)
    msbar2d = MSBar2D(u"日志差异在25%以上的重点频道", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [
        {"seriesname": beginDate, "color": "667c92", "data": []},
        {"seriesname": datetime_toString(string_toDatetime(beginDate)-timedelta(days=7)), "color":"a76561", "data": []},
    ]
    channelMap = get_channelMap()
    for d in datas:
        msbar2d.categories[0]["category"].append({"label": "%s [%.2f%s]" %(channelMap[d["channel_id"]], d["rate"]*100, "%")})
        msbar2d.dataset[0]["data"].append({"value": d["today_size"]})
        msbar2d.dataset[1]["data"].append({"value": d["lastweek_size"]})
    
    msbar2d.chart["showLegend"] = "1"
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def publish_total(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today() - timedelta(days=1)))}
    return render_to_response("publisher/publish_total.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def publish_year_data(request):
    begin_year = datetime.strptime(datetime.today().strftime("%Y"), "%Y")
    end_year = datetime.strptime("%s1231" %(datetime.today().strftime("%Y")), "%Y%m%d")

    data = LogPublishTotal.objects.filter(datetime__lte=end_year,datetime__gte=begin_year).order_by("datetime").values("datetime").annotate(total=Sum("size"))
    msline2d = MSLine2D(u"全年日志发布统计", datetime.today().strftime("%Y"))
    msline2d.chart["anchorRadius"] = "1"
    msline2d.chart["labelStep"] = "15"
    msline2d.chart["labelDisplay"] = "NONE"
    msline2d.categories = {"category": []}
    msline2d.dataset = [
            {"seriesname": u"全年日志发布统计", "color": "5a7baa", "anchorbgcolor": "5a7baa", "data": []},
    ]
    for d in data:
        msline2d.categories["category"].append({"label": d["datetime"].strftime("%m/%d")})
        msline2d.dataset[0]["data"].append({"value": "%s" %(d["total"])})

    res = json.dumps(msline2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*30)
def total_data(request):
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))
    endDate = string_toDatetime(beginDate)-timedelta(days=6)
    
    data = LogPublishTotal.objects.filter(datetime__lte=string_toDatetime(beginDate),datetime__gte=endDate).order_by("datetime").values("datetime").annotate(total=Sum("size"))
    data = sorted(format_column(string_toDatetime(beginDate), data), key=lambda d:d["datetime"])
    col3d = Column3D(u"日志发布趋势", u"总和")
    values = [{"label": "%s" %(d.get("datetime")), "value": "%s" %(d.get("total"))} for d in data]
    col3d.data = values
    res = json.dumps(col3d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*60)
def multi_total_data(request):
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))
    endDate = string_toDatetime(beginDate)-timedelta(days=6)
    
    data = LogPublishTotal.objects.filter(datetime__lte=string_toDatetime(beginDate),datetime__gte=endDate).order_by("datetime").values_list("datetime","source").annotate(total=Sum("size"))
    label = [datetime_toString(string_toDatetime(beginDate)-timedelta(days=i)) for i in range(6,-1,-1)]
    storage0 = [0*i for i in range(7)]
    storage1 = [0*i for i in range(7)]
    storage2 = [0*i for i in range(7)]
    storage3 = [0*i for i in range(7)]
    for d in data:
        if d[1] == "storage-0":
            storage0[label.index(datetime_toString(d[0]))] = d[2]
        elif d[1] == "storage-1":
            storage1[label.index(datetime_toString(d[0]))] = d[2]
        elif d[1] == "storage-2":
            storage2[label.index(datetime_toString(d[0]))] = d[2]
        elif d[1] == "storage-3":
            storage3[label.index(datetime_toString(d[0]))] = d[2]
    
    mscol3d = MSColumn3D(u"日志发布趋势", u"分源统计")
    mscol3d.categories = [{"category": [{"label": l} for l in label]}]
    mscol3d.dataset = [
        {"seriesname": SOURCE["storage-0"], "color": "667c92", "data": [{"value": each} for each in storage0]},
        {"seriesname": SOURCE["storage-1"], "color": "e8f1d8", "data": [{"value": each} for each in storage1]},
        {"seriesname": SOURCE["storage-2"], "color": "a76561", "data": [{"value": each} for each in storage2]},
        {"seriesname": SOURCE["storage-3"], "color": "cbc579", "data": [{"value": each} for each in storage3]},
    ]
    mscol3d.chart["showValues"] = "0"
    res = json.dumps(mscol3d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def publish_detail(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))}
    return render_to_response("publisher/publish_detail.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def publish_detail_data(request):
    customerId = request.GET.get("customerId")
    channelId = request.GET.get("channelId")
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))
    endDate = string_toDatetime(beginDate)-timedelta(days=6)

    if channelId == "0":
        title = u"%s" %(get_customerMap()[customerId])
        data = LogPublish.objects.filter(datetime__gte=endDate,datetime__lte=string_toDatetime(beginDate),customer_id=customerId).order_by("datetime").values("datetime").annotate(total=Sum("size"))
    else:
        title = u"%s" %(get_channelMap()[channelId])
        data = LogPublish.objects.filter(datetime__gte=endDate,datetime__lte=string_toDatetime(beginDate),channel_id=channelId).order_by("datetime").values("datetime").annotate(total=Sum("size"))

    data = sorted(format_column(string_toDatetime(beginDate), data), key=lambda d:d["datetime"])
    subtitle = "%s ~ %s" %(datetime_toString(endDate).split(" ")[0], beginDate)
    col3d = Column3D(title, subtitle)
    
    values = [{"label": "%s" %(d.get("datetime")), "value": "%s" %(d.get("total"))} for d in data]
    col3d.data = values
    res = json.dumps(col3d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*30)
def publish_delay(request):
    context = {}
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()))
    context["beginDate"] = beginDate
    endDate = string_toDatetime(beginDate)+timedelta(days=1)
    customers = LogPublishDelay.objects.all()
    customers.query.group_by = ["user_name"]
    context["customers"] = [ c.user_name for c in customers ]

    data = LogPublishDelay.objects.filter(datetime__gte=string_toDatetime(beginDate), datetime__lt=endDate).values("source").annotate(total=Sum("size"))
    if not data:
        context["storage2_delay"] = 0
        context["storage3_delay"] = 0
    else:
        for d in data:
            if d.get("source") == "storage-2":
                context["storage2_delay"] = data_format(d.get("total"))
            else:
                context["storage3_delay"] = data_format(d.get("total"))
    
    return render_to_response("publisher/publish_delay.html", context, context_instance=RequestContext(request))

@cache_page(60*60)
def publish_delay_summary(request):
    beginDate = request.GET.get("beginDate")
    endDate = string_toDatetime(beginDate)+timedelta(days=1)

    context = {}
    data = LogPublishDelay.objects.filter(datetime__gte=string_toDatetime(beginDate), datetime__lt=endDate, user_name=request.GET.get("customer")).values("source").annotate(total=Sum("size"))
    if not data:
        context["storage2_delay"] = 0
        context["storage3_delay"] = 0
    else:
        for d in data:
            if d.get("source") == "storage-2":
                context["storage2_delay"] = data_format(d.get("total"))
            else:
                context["storage3_delay"] = data_format(d.get("total"))

    return HttpResponse(json.dumps(context, ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*60)
def publish_delay_data(request):
    beginDate = request.GET.get("beginDate")
    endDate = string_toDatetime(beginDate)+timedelta(days=1)

    label = []
    datas = LogPublishDelay.objects.filter(datetime__gte=string_toDatetime(beginDate), datetime__lt=endDate, user_name=request.GET.get("customer")).order_by("datetime")
    for data in datas:
        if data.datetime.strftime("%H") not in label:
            label.append(data.datetime.strftime("%H"))
    storage2 = [ 0*i for i in range(len(label)) ]
    storage3 = [ 0*i for i in range(len(label)) ]
    for data in datas:
        if data.source == "storage-2":
            storage2[label.index(data.datetime.strftime("%H"))] = data.size
        elif data.source == "storage-3":
            storage3[label.index(data.datetime.strftime("%H"))] = data.size
    
    msline2d = MSLine2D(u"重点客户发布日志延迟统计", beginDate)
    msline2d.categories = {"category": [ {"label": l} for l in label ]}
    msline2d.dataset = [
        {"seriesname": SOURCE["storage-2"], "color": "5a7baa", "anchorbgcolor": "5a7baa", "data": [{"value": "%s" %d} for d in storage2]},
        {"seriesname": SOURCE["storage-3"], "color": "c54443", "anchorbgcolor": "c54443", "data": [{"value": "%s" %d} for d in storage3]}
    ]
    
    return HttpResponse(json.dumps(msline2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

def toplist(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))}
    return render_to_response("publisher/toplist.html", context, context_instance=RequestContext(request))

@cache_page(60*60)
def toplist_user(request):
    beginDate = request.GET.get("beginDate")
    datas = LogPublish.objects.filter(datetime=string_toDatetime(beginDate)).values("customer_id").annotate(total=Sum("size")).order_by("-total")[0:100]
    msbar2d = MSBar2D(u"全网客户发布日志排行榜", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [{"seriesname": u"发布大小", "color": "667c92", "data": []}]
    customerMap = get_customerMap()
    for data in datas:
        if customerMap.has_key(data.get("customer_id")):
            msbar2d.categories[0]["category"].append({"label": customerMap[data.get("customer_id")]})
        else:
            msbar2d.categories[0]["category"].append({"label": data.get("customer_id")})
        msbar2d.dataset[0]["data"].append({"value": data.get("total")})
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*60)
def toplist_channel(request):
    beginDate = request.GET.get("beginDate")
    datas = LogPublish.objects.filter(datetime=string_toDatetime(beginDate)).values("channel_id").annotate(total=Sum("size")).order_by("-total")[0:100]
    msbar2d = MSBar2D(u"全网频道发布日志排行榜", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [{"seriesname": u"发布大小", "color": "667c92", "data": []}]

    channelMap = get_channelMap()
    for data in datas:
        if channelMap.has_key(data.get("channel_id")):
            msbar2d.categories[0]["category"].append({"label": channelMap[data.get("channel_id")]})
        else:
            msbar2d.categories[0]["category"].append({"label": data.get("channel_id")})
        msbar2d.dataset[0]["data"].append({"value": data.get("total")})
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def add_logpublish(request):
    if request.method == "POST":
        for data in json.loads(request.POST.get("data")):
            args = {}
            try:
                args["customer_id"] = data.get("uId")
                args["channel_id"] = data.get("cId")
                args["datetime"] = datetime.strptime(data.get("datetime"), "%Y%m%d")
                args["size"] = data.get("size")

                if LogPublish.objects.filter(channel_id=args["channel_id"],datetime=args["datetime"]).exists():
                    logpublish = LogPublish.objects.get(channel_id=args["channel_id"],datetime=args["datetime"])
                    LogPublish.objects.filter(id=logpublish.id).update(size=args["size"])
                else:
                    LogPublish.objects.create(**args)
            except Exception, e:
                logger.error(e)
        return HttpResponse("Add log publish ok.")
    else:
        return HttpResponse("Http method wrong.")

def add_total_logpublish(request):
    if request.method == "POST":
        for data in json.loads(request.POST.get("data")):
            args = {}
            try:
                args["datetime"] = datetime.strptime(data.get("today"), "%Y%m%d")
                args["size"] = data.get("size")
                args["source"] = data.get("source")

                if LogPublishTotal.objects.filter(source=args["source"],datetime=args["datetime"]).exists():
                    logpublishtotal = LogPublishTotal.objects.get(source=args["source"],datetime=args["datetime"])
                    LogPublishTotal.objects.filter(id=logpublishtotal.id).update(size=args["size"])
                else:
                    LogPublishTotal.objects.create(**args)
            except Exception, e:
                logger.error(e)
        return HttpResponse("Add total publish ok.")
    else:
        return HttpResponse("Http method wrong.")

def add_publish_delay(request):
    if request.method == "POST":
        for data in json.loads(request.POST.get("data")):
            args = {}
            try:
                args["datetime"] = datetime.strptime(data.get("datetime"), "%Y%m%d%H")
                args["size"] = data.get("size")
                args["source"] = data.get("source")
                args["user_name"] = data.get("user_name")

                LogPublishDelay.objects.create(**args)
            except Exception, e:
                logger.error(e)
        return HttpResponse("Add publish delay ok.")
    else:
        return HttpResponse("Http method wrong.")
