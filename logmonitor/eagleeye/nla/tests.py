#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from datetime import datetime
from pymongo import Connection
from django.conf import settings
from models import Directory, Block
import json
import time

connection = Connection()
db = connection[settings.DATABASES["default"]["TEST_NAME"]]

class NLAStatisticClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.dt = "2011-08-14"
        self.nlafc = db["nlafc_%s" %(self.dt.replace("-",""))]
        db.drop_collection("nlafc_%s" %(self.dt.replace("-","")))
        self.channelnla = db["channelnla_%s" %(self.dt.replace("-",""))]
        db.drop_collection("channelnla_%s" %(self.dt.replace("-","")))

    def test_add_nalstatistic_success(self):
        nlafcs = [
            {"nlasn": "100", "fcsn": "200", "fcount": "100", "fsize": "80", "datetime": self.dt},
            {"nlasn": "101", "fcsn": "202", "fcount": "101", "fsize": "81", "datetime": self.dt}
        ]
        channelnlas = [
            {"channelId":"19691","nlasn":"010754H576","size":150080,"userId":"2216", "datetime": self.dt},
            {"channelId":"19692","nlasn":"010754H576","size":150081,"userId":"2217", "datetime": self.dt},
        ]

        response = self.c.post("/nla/nlafc/add/", {"data": json.dumps(nlafcs, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add data ok.")
        time.sleep(2)
        self.assertEqual(self.nlafc.count(), 2)

        response = self.c.post("/nla/channelnla/add/", {"data": json.dumps(channelnlas, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add data ok.")
        time.sleep(2)
        self.assertEqual(self.channelnla.count(), 2)

    def test_update_nalstatistic_success(self):
        nlafcs = [
            {"nlasn": "100", "fcsn": "200", "fcount": 100, "fsize": 80, "datetime": self.dt},
            {"nlasn": "101", "fcsn": "202", "fcount": 101, "fsize": 81, "datetime": self.dt}
        ]
        channelnlas = [
            {"channelId": "30", "userId": "1","nlasn": "100", "size": 80, "datetime": self.dt},
            {"channelId": "40", "userId": "2","nlasn": "101", "size": 60, "datetime": self.dt}
        ]

        self.c.post("/nla/nlafc/add/", {"data": json.dumps(nlafcs, ensure_ascii=False, sort_keys=True, indent=4)})
        response = self.c.post("/nla/nlafc/add/", {"data": json.dumps(nlafcs, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add data ok.")
        self.assertEqual(self.nlafc.count(), 2)
        data1 = self.nlafc.find_one({"nlasn": "100"})
        self.assertEqual(data1["fsize"], 160)
        self.assertEqual(data1["fcount"], 200)
        data2 = self.nlafc.find_one({"nlasn": "101"})
        self.assertEqual(data2["fsize"], 162)
        self.assertEqual(data2["fcount"], 202)

        self.c.post("/nla/channelnla/add/", {"data": json.dumps(channelnlas, ensure_ascii=False, sort_keys=True, indent=4)})
        response = self.c.post("/nla/channelnla/add/", {"data": json.dumps(channelnlas, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add data ok.")
        time.sleep(5)
        self.assertEqual(self.channelnla.count(), 2)
        data1 = self.channelnla.find_one({"channelId": "30"})
        self.assertEqual(data1["size"], 160)
        data2 = self.channelnla.find_one({"channelId": "40"})
        self.assertEqual(data2["size"], 120)

class UpdateChannelNlaTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.dt = "2011-08-14"
        self.collection = db["channelnla_%s" %(self.dt.replace("-",""))]
        db.drop_collection("channelnla_%s" %(self.dt.replace("-","")))

    def test_update_channelnla_success(self):
        channelfcs = [
            {"channelId": "30", "userId": "1","nlasn": "100", "size": 1, "datetime": self.dt},
            {"channelId": "40", "userId": "2","nlasn": "101", "size": 2, "datetime": self.dt}
        ]

        output_count = [
            {"channelId": "30", "nlasn": "100", "count": 20, "datetime": self.dt},
            {"channelId": "40", "nlasn": "101", "count": 30, "datetime": self.dt}
        ]

        upload_count = [
            {"channelId": "30", "nlasn": "100",  "count": 50, "datetime": self.dt},
            {"channelId": "40", "nlasn": "101",  "count": 60, "datetime": self.dt}
        ]

        self.c.post("/nla/channelnla/add/", {"data": json.dumps(channelfcs, ensure_ascii=False, sort_keys=True, indent=4)})

        time.sleep(5)

        response = self.c.post("/nla/channelnla/output/count/update/", {"data": json.dumps(output_count, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Update data ok.")
        self.assertEqual(self.collection.count(), 2)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["outputcount"], 20)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["outputcount"], 30)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["size"], 1)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["size"], 2)

        response = self.c.post("/nla/channelnla/output/count/update/", {"data": json.dumps(output_count, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Update data ok.")
        self.assertEqual(self.collection.count(), 2)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["outputcount"], 40)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["outputcount"], 60)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["size"], 1)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["size"], 2)

        response = self.c.post("/nla/channelnla/upload/count/update/", {"data": json.dumps(upload_count, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Update data ok.")
        self.assertEqual(self.collection.count(), 2)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["uploadcount"], 50)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["uploadcount"], 60)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["size"], 1)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["size"], 2)

        response = self.c.post("/nla/channelnla/upload/count/update/", {"data": json.dumps(upload_count, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Update data ok.")
        self.assertEqual(self.collection.count(), 2)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["uploadcount"], 100)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["uploadcount"], 120)
        self.assertEqual(self.collection.find_one({"nlasn": "100"})["size"], 1)
        self.assertEqual(self.collection.find_one({"nlasn": "101"})["size"], 2)

class NLADataClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.datetime = "2011-08-31 14:30"
        self.nla_performance = db["nla_performance_%s" %(datetime.now().strftime("%Y%m%d"))]
        self.nla_masterdir = db["nla_masterdir_%s" %(datetime.now().strftime("%Y%m%d"))]
        self.nla_health = db["nla_health"]
        db.drop_collection("nla_performance_%s" %(datetime.now().strftime("%Y%m%d")))
        db.drop_collection("nla_masterdir_%s" %(datetime.now().strftime("%Y%m%d")))
        db.drop_collection("nla_health")

    def test_add_nladata_success(self):
        dirs = [{"hostname": "30", "name": "/aa","count": "100", "size": "200", "level": "0", "datetime": self.datetime, "vsftp": "open", "health": 100},
                {"hostname": "30", "name": "/bb","count": "100", "size": "200", "level": "0", "datetime": self.datetime, "vsftp": "open", "health": 100}
        ]
        blocks = [{"hostname": "30", "name": "/aa","used": "45", "level": "0"},
                {"hostname": "30", "name": "/bb","used": "100", "level": "0"}
        ]

        performance = [{"hostname": "30", "datetime": self.datetime, "load_user": "1", "load_average": "1", "cpu_us": "1", "cpu_idle": "1", "memory_free": "1", "io_await": "1", "io_idle": "1"}]


        args = {"dir": dirs, "block": blocks, "performance": performance, "masterdir": {"datetime": self.datetime, "size": 200, "hostname": "30"}}
        self.c.post("/nla/data/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        response = self.c.post("/nla/data/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add nla data ok.")
        self.assertEqual(len(Directory.objects.all()), 2)
        self.assertEqual(len(Block.objects.all()), 2)

        time.sleep(3)
        self.assertEqual(self.nla_performance.count(), 2)
        self.assertEqual(self.nla_masterdir.count(), 2)
        self.assertEqual(self.nla_masterdir.find_one()["size"], 200)
        self.assertEqual(self.nla_health.count(), 2)
        self.assertEqual(self.nla_health.find_one()["health"], 100)