#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from datetime import datetime
from models import ChannelJob, NameNodeInfo, DataNodeInfo, DataNodePerformance
import json

class GetJobClientTestCase(TestCase):
    fixtures = ["hadoop.yaml"]

    def setUp(self):
        self.c = Client()

    def test_get_job_success(self):
        response = self.c.get("/hadoop/job/30/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data)
        self.assertEqual(data.get("status"), 0)
        self.assertEqual(data.get("id"), 1)
        self.assertEqual(data.get("user_id"), 10)

    def test_get_job_none(self):
        response = self.c.get("/hadoop/job/100000/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data)

class UpdateJobIdClientTestCase(TestCase):
    fixtures = ["hadoop.yaml"]

    def setUp(self):
        self.c = Client()
        self.update_time = datetime.now()

    def test_update_job_jobid_success(self):
        data = {"jobname": "test", "status": 5, "sourcefline": 200, "sourcefsize": 200,
                "targetfline": 200, "targetfsize": 200, "jobexecutetime": 200, "description": "test",
        }

        response = self.c.post("/hadoop/job/jobid/30/update/", {"data": json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Update successfully!")
        self.assertEqual(len(ChannelJob.objects.all()), 4)
        job = ChannelJob.objects.get(job_id=30)
        self.assertEqual(job.job_name, data.get("jobname"))
        self.assertEqual(job.status, data.get("status"))
        self.assertEqual(job.source_fline, data.get("sourcefline"))
        self.assertEqual(job.source_fsize, data.get("sourcefsize"))
        self.assertEqual(job.target_fline, data.get("targetfline"))
        self.assertEqual(job.target_fsize, data.get("targetfsize"))
        self.assertEqual(job.job_execute_time, data.get("jobexecutetime"))
        self.assertEqual(job.description, data.get("description"))

class UpdateDbIdClientTestCase(TestCase):
    fixtures = ["hadoop.yaml"]

    def setUp(self):
        self.c = Client()
        self.update_time = datetime.now()

    def test_update_job_dbid_success(self):
        data = {"jobid": "10101", "jobname": "test", "status": 5, "sourcefline": 200, "sourcefsize": 200,
                "targetfline": 200, "targetfsize": 200, "jobexecutetime": 200, "description": "test",
        }

        response = self.c.post("/hadoop/job/dbid/1/update/", {"data": json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Update successfully!")
        self.assertEqual(len(ChannelJob.objects.all()), 4)
        job = ChannelJob.objects.get(id=1)
        self.assertEqual(job.job_id, data.get("jobid"))
        self.assertEqual(job.job_name, data.get("jobname"))
        self.assertEqual(job.status, data.get("status"))
        self.assertEqual(job.source_fline, data.get("sourcefline"))
        self.assertEqual(job.source_fsize, data.get("sourcefsize"))
        self.assertEqual(job.target_fline, data.get("targetfline"))
        self.assertEqual(job.target_fsize, data.get("targetfsize"))
        self.assertEqual(job.job_execute_time, data.get("jobexecutetime"))
        self.assertEqual(job.description, data.get("description"))

class GetStatusJobsClientTestCase(TestCase):
    fixtures = ["hadoop.yaml"]

    def setUp(self):
        self.c = Client()

    def test_get_status_job_success(self):
        response = self.c.post("/hadoop/jobs/status/20110612/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

        response = self.c.post("/hadoop/jobs/status/20110611/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

class NameNodeClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def test_create_namenode_success(self):
        args = {
                "configuredcapacity": 10998021779456,
                "presentcapacity": 10394028538727,
                "dfsremaining": 8301784334336,
                "dfsused": 2092244204391,
                "dfsusedper": 20.13,
                "totaldatanode": 7,
                "deaddatanode": 0,
        }

        response = self.c.post("/hadoop/monitor/namenode/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)

        response = self.c.post("/hadoop/monitor/namenode/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(NameNodeInfo.objects.all()), 2)

class DataNodeClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def test_create_datanode_success(self):
        args = [{
                "name": "119.188.7.70:50010",
                "decommissionstatus": "Normal",
                "configuredcapacity": 10998021779456,
                "dfsremaining": 8301784334336,
                "dfsused": 2092244204391,
                "dfsusedper": 20.13,
                "dfsremainingper": 20.13,
                "nondfsused": 45333417984,
                "lastcontact": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                "name": "119.188.7.66:50010",
                "decommissionstatus": "Normal",
                "configuredcapacity": 10998021779456,
                "dfsremaining": 8301784334336,
                "dfsused": 2092244204391,
                "dfsusedper": 20.13,
                "dfsremainingper": 20.13,
                "nondfsused": 45333417984,
                "lastcontact": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
        ]

        response = self.c.post("/hadoop/monitor/datanode/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)

        response = self.c.post("/hadoop/monitor/datanode/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(DataNodeInfo.objects.all()), 2)

    def test_add_datanode_performance_success(self):
        args = {"hostname": "30", "datetime": "2011-09-09 12:10", "load_user": "1",
                "load_average": "1", "cpu_us": "1", "cpu_idle": "1", "memory_free": "1",
                "io_await": "1", "io_idle": "1"
        }

        response = self.c.post("/hadoop/monitor/datanode/performance/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(DataNodePerformance.objects.all()), 1)