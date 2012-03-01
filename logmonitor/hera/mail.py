#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage

class SendMail(object):
    def __init__(self, from_addr, to_addr, subject, body):
        self._from_addr = from_addr
        self._to_addr = to_addr
        self._subject = subject
        self._body = body

    def sendmail(self):
        mroot = MIMEMultipart("related")
        mroot["To"] = self._to_addr
        mroot["From"] = self._from_addr
        mroot["Subject"] = self._subject
        mroot.preamble = "NLA App Check"

        malternative = MIMEMultipart("alternative")
        mroot.attach(malternative)

        html = u"""
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
        for key, value in self._body.items():
            if value:
                html = u"%s<h3 class='title'>%s</h3>" %(html, key)
                if value[0].has_key("error"):
                    html = u"%s<table style='border-collapse: collapse; border: 1px solid #000000;'><tr><th>执行检查出错</th></tr><tr><td>%s</td></tr></table>" %(html, value[0].get("error"))
                else:
                    html = u"%s<table style='border-collapse: collapse; border: 1px solid #000000;'><tr><th>文件名字</th><th>本地信息</th><th>服务器信息</th><th>状态</th></tr>" %(html,)
                    for each in value:
                        html = u"%s<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(html, each.get("fname"), each.get("local"), each.get("svn"), each.get("status"))
                    html = u"%s</table>" %(html,)

        html = u"%s</body></html>" %(html,)
        html = MIMEText(html.encode("utf-8"), "html")
        malternative.attach(html)

        s = smtplib.SMTP("corp.chinacache.com")
        to_list = self._to_addr.split(",")
        try:
            s.sendmail(self._from_addr, to_list, mroot.as_string())
        finally:
            s.quit()