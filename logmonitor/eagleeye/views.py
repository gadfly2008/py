#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.db.models import Sum
from django.shortcuts import render_to_response
from datetime import datetime, timedelta
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from publisher.models import LogPublishTotal
from utilities import data_format
from django.conf import settings
import logging

logger = logging.getLogger("eagleeye")
db = settings.MONGODB

@cache_page(60*60)
def index(request):
    today = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    yesterday = datetime.strptime((datetime.today()-timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")
    third_day = datetime.strptime((datetime.today()-timedelta(days=2)).strftime("%Y-%m-%d"), "%Y-%m-%d")

    day_list = [today.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"), third_day.strftime("%Y-%m-%d")]
    data_list = [0, 0, 0]

    thirdday_collection = db["nlafc_%s" %(third_day.strftime("%Y%m%d"))]
    yesterday_collection = db["nlafc_%s" %(yesterday.strftime("%Y%m%d"))]
    today_collection = db["nlafc_%s" %(today.strftime("%Y%m%d"))]

    today_original = 0
    for d in today_collection.find():
        today_original += d["fsize"]

    yesterday_original = 0
    for d in yesterday_collection.find():
        yesterday_original += d["fsize"]

    thirdday_original = 0
    for d in thirdday_collection.find():
        thirdday_original += d["fsize"]

    data = LogPublishTotal.objects.filter(datetime__gte=third_day, datetime__lte=today).order_by("datetime").values("datetime").annotate(total=Sum("size"))
    for d in data:
        i = day_list.index(d["datetime"].strftime("%Y-%m-%d"))
        data_list[i] = d["total"]

    context = {"third": third_day.strftime("%m/%d"), "second": yesterday.strftime("%m/%d"), "first": today.strftime("%m/%d"),
               "third_original": data_format(thirdday_original),
               "third_publish": data_format(data_list[2]),
               "second_original": data_format(yesterday_original),
               "second_publish": data_format(data_list[1]),
               "first_original": data_format(today_original),
               "first_publish": data_format(data_list[0]),
    }
    
    return render_to_response("index.html", context, context_instance=RequestContext(request))