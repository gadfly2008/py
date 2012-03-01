#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from models import LogPublishDelay, LogPublish, LogPublishTotal
import json

class LogPublishClientTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        self.today = "20110412"

    def test_add_logpublish_success(self):
        args = [{"uId": "1", "cId": "100","datetime": self.today, "size": 100},
                {"uId": "2", "cId": "200","datetime": self.today, "size": 200}]

        response = self.c.post("/publisher/publish/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add log publish ok.")
        self.assertEqual(len(LogPublish.objects.all()), 2)

    def test_update_logpublish_success(self):
        args1 = [{"uId": "1", "cId": "100","datetime": self.today, "size": 100},
                {"uId": "2", "cId": "200","datetime": self.today, "size": 200}]
        args2 = [{"uId": "1", "cId": "100","datetime": self.today, "size": 200},
                {"uId": "2", "cId": "200","datetime": self.today, "size": 400}]

        self.c.post("/publisher/publish/add/", {"data": json.dumps(args1, ensure_ascii=False, sort_keys=True, indent=4)})
        response = self.c.post("/publisher/publish/add/", {"data": json.dumps(args2, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add log publish ok.")
        self.assertEqual(len(LogPublish.objects.all()), 2)
        data1 = LogPublish.objects.get(customer_id=1)
        self.assertEqual(data1.size, 200)
        data2 = LogPublish.objects.get(customer_id=2)
        self.assertEqual(data2.size, 400)

class TotalPublishClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.today = "20110412"

    def test_add_total_publish(self):
        args = [{"source": "storage-1", "today": self.today, "size": 100}]
        response = self.c.post("/publisher/total/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add total publish ok.")
        self.assertEqual(len(LogPublishTotal.objects.all()), 1)
        logpublish_total = LogPublishTotal.objects.get(source="storage-1")
        self.assertEqual(logpublish_total.size, 100)


    def test_update_total_publish(self):
        args = [{"source": "storage-1", "today": self.today, "size": 100}]
        self.c.post("/publisher/total/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        logpublish_total = LogPublishTotal.objects.get(source="storage-1")
        self.assertEqual(logpublish_total.size, 100)
        args = [{"source": "storage-1", "today": self.today, "size": 300}]
        self.c.post("/publisher/total/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        logpublish_total = LogPublishTotal.objects.get(source="storage-1")
        self.assertEqual(logpublish_total.size, 300)

class PublishDelayClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.today = "2011041203"

    def test_add_publish_delay(self):
        args = [{"source": "fs", "datetime": self.today, "size": 100, "user_name": "fs"},
                {"source": "fs", "datetime": self.today, "size": 101, "user_name": "kk"},
        ]
        response = self.c.post("/publisher/publishdelay/add/", {"data": json.dumps(args, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add publish delay ok.")
        self.assertEqual(len(LogPublishDelay.objects.all()), 2)