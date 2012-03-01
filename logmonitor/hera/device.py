#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json

class Device(object):
    def __init__(self, recorder):
        self.hostname = recorder[u"devName"]
        self.ip = recorder[u"devAdminIP"]
        self.port = recorder.get(u"devAdminPort", 22)
        self.user = recorder.get(u"user", "root")
        self.password = recorder.get(u"password", None)

    def _set_devName(self, name):
        self._devName = name
    def _get_devName(self):
        return self._devName
    def _set_devAdminIP(self, ip):
        self._devAdminIP = ip
    def _get_devAdminIP(self):
        return self._devAdminIP
    def _set_devAdminPort(self, port):
        self._devAdminPort = int(port)
    def _get_devAdminPort(self):
        return int(self._devAdminPort)
    def _set_user(self, user):
        self._user = user
    def _get_user(self):
        return self._user
    def _set_password(self, password):
        self._password = password
    def _get_password(self):
        return self._password

    hostname = property(_get_devName,_set_devName)
    ip = property(_get_devAdminIP,_set_devAdminIP)
    port = property(_get_devAdminPort,_set_devAdminPort)
    user = property(_get_user,_set_user)
    password = property(_get_password,_set_password)

def get_nlaDevices(devices):
    result = []
    api = "http://rcmsapi.chinacache.com:36000/app/name/NLA/devices/search?name="
    for d in devices.split(";"):
        opener = urllib2.urlopen("%s%s" %(api, d.strip()))
        for recorder in json.loads(opener.read()):
            result.append(Device(recorder))

    return result

def get_devices(api, test_devices=None):
    devices = []
    if test_devices:
        tlist = [each.strip() for each in open(test_devices).readlines()]
    else:
        tlist = []
    opener = urllib2.urlopen(api)
    for recorder in json.loads(opener.read()):
        if recorder["devStatus"] == "OPEN" and recorder["devName"] not in tlist:
            devices.append(Device(recorder))

    return devices

def get_device_by_file(f):
    devices = []
    recorder = {}
    for d in open(f):
        recorder[u"devName"],recorder[u"devAdminIP"],recorder[u"devAdminPort"],recorder[u"user"],recorder[u"password"] = d.strip().split(" ")
        devices.append(Device(recorder))

    return devices