#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.conf import settings
import logging
import json

logger = logging.getLogger("eagleeye")
db = settings.MONGODB

def get_customerMap():
    if cache.get("customerMap"):
        return cache.get("customerMap")
    else:
        customerMap = {}
        for customer in db.rcms_customer.find():
            customerMap[customer["customerId"]] = customer["name"]
        cache.set("customerMap", customerMap, 60*60*4)
        return customerMap

def get_channelMap():
    if cache.get("channelMap"):
        return cache.get("channelMap")
    else:
        channelMap = {}
        for channel in db.rcms_channel.find():
            channelMap[channel["channelId"]] = channel["name"]
        cache.set("channelMap", channelMap, 60*60*4)
        return channelMap

def get_device_map():
    if cache.get("deviceMap"):
        return cache.get("deviceMap")
    else:
        deviceMap = {}
        for device in db.rcms_device.find():
            deviceMap[device["sn"]] = device["name"]
        cache.set("deviceMap", deviceMap, 60*60*4)
        return deviceMap

@cache_page(60*60*4)
def search_nla_devices(request):
    name = request.GET.get("name").upper()
    devices = db.rcms_device.find({"name": {"$regex": r"%s%s" %("^", name)}, "app": "NLA"}, {"name": 1, "sn": 1, "_id": 0})[0:10]
    data = [device for device in devices]
    return HttpResponse(json.dumps({"nlas": data}, ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*60*4)
def search_fc_devices(request):
    name = request.GET.get("name").upper()
    devices = db.rcms_device.find({"name": {"$regex": r"%s%s" %("^", name)}, "app": "FC"}, {"name": 1, "sn": 1, "_id": 0})[0:10]
    data = [device for device in devices]
    return HttpResponse(json.dumps({"fcs": data}, ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*60*4)
def search_customers(request):
    name = request.GET.get("name")
    customers = db.rcms_customer.find({"name": {"$regex": r"%s%s" %("^", name)}}, {"name": 1, "customerId": 1, "_id": 0})[0:10]
    data = [customer for customer in customers]
    return HttpResponse(json.dumps({"customers": data}, ensure_ascii=False, sort_keys=True, indent=4))

@cache_page(60*60*4)
def search_channels(request):
    name = request.GET.get("name")
    channels = db.rcms_channel.find({"name": {"$regex": r"%s%s" %("^", name)}}, {"name": 1, "channelId": 1, "_id": 0})[0:10]
    data = [channel for channel in channels]
    return HttpResponse(json.dumps({"channels": data}, ensure_ascii=False, sort_keys=True, indent=4))