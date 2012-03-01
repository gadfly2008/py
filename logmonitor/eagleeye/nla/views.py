#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from models import Directory, Block
from flashcharts import ScrollComb2dDY, MSBar2D, MSCombiDY2D, MSLine2D, StackedArea2D, Pie2D, StackedBar2D
from datetime import datetime, date, timedelta
from django.core.cache import cache
from pymongo import DESCENDING
from utilities import datetime_toString, string_toDatetime, data_format
from rcms.views import get_device_map, get_channelMap
from django.conf import settings
import logging
import json

logger = logging.getLogger("eagleeye")
db = settings.MONGODB

def nla_monitor(request):
    context = {}
    return render_to_response("nla/nlamonitor.html", context, context_instance=RequestContext(request))

@cache_page(60*10)
def nla_monitor_data(request):
    args = {}
    if request.GET.get("device") != u"NLA查询":
        args["hostname"] = request.GET.get("device")
    if request.GET.get("ftp") != "-1":
        args["vsftp"] = request.GET.get("ftp")
    
    res = {"data": [], "warning": 0, "forewarning": 0, "notice": 0, "normal": 0}
    devicesMap = {}
    dirs = Directory.objects.filter(**args)
    blocks = Block.objects.filter(**args)
    for dir in dirs:
        if not devicesMap.has_key(dir.hostname):
            devicesMap[dir.hostname] = {"hostname": dir.hostname, "level": 0, "dirs": [], "blocks": []}

        devicesMap[dir.hostname]["ftp"] = dir.vsftp
        devicesMap[dir.hostname]["health"] = dir.health
        devicesMap[dir.hostname]["datetime"] = dir.datetime
        devicesMap[dir.hostname]["level"] |= dir.level
        devicesMap[dir.hostname]["dirs"].append({"name": dir.name, "size": dir.size, "count": dir.count})

    for block in blocks:
        devicesMap[block.hostname]["level"] |= block.level
        devicesMap[block.hostname]["blocks"].append({"name": block.name, "used": block.used})

    for key, value in devicesMap.items():
        value["dirs"] = sorted(value.get("dirs"), key=lambda d:d.get("size"), reverse=True)
        value["dirs"] = [{"name": each.get("name"), "size": data_format(each.get("size")), "count": each.get("count")} for each in value.get("dirs")]
        value["master_dir"] = value["dirs"].pop(0)

        value["blocks"] = sorted(value.get("blocks"), key=lambda d:d.get("used"), reverse=True)
        value["master_block"] = value["blocks"].pop(0)

        if datetime.now() > value["datetime"] and ((datetime.now() - value["datetime"]).seconds+(datetime.now() - value["datetime"]).days*86400) > 1800:
            value["level"] = 1
        elif value["level"] == 3 and value["ftp"] == "stop":
            value["level"] = 2
        value["datetime"] = value["datetime"].strftime("%Y/%m/%d %H:%M:%S")

        if value["level"] == 3:
            res["warning"] += 1
        elif value["level"] == 2:
            res["forewarning"] += 1
        elif value["level"] == 1:
            res["notice"] += 1
        else:
            res["normal"] += 1
        res["data"].append(value)
    
    res["data"] = sorted(res["data"], key=lambda d:d.get("level"), reverse=True)
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

def nla_monitor_delete(request, nla):
    try:
        Directory.objects.filter(hostname=nla).delete()
        Block.objects.filter(hostname=nla).delete()
        return HttpResponse("true")
    except Exception, e:
        logger.error(e)
        return HttpResponse("false")

def nla_performance(request, nla):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today())), "device_name": nla}
    return render_to_response("nla/nla_performance.html", context, context_instance=RequestContext(request))

