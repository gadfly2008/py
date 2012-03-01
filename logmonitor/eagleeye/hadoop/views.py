#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from models import ChannelJob, NameNodeInfo, DataNodeInfo, DataNodePerformance
from utilities import datetime_toString,string_toDatetime,data_format
from datetime import date, datetime, timedelta
from rcms.views import get_channelMap
from flashcharts import MSCombiDY2D, Column3D
import logging
import urllib2
import json

logger = logging.getLogger("eagleeye")

STATUS = {0: "sleep", 4: "waiting", 1: "doing", 2: "successful", 3: "failed", 5: "none"}
ACTION = {0: "play", 1: "stop", 2: "play", 3: "play", 4: "stop"}
DOWNLOAD_API = "http://182.61.128.18:8081/log/download"
HADOOP_API = "http://182.61.128.18:50030/jobdetails.jsp?"

@cache_page(60*5)
def job_list(request):
    context = {}
    beginDate = request.GET.get("beginDate", datetime_toString(date.today()-timedelta(days=1)))
    context["beginDate"] = beginDate
    context["source_size"] = 0
    context["target_size"] = 0
    context["all_tasks"] = 0
    context["waiting_tasks"] = 0
    context["success_tasks"] = 0
    context["failed_tasks"] = 0
    context["doing_tasks"] = 0
    for job in ChannelJob.objects.filter(job_day=string_toDatetime(beginDate)):
        context["source_size"] = context.get("source_size") + job.source_fsize
        context["target_size"] = context.get("target_size") + job.target_fsize
        context["all_tasks"] = context.get("all_tasks") + 1
        if STATUS[job.status] == "waiting":
            context["waiting_tasks"] = context.get("waiting_tasks") + 1
        elif STATUS[job.status] == "doing":
            context["doing_tasks"] = context.get("doing_tasks") + 1
        elif STATUS[job.status] == "successful":
            context["success_tasks"] = context.get("success_tasks") + 1
        elif STATUS[job.status] == "failed":
            context["failed_tasks"] = context.get("failed_tasks") + 1

    context["source_size"] = data_format(context.get("source_size"))
    context["target_size"] = data_format(context.get("target_size"))
    context["status"] = STATUS
    return render_to_response("hadoop/job_list.html", context, context_instance=RequestContext(request))

@cache_page(60*5)
def jobs_detail(request):
    args = {"job_day": string_toDatetime(request.GET.get("beginDate"))}
    customerId = request.GET.get("customerId")
    channelId = request.GET.get("channelId")
    priority = request.GET.get("priority")
    status = request.GET.get("status")

    if customerId != "0":
        args["user_id"] = customerId
    if channelId != "0":
        args["channel_id"] = channelId
    if priority != "-1":
        args["priority"] = priority
    if status != "-1":
        args["status"] = status

    res = {"all_tasks": 0, "publish_size": 0, "waiting_tasks": 0, "success_tasks": 0, "failed_tasks": 0, "doing_tasks": 0, "data": []}
    for job in ChannelJob.objects.filter(**args).order_by("priority"):
        res["all_tasks"] = res.get("all_tasks") + 1
        res["publish_size"] += job.target_fsize
        if STATUS[job.status] == "waiting":
            res["waiting_tasks"] = res.get("waiting_tasks") + 1
        elif STATUS[job.status] == "doing":
            res["doing_tasks"] = res.get("doing_tasks") + 1
        elif STATUS[job.status] == "successful":
            res["success_tasks"] = res.get("success_tasks") + 1
        elif STATUS[job.status] == "failed":
            res["failed_tasks"] = res.get("failed_tasks") + 1
        res["data"].append(
            {"dbId": job.id, "channel_name": job.channel_name, "priority": job.priority,
             "jobId": job.job_id,
             "status": STATUS.get(job.status),
             "channel_id": job.channel_id,
             "source_fline": job.source_fline,
             "source_fsize": data_format(job.source_fsize),
             "target_fline": job.target_fline,
             "target_fsize": data_format(job.target_fsize),
             "update_time": job.update_time.strftime("%Y/%m/%d %H:%M:%S"),
             "action": ACTION.get(job.status),
             "url": "%s/%s/%s/%s/%s" %(DOWNLOAD_API, job.job_day.strftime("%Y%m%d"),job.user_id,job.channel_id,job.pub_format_type),
             "job_url": "%sjobid=%s" %(HADOOP_API, job.job_id)
            }
        )
    res["publish_size"] = data_format(res["publish_size"])
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

def channel_publish(request, channel_id):
    context = {"beginDate": datetime_toString((datetime.today() - timedelta(days=1))),
               "channelId": channel_id}
    return render_to_response("hadoop/channel_publish.html", context, context_instance=RequestContext(request))

