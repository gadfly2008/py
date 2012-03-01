#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from flashcharts import MSCombiDY2D
from datetime import datetime, timedelta
from utilities import datetime_toString, string_toDatetime
from django.conf import settings
import logging
import json

logger = logging.getLogger("eagleeye")
db = settings.MONGODB

@cache_page(60*60)
def fc_original(request):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(datetime.today()))}
    return render_to_response("fc/fc_original.html", context, context_instance=RequestContext(request))

@cache_page(60*60)
def fc_original_data(request):
    beginDate = request.GET.get("beginDate")
    mscombidy2d = MSCombiDY2D(u"FC原始日志统计", beginDate)
    mscombidy2d.chart["formatNumber"] = "0"
    mscombidy2d.chart["formatNumberScale"] = "0"
    mscombidy2d.chart["sFormatNumber"] = "0"
    mscombidy2d.chart["sFormatNumberScale"] = "0"
    mscombidy2d.categories = [{"category": []}]

    fcReceiveDs = []
    fcReceiveFs = []
    fcSendDs = []
    fcSendFs = []
    labelIndex = []

    if cache.has_key("%s_fcReceiveDs" %(beginDate,)):
        fcReceiveDs = cache.get("%s_fcReceiveDs" %(beginDate,))
    if cache.has_key("%s_fcReceiveFs" %(beginDate,)):
        fcReceiveFs = cache.get("%s_fcReceiveFs" %(beginDate,))
    if cache.has_key("%s_fcSendDs" %(beginDate,)):
        fcSendDs = cache.get("%s_fcSendDs" %(beginDate,))
    if cache.has_key("%s_fcSendFs" %(beginDate,)):
        fcSendFs = cache.get("%s_fcSendFs" %(beginDate,))

    if not fcReceiveDs or not fcReceiveFs or not fcSendDs or not fcSendFs:

        func1 = """
            function(doc,prev){
                prev.count += doc.fcount;
            }
        """
        for i in range(2, -1, -1):
            dt = datetime_toString(string_toDatetime(beginDate) - timedelta(days=i))
            nlafc = db["nlafc_%s" %(dt.replace("-", ""),)]
            nlafc_data = nlafc.group(["fcsn"], None, {"count": 0}, func1)
            mscombidy2d.categories[0]["category"].append({"name": dt})
            fcReceiveDs.append({"value": len(nlafc_data)})
            count = 0
            for c in nlafc_data:
                count += c["count"]
            fcReceiveFs.append({"value": count})
            fcSendDs.append(0)
            fcSendFs.append(0)
            labelIndex.append(dt)

        func2 = """
            function(doc,prev){
                prev.fcount += doc.count;
                prev.count ++;
            }
        """
        fcoriginal = db["fc_original"]
        fcoriginal_data = fcoriginal.group(["datetime"], {"datetime": {"$gte": (string_toDatetime(beginDate) - timedelta(days=2)),
                                "$lte": string_toDatetime(beginDate)}}, {"count": 0, "fcount": 0}, func2)

        for i in fcoriginal_data:
            fcSendDs[labelIndex.index(datetime_toString(i["datetime"]))] = i["count"]
            fcSendFs[labelIndex.index(datetime_toString(i["datetime"]))] = i["fcount"]

        cache.set("%s_fcReceiveDs" %(beginDate,), fcReceiveDs, 60*60)
        cache.set("%s_fcReceiveFs" %(beginDate,), fcReceiveFs, 60*60)
        cache.set("%s_fcSendDs" %(beginDate,), fcSendDs, 60*60)
        cache.set("%s_fcSendFs" %(beginDate,), fcSendFs, 60*60)

    mscombidy2d.dataset = [
        {"seriesname": u"收到设备数量", "color": "5a885e",
         "data": fcReceiveDs
        },
        {"seriesname": u"传出设备数量", "color": "6F7399",
         "data": [{"value": each}for each in fcSendDs]
        },
        {"seriesname": u"收到的FC文件数", "parentyaxis": "S", "color": "5a885e",
         "data": fcReceiveFs
        },
        {"seriesname": u"传出的FC文件数", "parentyaxis": "S", "color": "6F7399",
         "data": [{"value": each}for each in fcSendFs]
        },
        
    ]
    res = json.dumps(mscombidy2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def add_fc_original(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        send_dt = json.loads(request.POST.get("dt"))

        if data:
            dt = datetime.strptime(str(send_dt), "%Y%m%d")
            collection = db["fc_original"]
            collection.remove({"datetime": dt})
            collection.insert([{"datetime": dt, "fc": i["fc"], "count": int(i["count"])} for i in data])
            return HttpResponse("Update data ok.")
        else:
            return HttpResponse("Empty data.")
    else:
        return HttpResponse("Http method wrong.")