@cache_page(60*10)
def nla_performance_data(request, nla):
    ptype = request.GET.get("type")
    beginDate = request.GET.get("beginDate")

    ckey = "nlamonitor_performance_%s_%s" %(nla, beginDate.replace("-", ""))
    if cache.has_key(ckey):
        data = cache.get(ckey)
    else:
        collection = db["nla_performance_%s" %(beginDate.replace("-", ""))]
        data = [d for d in collection.find({"hostname": nla})]
        cache.set(ckey, data, 60*30)

    mscombidy2d = MSCombiDY2D("Performance", beginDate)
    if ptype == "cpu":
        mscombidy2d.chart["formatNumber"] = "0"
        mscombidy2d.chart["formatNumberScale"] = "0"
        mscombidy2d.chart["sFormatNumber"] = "0"
        mscombidy2d.chart["sFormatNumberScale"] = "0"
        mscombidy2d.chart["caption"] = "CPU Monitor"
        mscombidy2d.categories = {"category": [{"name": d["datetime"].strftime("%H:%M")} for d in data]}
        mscombidy2d.dataset = [
            {"seriesname": "CPU US", "parentyaxis": "P", "renderas": "Area", "color": "5a885e",
             "data": [{"value": "%s" %(d["cpu_us"],)} for d in data]
            },
            {"seriesname": "CPU Idle", "parentyaxis": "S", "renderas": "Area", "color": "dca657",
             "data": [{"value": "%s" %(d["cpu_idle"],)} for d in data]
            }
        ]
    elif ptype == "io":
        mscombidy2d.chart["formatNumber"] = "0"
        mscombidy2d.chart["formatNumberScale"] = "0"
        mscombidy2d.chart["sFormatNumber"] = "0"
        mscombidy2d.chart["sFormatNumberScale"] = "0"
        mscombidy2d.chart["caption"] = "IO Monitor"
        mscombidy2d.categories = {"category": [{"name": d["datetime"].strftime("%H:%M")} for d in data]}
        mscombidy2d.dataset = [
            {"seriesname": "IO Await", "parentyaxis": "P", "renderas": "Area", "color": "5a885e",
             "data": [{"value": "%s" %(d["io_await"],)} for d in data]
            },
            {"seriesname": "IO Idle", "parentyaxis": "S", "renderas": "Area", "color": "dca657",
             "data": [{"value": "%s" %(d["io_idle"],)} for d in data]
            }
        ]
    elif ptype == "memory":
        mscombidy2d.chart["caption"] = "Memory Monitor"
        mscombidy2d.chart["showSecondaryLimits"] = "0"
        mscombidy2d.chart["showDivLineSecondaryValue"] = "0"
        mscombidy2d.categories = {"category": [{"name": d["datetime"].strftime("%H:%M")} for d in data]}
        mscombidy2d.dataset = [
            {"seriesname": "Memory Free", "parentyaxis": "P", "renderas": "Area", "color": "5a885e",
             "data": [{"value": "%s" %(int(d["memory_free"])*1024,)} for d in data]
            }
        ]
    elif ptype == "load":
        mscombidy2d.chart["formatNumber"] = "0"
        mscombidy2d.chart["formatNumberScale"] = "0"
        mscombidy2d.chart["sFormatNumber"] = "0"
        mscombidy2d.chart["sFormatNumberScale"] = "0"
        mscombidy2d.chart["caption"] = "Load Monitor"
        mscombidy2d.categories = {"category": [{"name": d["datetime"].strftime("%H:%M")} for d in data]}
        mscombidy2d.dataset = [
            {"seriesname": "Load Average", "parentyaxis": "P", "renderas": "Area", "color": "5a885e",
             "data": [{"value": "%s" %(d["load_average"],)} for d in data]
            }
            ,
            {"seriesname": "Load User", "parentyaxis": "S", "renderas": "Area", "color": "dca657",
             "data": [{"value": "%s" %(d["load_user"],)} for d in data]
            }
        ]
    elif ptype == "health":
        collection = db["nla_health"]
        mscombidy2d.chart["caption"] = "NLA Health"
        mscombidy2d.chart["showSecondaryLimits"] = "0"
        mscombidy2d.chart["showDivLineSecondaryValue"] = "0"
        mscombidy2d.chart["formatNumber"] = "0"
        mscombidy2d.chart["formatNumberScale"] = "0"
        mscombidy2d.categories = {"category": []}
        mscombidy2d.dataset = [
            {"seriesname": "NLA Health", "parentyaxis": "P", "renderas": "Area", "color": "5a885e",
             "data": []
            }
        ]
        for data in collection.find({"hostname": nla, "datetime": {"$gte": string_toDatetime(beginDate), "$lt": string_toDatetime(beginDate)+timedelta(days=1)}}):
            mscombidy2d.categories["category"].append({"name": data["datetime"].strftime("%H:%M")})
            mscombidy2d.dataset[0]["data"].append({"value": "%s" %(data["health"])})

    elif ptype == "dir":
        collection = db["nla_masterdir_%s" %(beginDate.replace("-", ""))]
        mscombidy2d.chart["caption"] = "NLA Dir"
        mscombidy2d.chart["showSecondaryLimits"] = "0"
        mscombidy2d.chart["showDivLineSecondaryValue"] = "0"
        mscombidy2d.categories = {"category": []}
        mscombidy2d.dataset = [
            {"seriesname": "NLA Dir", "parentyaxis": "P", "renderas": "Line", "color": "5a885e",
             "data": []
            }
        ]
        for data in collection.find({"hostname": nla}):
            mscombidy2d.categories["category"].append({"name": data["datetime"].strftime("%H:%M")})
            mscombidy2d.dataset[0]["data"].append({"value": "%s" %(data["size"])})

    elif ptype == "speed":
        collection = db["nla_process_%s" %(beginDate.replace("-", ""))]
        mscombidy2d.chart["caption"] = "NLA Process Speed"
        mscombidy2d.chart["showSecondaryLimits"] = "0"
        mscombidy2d.chart["showDivLineSecondaryValue"] = "0"
        mscombidy2d.categories = {"category": []}
        mscombidy2d.dataset = [
            {"seriesname": "NLA Process Speed", "parentyaxis": "P", "renderas": "Line", "color": "5a885e",
             "data": []
            }
        ]
        for data in collection.find({"hostname": nla}):
            mscombidy2d.categories["category"].append({"name": data["datetime"].strftime("%H:%M")})
            mscombidy2d.dataset[0]["data"].append({"value": "%.2f" %(float(data["size"])/data["use_time"])})

    res = json.dumps(mscombidy2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def nla_statistic(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today()))}
    return render_to_response("nla/nla_statistic.html", context, context_instance=RequestContext(request))

