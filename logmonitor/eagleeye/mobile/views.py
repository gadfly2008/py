#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
import logging
import urllib
import urllib2

logger = logging.getLogger("eagleeye")

def index(request):
    api = "http://sms.chinacache.com/ReceiverSms"
    username = "1295410062943JJQ"
    password = "nocbrother"
    content = request.POST.get("content", "")
    phone_nums = request.POST.get("phonenum", "")

    if not content or not phone_nums:
        return HttpResponse("Missing args.")

    data = {"username": username, "password": password, "mobile": phone_nums, "content": content.encode("utf-8")}
    res = urllib2.urlopen(api, urllib.urlencode(data))
    return HttpResponse(res.read())