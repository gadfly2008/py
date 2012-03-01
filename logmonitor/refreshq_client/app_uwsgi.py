#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ["DJANGO_SETTINGS_MODULE"] = "refreshq_client.settings"

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()