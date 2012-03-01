#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
import zipfile
import gzip
import logging
from django.http import HttpResponse
from cStringIO import StringIO
from django.shortcuts import render_to_response

HADOOP_API = "hadoop.chinacache.net:50075"
logger = logging.getLogger("myLogger")

def pub_file_size(url):
    try:
        request = urllib2.Request("http://%s/%s" %(HADOOP_API, url))
        request.add_header("Accept-encoding", "gzip")
        opener = urllib2.build_opener()
        f = opener.open(request)
        compressedstream = StringIO(f.read())
        return compressedstream
    except Exception, e:
        logger.error(e)
        return 0

def index(request):
    return render_to_response("base.html")

def response_zip(request, pubDate, userId, channelId, ptype):
    buffer = StringIO()
    outputer = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    filename = "%s_%s_%s" %(channelId, pubDate, ptype)

    for i in range(24):
        if i < 10:
            url = "streamFile?filename=/out/%s/%s/%s/0%s.gz" %(pubDate, userId, channelId, i)
        else:
            url = "streamFile?filename=/out/%s/%s/%s/%s.gz" %(pubDate, userId, channelId, i)

        data = pub_file_size(url)
        if data:
            inputer = gzip.GzipFile(fileobj=data)
            outputer.writestr("%s_%s.log" %(filename, i), inputer.read())

    outputer.close()
    buffer.flush()

    ret_zip = buffer.getvalue()
    buffer.close()
    response = HttpResponse(mimetype="application/zip")
    response["Content-Disposition"] = "attachment; filename=%s.zip" %(filename, )
    response["Content-Length"] = len(ret_zip)
    response.write(ret_zip)

    return response

def response_gzip(request, pubDate, userId, channelId, ptype):
    buffer = StringIO()
    outputer = gzip.GzipFile(mode="wb", fileobj=buffer, compresslevel=1)
    
    for i in range(24):
        if i < 10:
            url = "streamFile?filename=/out/%s/%s/%s/0%s.gz" %(pubDate, userId, channelId, i)
        else:
            url = "streamFile?filename=/out/%s/%s/%s/%s.gz" %(pubDate, userId, channelId, i)

        data = pub_file_size(url)
        if data:
            inputer = gzip.GzipFile(fileobj=data)
            outputer.write(inputer.read())

    outputer.close()
    buffer.flush()

    ret_gzip = buffer.getvalue()
    buffer.close()
    response = HttpResponse(mimetype="application/x-gzip")
    response["Content-Encoding"] = "gzip"
    response["Content-Disposition"] = "attachment; filename=%s_%s_%s.gz" %(channelId, pubDate, ptype)
    response["Content-Length"] = len(ret_gzip)
    response.write(ret_gzip)

    return response