def channel_publish_data(request, channel_id):
    beginDate = request.GET.get("beginDate")
    endDate = string_toDatetime(beginDate)-timedelta(days=6)
    channelMap = get_channelMap()

    data = ChannelJob.objects.filter(job_day__lte=string_toDatetime(beginDate),job_day__gte=endDate,channel_id=channel_id).order_by("job_day")
    col3d = Column3D(channelMap[channel_id], u"%s ~ %s" %(datetime_toString(endDate), beginDate))
    dataMap = {}
    for d in data:
        dataMap[d.job_day.strftime("%Y%m%d")] = d.target_fsize
    values = []
    for i in range(6, -1, -1):
        dayKey = (string_toDatetime(beginDate) - timedelta(days=i)).strftime("%Y%m%d")
        if dataMap.has_key(dayKey):
            values.append({"label": "%s" %((string_toDatetime(beginDate) - timedelta(days=i)).strftime("%m/%d")),
                           "value": "%s" %(dataMap[dayKey])})
        else:
            values.append({"label": "%s" %((string_toDatetime(beginDate) - timedelta(days=i)).strftime("%m/%d")),
                           "value": "0"})
    col3d.data = values
    res = json.dumps(col3d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def job_action(request):
    db_id = request.GET.get("dbId")
    action = request.GET.get("action")

    if action == "levelup":
        ChannelJob.objects.filter(id=db_id).update(priority=0, update_time=datetime.now())
        return HttpResponse(json.dumps({"result": 1, "action": action}, ensure_ascii=False, sort_keys=True, indent=4))

    if action == "start":
        try:
            if int(urllib2.urlopen("http://119.188.7.65:5000/job/start/%s" %(db_id,), timeout=30).read()):
                ChannelJob.objects.filter(id=db_id).update(status=1, update_time=datetime.now())
                res = {"result": 1, "action": action}
            else:
                res = {"result": 0, "action": action}
        except Exception, e:
            logger.error(e)
            res = {"result": 0, "action": action}
    elif action == "kill":
        job_id = ChannelJob.objects.get(id=db_id).job_id
        try:
            if int(urllib2.urlopen("http://119.188.7.65:5000/job/kill/%s" %(job_id,), timeout=30).read()):
                ChannelJob.objects.filter(id=db_id).update(status=0, update_time=datetime.now())
                res = {"result": 1, "action": action}
            else:
                res = {"result": 0, "action": action}
        except Exception, e:
            logger.error(e)
            res = {"result": 0, "action": action}
    else:
        res = {"result": 0, "action": action}
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

def job_action_failed(request):
    return render_to_response("hadoop/action_failed.html", context_instance=RequestContext(request))

def jobs_byDay(request):
    cjobs = ChannelJob.objects.filter(job_day=string_toDatetime(request.GET.get("day", datetime_toString(date.today()))))
    res = []
    for job in cjobs:
        res.append({"id": job.id, "user_id": job.user_id, "user_name": job.user_name,
                    "channel_id": job.channel_id, "channel_name": job.channel_name,
                    "priority": job.priority, "source_path": job.source_path,
                    "target_path": job.target_path, "status": job.status, "job_day": datetime_toString(job.job_day),
                    "pub_mime_filter": job.pub_mime_filter, "pub_url_filter": job.pub_url_filter,
                    "pub_way": job.pub_way, "pub_is_filter": job.pub_is_filter, "pub_format_type": job.pub_format_type,
                    "pub_ftp_ip": job.pub_ftp_ip, "pub_ftp_port": job.pub_ftp_port, "pub_ftp_dir": job.pub_ftp_dir,
                    "pub_ftp_user": job.pub_ftp_user, "pub_ftp_passwd": job.pub_ftp_passwd,
        })
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

def get_job(request, dbId):
    try:
        job = ChannelJob.objects.get(id=dbId)
        res = {"id": job.id, "user_id": job.user_id, "user_name": job.user_name,
               "channel_id": job.channel_id, "channel_name": job.channel_name,
               "priority": job.priority, "source_path": job.source_path,
               "target_path": job.target_path, "status": job.status, "job_day": datetime_toString(job.job_day),
               "pub_mime_filter": job.pub_mime_filter, "pub_url_filter": job.pub_url_filter,
               "pub_way": job.pub_way, "pub_is_filter": job.pub_is_filter, "pub_format_type": job.pub_format_type,
               "pub_ftp_ip": job.pub_ftp_ip, "pub_ftp_port": job.pub_ftp_port, "pub_ftp_dir": job.pub_ftp_dir,
               "pub_ftp_user": job.pub_ftp_user, "pub_ftp_passwd": job.pub_ftp_passwd,
        }
        return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))
    except Exception, e:
        logger.error(e)
        return HttpResponse(json.dumps({}, ensure_ascii=False, sort_keys=True, indent=4))

