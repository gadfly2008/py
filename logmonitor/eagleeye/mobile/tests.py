#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client

class SendMessageClientTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def test_send_message_fail(self):
        response = self.c.post("/mobile/", {"content": "test", "phonenum": "13699267182"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.strip(), "8 0 来源ip地址未被授权")