@cache_page(60*10)
def nla_statistic_systemload(request):
    beginDate = request.GET.get("beginDate")
    ckey = "nla_performance_systemload_%s" %(beginDate.replace("-", ""))

    if cache.has_key(ckey):
        data = cache.get(ckey)
    else:
        collection = db["nla_performance_%s" %(beginDate.replace("-", ""))]

        func = """
            function(doc,prev){
                var load = parseFloat(doc.load_average);
                if (load >= 0.00 && load < 2.00){
                    prev.count1++;
                }
                else if (load >= 2.00 && load < 6.00){
                    prev.count2++;
                }
                else if (load >= 6.00 && load < 10.00){
                    prev.count3++;
                }
                else {
                    prev.count4++;
                }
            }
        """
        data = collection.group(["datetime"], None, {"count1": 0, "count2": 0, "count3": 0, "count4": 0}, func)
        cache.set(ckey, data, 60*30)

    stackedarea2D = StackedArea2D(u"NLA负载统计", beginDate)
    stackedarea2D.categories = {"category": []}
    stackedarea2D.dataset = [
        {"seriesname": "0~2", "color": "5978a7", "data": []},
        {"seriesname": "2~6", "color": "ad6359", "data": []},
        {"seriesname": "6~10", "color": "d7e098", "data": []},
        {"seriesname": "10~~", "color": "23d174", "data": []},
    ]

    for d in data:
        stackedarea2D.categories["category"].append({"label": d["datetime"].strftime("%H:%M")})
        stackedarea2D.dataset[0]["data"].append({"value": "%s" %(d["count1"])})
        stackedarea2D.dataset[1]["data"].append({"value": "%s" %(d["count2"])})
        stackedarea2D.dataset[2]["data"].append({"value": "%s" %(d["count3"])})
        stackedarea2D.dataset[3]["data"].append({"value": "%s" %(d["count4"])})

    stackedarea2D.chart["legendNumColumns"] = "6"
    return HttpResponse(json.dumps(stackedarea2D.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*10)
def nla_statistic_masterdir(request):
    beginDate = request.GET.get("beginDate")
    ckey = "nla_masterdir_statistic_%s" %(beginDate.replace("-", ""))

    if cache.has_key(ckey):
        data = cache.get(ckey)
    else:
        collection = db["nla_masterdir_%s" %(beginDate.replace("-", ""))]
        func = """
            function(doc,prev){
                prev.total_size += doc.size;
            }
        """
        data = collection.group(["datetime"], None, {"total_size": 0}, func)
        cache.set(ckey, data, 60*30)


    msline2d = MSLine2D(u"LogAnalysis目录统计", beginDate)
    msline2d.categories = {"category": []}
    msline2d.dataset = [
        {"seriesname": "/proclog/loganalysis/begin", "color": "5a7baa", "anchorbgcolor": "5a7baa", "data": []},
    ]

    for d in data:
        msline2d.categories["category"].append({"label": d["datetime"].strftime("%H:%M")})
        msline2d.dataset[0]["data"].append({"value": "%s" %(d["total_size"])})

    return HttpResponse(json.dumps(msline2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*10)
def nla_statistic_speed(request):
    beginDate = request.GET.get("beginDate")
    ckey = "nla_process_statistic_%s" %(beginDate.replace("-", ""))
    if cache.has_key(ckey):
        data = cache.get(ckey)
    else:
        collection = db["nla_process_%s" %(beginDate.replace("-", ""))]
        func = """
            function(doc,prev){
                prev.total_size += doc.size;
                prev.total_use_time += doc.use_time;
            }
        """
        data = collection.group(["datetime"], None, {"total_size": 0, "total_use_time": 0}, func)
        cache.set(ckey, data, 60*30)

    msline2d = MSLine2D(u"LogAnalysis处理速度统计", beginDate)
    msline2d.categories = {"category": []}
    msline2d.dataset = [
        {"seriesname": u"LogAnalysis处理速度", "color": "5a7baa", "anchorbgcolor": "5a7baa", "data": []},
    ]

    for d in data:
        msline2d.categories["category"].append({"label": d["datetime"].strftime("%H:%M")})
        msline2d.dataset[0]["data"].append({"value": "%.2f" %(float(d["total_size"])/d["total_use_time"])})

    return HttpResponse(json.dumps(msline2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

def nla_area(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today()))}
    return render_to_response("nla/nla_area.html", context, context_instance=RequestContext(request))

def get_nlafc_data(dt):
    ckey = "nlafc_area_statistic_%s" %(dt.replace("-", ""),)
    if cache.has_key(ckey):
        return cache.get(ckey)
    else:
        collection = db["nlafc_%s" %(dt.replace("-", ""),)]
        data = [d for d in collection.find()]
        cache.set(ckey, data, 60*30)
        return data

@cache_page(60*30)
def nlafc_node_rate(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)

    pie2d = Pie2D(u"同节点与不同节点的比较", beginDate)
    snode = 0
    dnode = 0
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue

        nla_node = "-".join(deviceMap[data["nlasn"]].split("-")[0:3])
        fc_node = "-".join(deviceMap[data["fcsn"]].split("-")[0:3])
        if nla_node == fc_node:
            snode += 1
        else:
            dnode += 1

    pie2d.data = [{"label": u"同节点", "value": "%s" %(snode,), "isSliced": "1"},{"label": u"不同节点", "value": "%s" %(dnode,)}]

    return HttpResponse(json.dumps(pie2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*30)
def nlafc_city_rate(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)

    pie2d = Pie2D(u"同城市与不同城市的比较", beginDate)
    scity = 0
    dcity = 0
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue
        nla_city = "".join(deviceMap[data["nlasn"]].split("-")[1:2])
        fc_city = "".join(deviceMap[data["fcsn"]].split("-")[1:2])
        if nla_city == fc_city:
            scity += 1
        else:
            dcity += 1
    pie2d.data = [{"label": u"同城市", "value": "%s" %(scity,), "isSliced": "1"},{"label": u"不同城市", "value": "%s" %(dcity,)}]

    return HttpResponse(json.dumps(pie2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*30)
def nlafc_isp_rate(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)

    pie2d = Pie2D(u"同ISP与不同ISP的比较", beginDate)
    sisp = 0
    disp = 0
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue
            
        nla_isp = "".join(deviceMap[data["nlasn"]].split("-")[0:1])
        fc_isp = "".join(deviceMap[data["fcsn"]].split("-")[0:1])
        if nla_isp == fc_isp:
            sisp += 1
        else:
            disp += 1
    pie2d.data = [{"label": u"同ISP", "value": "%s" %(sisp,), "isSliced": "1"},{"label": u"不同ISP", "value": "%s" %(disp,)}]

    return HttpResponse(json.dumps(pie2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))
    
@cache_page(60*30)
def nlafc_crosschn_data(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)
    pie2d = Pie2D(u"CHN之外的ISP", beginDate)
    pie2d.data = []
    res = {}
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue
        
        nla_isp = "".join(deviceMap[data["nlasn"]].split("-")[0:1])
        fc_isp = "".join(deviceMap[data["fcsn"]].split("-")[0:1])

        if nla_isp == "CHN" and fc_isp !="CHN":
            if not res.has_key(fc_isp):
                res[fc_isp] = 1
            else:
                res[fc_isp] += 1

    for key, value in res.items():
        pie2d.data.append({"label": "%s" %(key, ), "value": "%s" %(value,),})

    return HttpResponse(json.dumps(pie2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*30)
def nlafc_crosscnc_data(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)
    pie2d = Pie2D(u"CNC之外的ISP", beginDate)
    pie2d.data = []
    res = {}
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue

        nla_isp = "".join(deviceMap[data["nlasn"]].split("-")[0:1])
        fc_isp = "".join(deviceMap[data["fcsn"]].split("-")[0:1])

        if nla_isp == "CNC" and fc_isp !="CNC":
            if not res.has_key(fc_isp):
                res[fc_isp] = 1
            else:
                res[fc_isp] += 1

    for key, value in res.items():
        pie2d.data.append({"label": "%s" %(key, ), "value": "%s" %(value,),})

    return HttpResponse(json.dumps(pie2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4))

def order_data(chart, data):
    data = sorted(data.items(), key=lambda d:float(d[1]["nlacounts"])/d[1]["fccounts"] if d[1]["fccounts"] else float(100), reverse=True)

    for key, value in data:
        chart.categories[0]["category"].append({"label": "%s" %(key,)})
        chart.dataset[0]["data"].append({"value": "%s" %(value["nlacounts"])})
        chart.dataset[1]["data"].append({"value": "%s" %(value["fccounts"])})

    return chart

@cache_page(60*30)
def nlafc_node_data(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)

    sb2d = StackedBar2D(u"节点NLA和FC比例", beginDate)
    sb2d.categories = [{"category": []}]
    sb2d.dataset = [
        {"seriesname": "NLA", "color": "5978a7", "data": []},
        {"seriesname": "FC", "color": "ad6359", "data": []},
    ]
    res = {}
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue

        nla_name = deviceMap[data["nlasn"]]
        fc_name = deviceMap[data["fcsn"]]
        nla_node = "-".join(nla_name.split("-")[0:3])
        fc_node = "-".join(fc_name.split("-")[0:3])

        if not res.has_key(nla_node):
            res[nla_node] = {"nlas": [], "nlacounts": 0, "fcs": [], "fccounts": 0}
        if not res.has_key(fc_node):
            res[fc_node] = {"nlas": [], "nlacounts": 0 ,"fcs": [], "fccounts": 0}

        if nla_name not in res[nla_node]["nlas"]:
            res[nla_node]["nlas"].append(nla_name)
            res[nla_node]["nlacounts"] += 1
        if fc_name not in res[fc_node]["fcs"]:
            res[fc_node]["fcs"].append(fc_name)
            res[fc_node]["fccounts"] += 1

    sb2d = order_data(sb2d, res)
    res = json.dumps(sb2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*30)
def nlafc_city_data(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)

    sb2d = StackedBar2D(u"城市NLA和FC比例", beginDate)
    sb2d.categories = [{"category": []}]
    sb2d.dataset = [
        {"seriesname": "NLA", "color": "5978a7", "data": []},
        {"seriesname": "FC", "color": "ad6359", "data": []},
    ]
    res = {}
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue

        nla_name = deviceMap[data["nlasn"]]
        fc_name = deviceMap[data["fcsn"]]
        nla_city = "".join(nla_name.split("-")[1:2])
        fc_city = "".join(fc_name.split("-")[1:2])

        if not res.has_key(nla_city):
            res[nla_city] = {"nlas": [], "nlacounts": 0, "fcs": [], "fccounts": 0}
        if not res.has_key(fc_city):
            res[fc_city] = {"nlas": [], "nlacounts": 0 ,"fcs": [], "fccounts": 0}

        if nla_name not in res[nla_city]["nlas"]:
            res[nla_city]["nlas"].append(nla_name)
            res[nla_city]["nlacounts"] += 1
        if fc_name not in res[fc_city]["fcs"]:
            res[fc_city]["fcs"].append(fc_name)
            res[fc_city]["fccounts"] += 1

    sb2d = order_data(sb2d, res)
    res = json.dumps(sb2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*30)
def nlafc_isp_data(request):
    beginDate = request.GET.get("beginDate")
    datas = get_nlafc_data(beginDate)

    sb2d = StackedBar2D(u"ISP NLA和FC比例", beginDate)
    sb2d.categories = [{"category": []}]
    sb2d.dataset = [
        {"seriesname": "NLA", "color": "5978a7", "data": []},
        {"seriesname": "FC", "color": "ad6359", "data": []},
    ]
    res = {}
    deviceMap = get_device_map()
    for data in datas:
        if not deviceMap.has_key(data["nlasn"]):
            continue
        if not deviceMap.has_key(data["fcsn"]):
            continue

        nla_name = deviceMap[data["nlasn"]]
        fc_name = deviceMap[data["fcsn"]]
        nla_isp = "".join(nla_name.split("-")[0:1])
        fc_isp = "".join(fc_name.split("-")[0:1])

        if not res.has_key(nla_isp):
            res[nla_isp] = {"nlas": [], "nlacounts": 0, "fcs": [], "fccounts": 0}
        if not res.has_key(fc_isp):
            res[fc_isp] = {"nlas": [], "nlacounts": 0 ,"fcs": [], "fccounts": 0}

        if nla_name not in res[nla_isp]["nlas"]:
            res[nla_isp]["nlas"].append(nla_name)
            res[nla_isp]["nlacounts"] += 1
        if fc_name not in res[fc_isp]["fcs"]:
            res[fc_isp]["fcs"].append(fc_name)
            res[fc_isp]["fccounts"] += 1

    sb2d = order_data(sb2d, res)
    res = json.dumps(sb2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def nla_fc(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today()))}
    return render_to_response("nla/nlafc.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def nla_fc_summary(request):
    nlafc = None
    res = {"count": 0, "fsize": 0, "fcount": 0}
    beginDate = request.GET.get("beginDate")
    collection = db["nlafc_%s" %(beginDate.replace("-", ""))]

    nla = request.GET.get("nla")
    fc = request.GET.get("fc")

    func = """
        function(doc,prev){
            prev.fsize += doc.fsize;
            prev.fcount += doc.fcount;
            prev.count++;
        }
    """

    if nla != "0":
        nlafc = collection.group(["nlasn"],{"nlasn": nla},{"count": 0, "fsize": 0, "fcount": 0}, func)

    if fc != "0":
        nlafc = collection.group(["fcsn"],{"fcsn": fc},{"count": 0, "fsize": 0, "fcount": 0}, func)

    if nlafc:
        res = {"count": nlafc[0].get("count"), "fsize": data_format(int(nlafc[0].get("fsize"))), "fcount": nlafc[0].get("fcount")}
        
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*30)
def nla_fc_data(request):
    beginDate = request.GET.get("beginDate")
    collection = db["nlafc_%s" %(beginDate.replace("-", ""))]

    nla = request.GET.get("nla")
    fc = request.GET.get("fc")

    deviceMap = get_device_map()
    if nla != "0" and fc == "0":
        ifilter = {"nlasn": nla}
        name = deviceMap[nla]
    elif nla == "0" and fc != "0":
        ifilter = {"fcsn": fc}
        name = deviceMap[fc]
    else:
        ifilter = {"nlasn": nla, "fcsn": fc}
        name = deviceMap[nla]

    nlafcs = collection.find(ifilter).sort("fsize", DESCENDING)
    sc2ddy = ScrollComb2dDY(name, beginDate)

    fsize = []
    fcount = []
    labels = []
    for nlafc in nlafcs:
        fsize.append({"value": "%s" %(nlafc["fsize"],)})
        fcount.append({"value": "%s" %(nlafc["fcount"],)})
        if ifilter.has_key("nlasn"):
            if deviceMap.has_key(nlafc["fcsn"]):
                labels.append({"label": deviceMap[nlafc["fcsn"]]})
            else:
                labels.append({"label": nlafc["fcsn"]})
        else:
            if deviceMap.has_key(nlafc["nlasn"]):
                labels.append({"label": deviceMap[nlafc["nlasn"]]})
            else:
                labels.append({"label": nlafc["nlasn"]})

    sc2ddy.categories = [{"category": labels}]
    sc2ddy.dataset = [
        {"seriesname": u"文件大小", "showvalues": "0", "color": "848563", "data": fsize, "parentyaxis": "P"},
        {"seriesname": u"文件数量", "color": "445774", "data": fcount, "parentyaxis": "S"},
    ]
    
    res = json.dumps(sc2ddy.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def channel_nla(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today()))}
    return render_to_response("nla/channel_original.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def channel_original(request):
    channelId = request.GET.get("channelId")
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))
    endDate = string_toDatetime(beginDate)-timedelta(days=6)

    channelMap = get_channelMap()
    mscdy2d = MSCombiDY2D(channelMap[channelId], "%s ~ %s" %(datetime_toString(endDate), beginDate))

    mscdy2d.categories = {"category": []}
    mscdy2d.dataset = [
        {"seriesname": u"文件行数", "parentyaxis": "P", "color": "5a885e", "data": []
        },
    ]
    func = """
        function(obj,prev){
            if (obj.size){
                prev.total_size += obj.size;
            }
        }
    """
    for i in range(6,-1,-1):
        dt = datetime_toString(string_toDatetime(beginDate)-timedelta(days=i))
        mscdy2d.categories["category"].append({"name": dt})
        collection = db["channelnla_%s" %(dt.replace("-", ""))]
        channelnla = collection.group(["channelId"], {"channelId": "%s" %(channelId,)}, {"total_size": 0}, func)
        if channelnla:
            mscdy2d.dataset[0]["data"].append({"value": "%s" %(channelnla[0]["total_size"]), "link": "javascript:popupChart('%s', %s)" %(dt, channelId)})
        else:
            mscdy2d.dataset[0]["data"].append({"value": "0"})

    mscdy2d.chart["showValues"] = "0"
    mscdy2d.chart["formatNumber"] = "0"
    mscdy2d.chart["formatNumberScale"] = "0"
    mscdy2d.chart["showSecondaryLimits"] = "0"
    mscdy2d.chart["showDivLineSecondaryValue"] = "0"

    res = json.dumps(mscdy2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*30)
def channel_nla_summary(request):
    context = {"nlacount": 0, "size": 0, "output_count": 0, "upload_count": 0}
    beginDate = request.GET.get("beginDate")
    channelId = request.GET.get("channelId")

    func = """
        function(doc,prev){
            if (doc.size){
                prev.size += doc.size;
            }
            if (doc.outputcount){
                prev.outputcount += doc.outputcount;
            }
            if (doc.uploadcount){
                prev.uploadcount += doc.uploadcount;
            }
            prev.count++;
        }
    """
    collection = db["channelnla_%s" %(beginDate.replace("-", ""))]
    channelnla = collection.group(["channelId"], {"channelId": channelId}, {"size": 0, "outputcount": 0, "uploadcount": 0, "count": 0}, func)[0]
    
    context["channelId"] = channelId
    context["beginDate"] = beginDate
    if channelnla:
        context["nlacount"] = int(channelnla["count"])
        context["size"] = int(channelnla["size"])
        context["output_count"] = int(channelnla["outputcount"])
        context["upload_count"] = int(channelnla["uploadcount"])
            
    return render_to_response("nla/channelnla.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def channel_nla_data(request, channelId):
    beginDate = request.GET.get("beginDate")
    collection = db["channelnla_%s" %(beginDate.replace("-", ""))]

    channelMap = get_channelMap()
    sc2ddy = ScrollComb2dDY(channelMap[channelId], beginDate)
    size = []
    output_count = []
    upload_count = []
    labels = []
    deviceMap = get_device_map()
    for channelnla in collection.find({"channelId": channelId}).sort("size", DESCENDING):
        size.append({"value": "%s" %(channelnla["size"],) if channelnla.has_key("size") else "0"})
        output_count.append({"value": "%s" %(channelnla["outputcount"],) if channelnla.has_key("outputcount") else "0"})
        upload_count.append({"value": "%s" %(channelnla["uploadcount"],) if channelnla.has_key("uploadcount") else "0"})
        if deviceMap.has_key(channelnla["nlasn"]):
            labels.append({"label": deviceMap[channelnla["nlasn"]]})
        else:
            labels.append({"label": channelnla["nlasn"]})
    sc2ddy.categories = [{"category": labels}]
    sc2ddy.dataset = [
        {"seriesname":u"产生文件数","showvalues": "0","color":"848563","data": output_count, "parentyaxis": "P"},
        {"seriesname":u"上传文件数","showvalues": "0","color":"b396bc","data": upload_count, "parentyaxis": "P"},
        {"seriesname":u"文件行数","showvalues": "0","color":"603952","data": size, "parentyaxis": "S"},
    ]
    
    sc2ddy.chart["showDivLineSecondaryValue"] = "1"
    sc2ddy.chart["showSecondaryLimits"] = "1"
    sc2ddy.chart["showValues"] = "0"
    sc2ddy.chart["formatNumber"] = "0"
    sc2ddy.chart["formatNumberScale"] = "0"
    sc2ddy.chart["sFormatNumber"] = "0"
    sc2ddy.chart["sFormatNumberScale"] = "0"
    res = json.dumps(sc2ddy.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def nla_toplist(request):
    context = {}
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()))
    context["beginDate"] = beginDate
    return render_to_response("nla/nla_toplist.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def process_size_top(request):
    beginDate = request.GET.get("beginDate")
    direction = request.GET.get("direction")

    ckey = "nlafc_process_size_top_%s" %(beginDate.replace("-", ""))
    if cache.has_key(ckey):
        data = cache.get(ckey)
    else:
        collection = db["nlafc_%s" %(beginDate.replace("-", ""))]
        func = """
            function(doc,prev){
                prev.total_fsize += doc.fsize;
            }
        """
        data = collection.group(["nlasn"], None, {"total_fsize": 0}, func)
        cache.set(ckey, data, 60*30)

    if direction == "-1":
        data = sorted(data, key=lambda d:d["total_fsize"], reverse=True)
    else:
        data = sorted(data, key=lambda d:d["total_fsize"])

    msbar2d = MSBar2D(u"全网NLA处理日志排行榜", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [{"seriesname": u"文件大小", "color": "667c92", "data": []}]
    deviceMap = get_device_map()
    for d in data[0:50]:
        if deviceMap.has_key(d["nlasn"]):
            msbar2d.categories[0]["category"].append({"label": deviceMap[d["nlasn"]]})
        else:
            msbar2d.categories[0]["category"].append({"label": d["nlasn"]})
        msbar2d.dataset[0]["data"].append({"value": "%s" %(d["total_fsize"])})
    
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

@cache_page(60*30)
def process_speed_top(request):
    beginDate = request.GET.get("beginDate")
    direction = request.GET.get("direction")

    ckey = "top_processspeed_%s" %(beginDate.replace("-", ""))
    if cache.has_key(ckey):
        data = cache.get(ckey)
    else:
        data = []
        collection = db["nla_process_%s" %(beginDate.replace("-", ""))]

        func = """
            function(doc,prev){
                prev.total_size += doc.size;
                prev.total_use_time += doc.use_time;
            }
        """
        nlafcs = collection.group(["hostname"], None, {"total_size": 0, "total_use_time": 0}, func)
        for each in nlafcs:
            data.append({"hostname": each["hostname"], "speed": each["total_size"]/each["total_use_time"]})
        cache.set(ckey, data, 60*30)

    if direction == "-1":
        data = sorted(data, key=lambda d:d["speed"], reverse=True)
    else:
        data = sorted(data, key=lambda d:d["speed"])

    msbar2d = MSBar2D(u"全网NLA处理速度排行榜", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [{"seriesname": u"日志处理速度", "color": "667c92", "data": []}]
    for d in data[0:50]:
        msbar2d.categories[0]["category"].append({"label": d["hostname"]})
        msbar2d.dataset[0]["data"].append({"value": "%.2f" %(d["speed"])})

    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def channel_toplist(request):
    context = {}
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()))
    context["beginDate"] = beginDate
    return render_to_response("nla/channel_toplist.html", context, context_instance=RequestContext(request))

@cache_page(60*30)
def file_line_top(request):
    beginDate = request.GET.get("beginDate")
    collection = db["channelnla_%s" %(beginDate.replace("-", ""))]

    channelnlas = collection.group(["channelId"], None, {"size": 0},"function(doc,prev){prev.size = prev.size+doc.size;}")
    msbar2d = MSBar2D(u"全网频道原始日志排行榜", beginDate)
    msbar2d.categories = [{"category": []}]
    msbar2d.dataset = [{"seriesname": u"文件行数", "color": "667c92", "data": []}]
    channelMap = get_channelMap()
    data = sorted(channelnlas, key=lambda d:d["size"] if float(d["size"]) > 0.0 else 0.0, reverse=True)[0:100]
    for channelnla in data:
        if channelMap.has_key(channelnla["channelId"]):
            msbar2d.categories[0]["category"].append({"label": channelMap[channelnla["channelId"]]})
        else:
            msbar2d.categories[0]["category"].append({"label": channelnla["channelId"]})
        msbar2d.dataset[0]["data"].append({"value": channelnla["size"]})
    msbar2d.chart["formatNumber"] = "0"
    msbar2d.chart["formatNumberScale"] = "0"
    res = json.dumps(msbar2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def add_nlafc(request):
    if request.method == "POST":
        try:
            for data in json.loads(request.POST.get("data")):
                try:
                    collection = db["nlafc_%s" %(data["datetime"].replace("-", ""))]
                    collection.update({"nlasn": data["nlasn"], "fcsn": data["fcsn"]},
                    {"$inc": {"fsize": int(data["fsize"]), "fcount": int(data["fcount"])}}, upsert=True)
                except Exception, e:
                    logger.error("%s, %s" %(data,e))
        except Exception, e:
            logger.error(e)
        return HttpResponse("Add data ok.")
    else:
        return HttpResponse("Http method wrong.")

def add_channelnla(request):
    if request.method == "POST":
        try:
            for data in json.loads(request.POST.get("data")):
                try:
                    collection = db["channelnla_%s" %(data["datetime"].replace("-", ""))]
                    collection.update({"channelId": data["channelId"], "nlasn": data["nlasn"]},
                    {"$inc": {"size": int(data["size"])}, "$set": {"userId": data["userId"]}}, upsert=True)

                except Exception, e:
                    logger.error("%s, %s" %(data,e))
        except Exception, e:
            logger.error(e)
        return HttpResponse("Add data ok.")
    else:
        return HttpResponse("Http method wrong.")

def update_channel_outputcount(request):
    if request.method == "POST":
        try:
            for data in json.loads(request.POST.get("data")):
                try:
                    collection = db["channelnla_%s" %(data["datetime"].replace("-", ""))]
                    collection.update({"channelId": data["channelId"], "nlasn": data["nlasn"]},
                    {"$inc": {"outputcount": int(data["count"])}}, upsert=True)
                except Exception, e:
                    logger.error("%s %s" %(e, data))
        except Exception, e:
            logger.error(e)
        return HttpResponse("Update data ok.")
    else:
        return HttpResponse("Http method wrong.")

def update_channel_uploadcount(request):
    if request.method == "POST":
        try:
            for data in json.loads(request.POST.get("data")):
                try:
                    collection = db["channelnla_%s" %(data["datetime"].replace("-", ""))]
                    collection.update({"channelId": data["channelId"], "nlasn": data["nlasn"]},
                    {"$inc": {"uploadcount": int(data["count"])}}, upsert=True)
                except Exception, e:
                    logger.error("%s %s" %(e, data))
        except Exception, e:
            logger.error(e)

        return HttpResponse("Update data ok.")
    else:
        return HttpResponse("Http method wrong.")

def add_nla_data(request):
    if request.method == "POST":
        try:
            datas = json.loads(request.POST.get("data"))

            if datas.has_key("process"):
                data = datas["process"]
                collection = db["nla_process_%s" %(datetime.today().strftime("%Y%m%d"))]
                try:
                    dt = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
                    if dt.minute%2:
                        collection.insert({"datetime": dt, "size": int(data["size"]), "count": int(data["count"]),
                                           "use_time": int(data["use_time"]), "hostname": data["hostname"]})
                except Exception, e:
                    logger.error(e)

            if datas.has_key("masterdir"):
                data = datas["masterdir"]
                collection = db["nla_masterdir_%s" %(datetime.today().strftime("%Y%m%d"))]
                try:
                    dt = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
                    if not dt.minute%2:
                        collection.insert({"datetime": dt, "size": int(data["size"]), "hostname": data["hostname"]})
                except Exception, e:
                    logger.error(e)

            if datas.has_key("dir"):
                collection = db["nla_health"]
                health = 0
                hostname = ""
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                for data in datas.get("dir"):
                    args = {}
                    try:
                        args["hostname"] = data.get("hostname")
                        args["name"] = data.get("name")
                        args["count"] = data.get("count")
                        args["size"] = data.get("size")
                        args["level"] = int(data.get("level"))
                        args["datetime"] = datetime.strptime(data.get("datetime"), "%Y-%m-%d %H:%M")
                        args["vsftp"] = data.get("vsftp")
                        args["health"] = data.get("health")
                        hostname = data.get("hostname")
                        health = int(data.get("health"))
                        dt = datetime.strptime(data.get("datetime"), "%Y-%m-%d %H:%M")

                        if Directory.objects.filter(hostname=args["hostname"],name=args["name"]).exists():
                            directory = Directory.objects.get(hostname=args["hostname"],name=args["name"])
                            Directory.objects.filter(id=directory.id).update(count=args["count"],size=args["size"],level=args["level"],datetime=args["datetime"],vsftp=args["vsftp"],health=args["health"])
                        else:
                            Directory.objects.create(**args)
                    except Exception, e:
                        logger.error(e)

                collection.insert({"hostname": hostname, "health": health, "datetime": dt})

            if datas.has_key("block"):
                for data in datas.get("block"):
                    args = {}
                    try:
                        args["hostname"] = data.get("hostname")
                        args["name"] = data.get("name")
                        args["used"] = data.get("used")
                        args["level"] = int(data.get("level"))

                        if Block.objects.filter(hostname=args["hostname"],name=args["name"]).exists():
                            block = Block.objects.get(hostname=args["hostname"],name=args["name"])
                            Block.objects.filter(id=block.id).update(used=args["used"],level=args["level"])
                        else:
                            Block.objects.create(**args)
                    except Exception, e:
                        logger.error(e)

            if datas.has_key("performance"):
                collection = db["nla_performance_%s" %(datetime.today().strftime("%Y%m%d"))]
                data = []
                for d in datas.get("performance"):
                    d["datetime"] = datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M")
                    if not d["datetime"].minute%2:
                        data.append(d)
                try:
                    collection.insert(data)
                except Exception, e:
                    logger.error(e)
        except Exception, e:
            logger.error(e)
            
        return HttpResponse("Add nla data ok.")
    else:
        return HttpResponse("Http method wrong.")