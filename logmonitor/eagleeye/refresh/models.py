#!/usr/local/bin/python
# -*- coding: utf-8 -*-

class Queue(object):
    def __init__(self, d):
        self._name = d["name"]
        self._m_ready = d["m_ready"]
        self._m_unacknowledged = d["m_unacknowledged"]

    def __get_name(self):
        return self._name
    def __get_m_ready(self):
        return self._m_ready
    def __get_m_unacknowledged(self):
        return self._m_unacknowledged

    name = property(__get_name)
    mready = property(__get_m_ready)
    munacknowledged = property(__get_m_unacknowledged)