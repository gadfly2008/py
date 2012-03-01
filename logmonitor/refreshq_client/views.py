#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
import json
import subprocess
import logging

logger = logging.getLogger("myLogger")

def queue_query(request):
    data = []
    cmd = "/usr/local/rabbitmq_server-2.6.1/sbin/rabbitmqctl   list_queues name messages_ready messages_unacknowledged"
    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    if p.returncode:
        logger.error("Query queue error %s" %(stderrdata,))
    else:
        result = stdoutdata.split("\n")[1:-2]
        for r in result:
            q_name, messages_ready, messages_unacknowledged = r.split("\t")
            data.append({"name": q_name, "m_ready": messages_ready, "m_unacknowledged": messages_unacknowledged})
    
    return HttpResponse(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))