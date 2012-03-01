#!/bin/bash

/usr/local/bin/python manage.py runfcgi method=prefork socket=/tmp/eagleeye.sock pidfile=/tmp/eagleeye.pid maxrequests=128 maxchildren=8