def get_job_detail(request):
    channel_ids = request.GET.get("channelids").strip().split(",")
    job_day = request.GET.get("jobday").strip()

    jobs = ChannelJob.objects.filter(job_day=string_toDatetime(job_day), channel_id__in=channel_ids)
    res = []
    for job in jobs:
        res.append({"id": job.id, "user_id": job.user_id, "user_name": job.user_name,
                    "channel_id": job.channel_id, "channel_name": job.channel_name,
                    "priority": job.priority, "source_path": job.source_path,
                    "target_path": job.target_path, "status": job.status, "job_day": datetime_toString(job.job_day),
                    "pub_mime_filter": job.pub_mime_filter, "pub_url_filter": job.pub_url_filter,
                    "pub_is_filter": job.pub_is_filter, "pub_format_type": job.pub_format_type,
                    "job_id": job.job_id
        })
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

def datanode_performance(request, nodename):
    context = {"beginDate": request.GET.get("beginDate", datetime_toString(date.today())), "device_name": nodename}
    return render_to_response("hadoop/datanode_performance.html", context, context_instance=RequestContext(request))

@cache_page(60*10)
def datanode_performance_data(request, nodename):
    ptype = request.GET.get("type")
    beginDate = request.GET.get("beginDate")
    args = {"datetime__gte": string_toDatetime(beginDate), "datetime__lt": string_toDatetime(beginDate)+timedelta(days=1), "hostname": nodename}
    performance = DataNodePerformance.objects.filter(**args)
    mscombidy2d = MSCombiDY2D("Performance", beginDate)
    if ptype == "cpu":
        mscombidy2d.chart["caption"] = "CPU Monitor"
        mscombidy2d.categories = {"category": [{"name": d.datetime.strftime("%H:%M")} for d in performance]}
        mscombidy2d.dataset = [
            {"seriesname": "CPU US", "parentyaxis": "P", "color": "5a885e",
             "data": [{"value": "%s" %(d.cpu_us,)} for d in performance]
            },
            {"seriesname": "CPU Idle", "parentyaxis": "S", "renderas": "Line", "color": "dca657", "anchorbgcolor": "dca657",
             "data": [{"value": "%s" %(d.cpu_idle,)} for d in performance]
            }
        ]
    elif ptype == "io":
        mscombidy2d.chart["caption"] = "IO Monitor"
        mscombidy2d.categories = {"category": [{"name": d.datetime.strftime("%H:%M")} for d in performance]}
        mscombidy2d.dataset = [
            {"seriesname": "IO Await", "parentyaxis": "P", "color": "5a885e",
             "data": [{"value": "%s" %(d.io_await,)} for d in performance]
            },
            {"seriesname": "IO Idle", "parentyaxis": "S", "renderas": "Line", "color": "dca657", "anchorbgcolor": "dca657",
             "data": [{"value": "%s" %(d.io_idle,)} for d in performance]
            }
        ]
    elif ptype == "memory":
        mscombidy2d.chart["caption"] = "Memory Monitor"
        mscombidy2d.chart["showSecondaryLimits"] = "0"
        mscombidy2d.chart["showDivLineSecondaryValue"] = "0"
        mscombidy2d.categories = {"category": [{"name": d.datetime.strftime("%H:%M")} for d in performance]}
        mscombidy2d.dataset = [
            {"seriesname": "Memory Free", "parentyaxis": "P", "color": "5a885e",
             "data": [{"value": "%s" %(int(d.memory_free)*1024,)} for d in performance]
            }
        ]
    res = json.dumps(mscombidy2d.to_dict(), ensure_ascii=False, sort_keys=True, indent=4)
    return HttpResponse(res)

def parser_args(data):
    args = {"update_time": datetime.now()}
    job_id = data.get("jobid", None)
    job_name = data.get("jobname", None)
    source_fline = data.get("sourcefline", None)
    source_fsize = data.get("sourcefsize", None)
    target_fline = data.get("targetfline", None)
    target_fsize = data.get("targetfsize", None)
    status = data.get("status", None)
    job_execute_time = data.get("jobexecutetime", None)
    description = data.get("description", None)

    if job_id:
        args["job_id"] = job_id
    if job_name:
        args["job_name"] = job_name
    if source_fline:
        args["source_fline"] = source_fline
    if source_fsize:
        args["source_fsize"] = source_fsize
    if target_fline:
        args["target_fline"] = target_fline
    if target_fsize:
        args["target_fsize"] = target_fsize
    if status:
        args["status"] = status
    if job_execute_time:
        args["job_execute_time"] = job_execute_time
    if description:
        args["description"] = description

    return args

