#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from models import Directory, Block
import json


class LcerClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.today = "2011-04-15 14:12"

    def test_add_publish_delay(self):
        dirs = [{"hostname": "fs", "datetime": self.today, "size": 100, "name": "fs", "count": 123},
                {"hostname": "dd", "datetime": self.today, "size": 100, "name": "fsdfs", "count": 123},
        ]

        blocks = [{"hostname": "fs", "used": 12, "name": "fsdfs"},
                  {"hostname": "cc", "used": 88, "name": "fsdfs"},
        ]
        response = self.c.post("/lcer/data/add/", {"data": json.dumps({"dir": dirs, "block": blocks}, ensure_ascii=False, sort_keys=True, indent=4)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "Add lc data ok.")
        self.assertEqual(len(Directory.objects.all()), 2)
        self.assertEqual(len(Block.objects.all()), 2)
