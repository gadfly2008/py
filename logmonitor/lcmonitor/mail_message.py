#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import smtplib
import urllib
import urllib2
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage

class SendMail(object):
    def __init__(self, body):
        self._from_addr = "nocalert@chinacache.com"
        self._to_addr = "log@chinacache.com,nocvoice@chinacache.com"
        self._subject = u"【一级故障】 日志发布系统告警 马上通知李根"
        self._body = body

    def sendmail(self):
        mroot = MIMEMultipart("related")
        mroot["To"] = self._to_addr
        mroot["From"] = self._from_addr
        mroot["Subject"] = self._subject
        mroot.preamble = "LC monitor"

        malternative = MIMEMultipart("alternative")
        mroot.attach(malternative)

        html = """
        <!doctype html>
        <html lang=\"en\">
            <head>
                <meta charset="utf-8"/>
                <title>Log Publisher Monitor</title>
                <style type='text/css'>
                    body {
                       font-family: Arial,Helvetica,'lucida grande',tahoma,'bitstream vera sans',sans-serif;
                    }
                    a {
                        text-decoration: none;
                    }
                    .title {
                        font-size: 18px;
                        color: #575746;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }
                    table tr {
                       text-align: left;
                    }
                    table tr th {
                        font-size: 15px;
                        padding: 5px;
                        background-color: #d5e0cb;
                        color: #5a4e5c;
                        border: 1px solid #000000;
                    }
                    table tr td {
                        font-size: 13px;
                        padding: 6px 6px 6px 4px;
                        background-color: #fffcf3;
                        color: #55544f;
                        border: 1px solid #000000;
                    }
                </style>
            </head>
            <body>"""
        html = "%s<h3 class='title'>%s</h3>" %(html, self._body.get("hostname"))

        if self._body["dirs"]:
            html = u"%s<table style='border-collapse: collapse; border: 1px solid #000000;'> \
            <tr><th>目录报警</th><th>结果</th></tr>" %(html,)
            for key, value in self._body["dirs"].items():
                html = "%s<tr><td>%s</td><td>%s</td></tr>" %(html, key, value)
            html = "%s</table>" %(html,)
            html = "%s<br/>" %(html,)
        if self._body["blocks"]:
            html = u"%s<table style='border-collapse: collapse; border: 1px solid #000000;'> \
            <tr><th>分区报警</th><th>使用率</th></tr>" %(html,)
            for key, value in self._body["blocks"].items():
                html = "%s<tr><td>%s</td><td>%s%s</td></tr>" %(html, key, value, "%")
            html = "%s</table>" %(html,)

        html = "%s</body></html>" %(html,)
        html = MIMEText(html.encode("utf-8"), "html")
        malternative.attach(html)

        s = smtplib.SMTP("corp.chinacache.com")
        to_list = self._to_addr.split(",")
        try:
            s.sendmail(self._from_addr, to_list, mroot.as_string())
        finally:
            s.quit()

class SendMessage(object):
    def __init__(self, content):
        self._api = "http://sms.chinacache.com/ReceiverSms"
        self._username = "1295410062943JJQ"
        self._password = "nocbrother"
        self._mobiles = "13801289719;13910840138;13811436953"
        self._content = content

    def sendmessage(self):
        body = u"设备: %s\n" %(self._content.get("hostname"))
        for key,value in self._content["dirs"].items():
            if key:
                body = u"%s%s: %s\n" %(body, key, value)
        for key,value in self._content["blocks"].items():
            if key:
                body = u"%s%s: 使用了 %s%s\n" %(body, key, value, "%")

        data = {"username": self._username, "password": self._password,
                "mobile": self._mobiles, "content": body.encode("utf-8")}
        res = urllib2.urlopen(self._api, urllib.urlencode(data))
        return res.read()