def updateJob_dbId(request, dbId):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        args = parser_args(data)
        ChannelJob.objects.filter(id=dbId).update(**args)
        return HttpResponse("Update successfully!")
    else:
        return HttpResponse("Http method wrong.")

def updateJob_jobId(request, jobId):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        args = parser_args(data)
        ChannelJob.objects.filter(job_id=jobId).update(**args)
        return HttpResponse("Update successfully!")
    else:
        return HttpResponse("Http method wrong.")

def jobs_need_update_status(request, jobDay):
    jobs = ChannelJob.objects.filter(status__in=[1,2],job_day=datetime.strptime(jobDay, "%Y%m%d"))
    res = []
    for job in jobs:
        res.append({"id": job.id, "jobId": job.job_id, "status": job.status})
    return HttpResponse(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))

def hadoop_monitor(request):
    namenode = NameNodeInfo.objects.latest("update_time")
    context = {
        "configuredcapacity": data_format(namenode.configured_capacity),
        "presentcapacity": data_format(namenode.present_capacity),
        "dfsremaining": data_format(namenode.dfs_remaining),
        "dfsused": data_format(namenode.dfs_used),
        "dfsusedper": namenode.dfs_usedper,
        "totaldatanode": namenode.total_datanode,
        "deaddatanode": namenode.dead_datanode,
        "updatetime": namenode.update_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    datanodes = []
    for datanode in DataNodeInfo.objects.all():
        datanodes.append([datanode.name, datanode.decommission_status, data_format(datanode.configured_capacity),
                          data_format(datanode.dfs_used), datanode.dfs_usedper,
                          data_format(datanode.dfs_remaining), datanode.dfs_remainingper,
                          data_format(datanode.non_dfs_used), datanode.last_contact.strftime("%Y-%m-%d %H:%M:%S"),
        ])
    context["datanodes"] = datanodes
    return render_to_response("hadoop/hadoop_monitor.html", context, context_instance=RequestContext(request))

def add_namenode_info(request):
    if request.method == "POST":
        try:
            data = json.loads(request.POST.get("data"))
            args = {"update_time": datetime.now(),
                    "configured_capacity": data.get("configuredcapacity"),
                    "present_capacity": data.get("presentcapacity"),
                    "dfs_remaining": data.get("dfsremaining"),
                    "dfs_used": data.get("dfsused"),
                    "dfs_usedper": data.get("dfsusedper"),
                    "total_datanode": data.get("totaldatanode"),
                    "dead_datanode": data.get("deaddatanode"),
            }

            NameNodeInfo.objects.create(**args)
        except Exception, e:
            logger.error(e)
        return HttpResponse("Add successfully!")
    else:
        return HttpResponse("Http method wrong.")

def add_datanode_info(request):
    if request.method == "POST":
        datas = json.loads(request.POST.get("data"))
        for data in datas:
            try:
                args = {"update_time": datetime.now(),
                        "name": data.get("name"),
                        "decommission_status": data.get("decommissionstatus"),
                        "configured_capacity": data.get("configuredcapacity"),
                        "dfs_remaining": data.get("dfsremaining"),
                        "dfs_used": data.get("dfsused"),
                        "dfs_usedper": data.get("dfsusedper"),
                        "dfs_remainingper": data.get("dfsremainingper"),
                        "non_dfs_used": data.get("nondfsused"),
                        "last_contact": data.get("lastcontact"),
                }

                datanode = DataNodeInfo.objects.filter(name=args.get("name"))

                if datanode:
                    datanode.delete()
                DataNodeInfo.objects.create(**args)
            except Exception, e:
                logger.error(e)
        return HttpResponse("Add successfully!")
    else:
        return HttpResponse("Http method wrong.")

def add_datanode_performance(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        args = {}
        try:
            args["hostname"] = data.get("hostname")
            args["datetime"] = datetime.strptime(data.get("datetime"), "%Y-%m-%d %H:%M")
            args["load_user"] = data.get("load_user", "0")
            args["load_average"] = data.get("load_average", "0")
            args["cpu_us"] = data.get("cpu_us", "0")
            args["cpu_idle"] = data.get("cpu_idle", "0")
            args["memory_free"] = data.get("memory_free", "0")
            args["io_await"] = data.get("io_await", "0")
            args["io_idle"] = data.get("io_idle", "0")

            DataNodePerformance.objects.create(**args)
        except Exception, e:
            logger.error(e)

        return HttpResponse("Add datanode performance ok.")
    else:
        return HttpResponse("Http method wrong.")