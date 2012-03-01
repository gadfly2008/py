#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import smtplib
import mimetypes
import os
import platform
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email import encoders
from os.path import join

class SendMail(object):
    def __init__(self, body):
        self._from_addr = "downloadclient@chinacache.com"
        self._to_addr = "zhigang.li@chinacache.com,yachuan.chen@chinacache.com,gen.li@chinacache.com,peng.xu@chinacache.com"
        self._body = body

    def send_with_attachment(self):
        m = MIMEMultipart()
        m["To"] = self._to_addr
        m["From"] = self._from_addr
        m["Subject"] = u"日志下载客户端日志"
        attachment = join(os.getcwd(), "logs", "core.log")

        m.attach(MIMEText(self._body, "plain", "utf-8"))
        ctype, encoding = mimetypes.guess_type(attachment)
        if ctype:
            maintype, subtype = ctype.split("/", 1)
        else:
            maintype = "text"
            subtype = "plain"

        fp = open(attachment, "rb")
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(msg)
        msg.add_header("Content-Disposition", "attachment", filename = attachment.split("\\")[-1] if platform.system() == "Windows" else attachment.split("/")[-1])
        m.attach(msg)

        s = smtplib.SMTP("corp.chinacache.com")
        to_list = self._to_addr.split(",")
        try:
            s.sendmail(self._from_addr, to_list, m.as_string())
        finally:
            s.quit()

    def send_with_normal(self):
        m = MIMEMultipart()
        m["To"] = self._to_addr
        m["From"] = self._from_addr
        m["Subject"] = u"日志下载客户端下载异常"

        m.attach(MIMEText(self._body.encode("utf-8"), "plain", "utf-8"))

        s = smtplib.SMTP("corp.chinacache.com")
        to_list = self._to_addr.split(",")
        try:
            s.sendmail(self._from_addr, to_list, m.as_string())
        finally:
            s.quit()