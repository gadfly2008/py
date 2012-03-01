#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage

def data_format(data):
    KB = 1024
    MB = 1024*1024
    GB = 1024*1024*1024

    if data < KB:
        return "%s" %(data,)
    elif float(data)/KB < KB:
        return "%.2f%s" %(float(data)/KB, "KB")
    elif float(data)/MB < KB:
        return "%.2f%s" %(float(data)/MB, "MB")
    elif float(data)/GB < KB:
        return "%.2f%s" %(float(data)/GB, "GB")

class SendMail(object):
    def __init__(self, from_addr, to_addr, body, today, lastweek):
        self._from_addr = from_addr
        self._to_addr = to_addr
        self._subject = u"日志发布大小监控"
        self._body = body
        self._today = today.split(" ")[0]
        self._lastweek = lastweek.split(" ")[0]

    def sendmail(self):
        mroot = MIMEMultipart("related")
        mroot["To"] = self._to_addr
        mroot["From"] = self._from_addr
        mroot["Subject"] = self._subject
        mroot.preamble = "Log Publisher Monitor"

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
        for key, value in self._body.items():
            html = """
                %s
                <h3 class='title'>%s</h3>
            """ %(html, key)
            html = u"""
                %s
                <table style='border-collapse: collapse; border: 1px solid #000000;'>
                    <tr>
                        <th>Channel</th>
                        <th>%s</th>
                        <th>%s</th>
                        <th>Rate</th>
                    </tr>
            """ %(html, self._today, self._lastweek)
            for each in value:
                html = """
                    %s
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%.2f %s</td>
                    </tr>
                """ %(html, each.get("channelname"),data_format(each.get("today_size")),data_format(each.get("lastday_size")),each.get("rate"),"%")
            html = """%s</table>""" %(html,)
        html = """
            %s
            </body></html>
        """ %(html,)

        html = MIMEText(html.encode("utf-8"), "html")
        malternative.attach(html)

        s = smtplib.SMTP("corp.chinacache.com")
        to_list = self._to_addr.split(",")
        try:
            s.sendmail(self._from_addr, to_list, mroot.as_string())
        finally:
            s.quit()