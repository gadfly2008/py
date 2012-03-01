#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import paramiko
import socket
from os.path import join, dirname

paramiko.util.log_to_file("%s/paramiko.log" %(join(dirname(__file__), "logs")), level=40)

class Connection(object):
    def __init__(self, host, port=22, user="root", password=None, private_key="/root/ker/ldc", kpassword="maint_app"):
        self._sftp_live = False
        self._sftp = None
        self._transport_live = False
        self._transport = None

        self._host = host
        self._username = user
        self._password = password
        self._private_key = private_key
        self._kpassword = kpassword
        self._port = port

        logging.config.fileConfig("%s/conf/logging.conf" %(dirname(__file__)))
        logging.getLogger("paramiko")

    def _transport_connect(self):
        if not self._transport_live:
            socket.setdefaulttimeout(60)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._host, self._port))
            self._transport = paramiko.Transport(sock)
            if self._password:
                self._transport.connect(username=self._username, password=self._password)
            else:
                key = paramiko.DSSKey.from_private_key_file(self._private_key, self._kpassword)
                self._transport.connect(username=self._username, pkey=key)

            self._transport_live = True

    def _sftp_connect(self):
        if not self._transport_live:
            self._transport_connect()
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def put(self, localpath, remotepath=None):
        if not remotepath:
            remotepath = localpath
        self._sftp_connect()
        self._sftp.put(localpath, remotepath)

    def mkdir(self, remotepath, mode=511):
        self._sftp_connect()
        self._sftp.mkdir(remotepath, mode)

    def get(self, remotepath, localpath=None):
        if not localpath:
            localpath = remotepath
        self._sftp_connect()
        self._sftp.get(remotepath, localpath)

    def remove(self, remotepath):
        self._sftp_connect()
        self._sftp.remove(remotepath)

    def rename(self, old, new):
        self._sftp_connect()
        self._sftp.rename(old, new)

    def listdir(self, remotepath="."):
        self._sftp_connect()
        return self._sftp.listdir(remotepath)

    def execute(self, command):
        self._transport_connect()
        channel = self._transport.open_session()
        channel.settimeout(120)
        channel.exec_command(command)

        output = channel.makefile("rb", -1).readlines()
        if output:
            return {"status": "success", "output": output}
        else:
            error = channel.makefile_stderr("rb", -1).readlines()
            if error:
                return {"status": "error", "output": error}
            else:
                return {"status": "success", "output": ""}

    def has_path(self, path):
        subpath = path.split("/")[-1]
        parentpath = "/".join(path.split("/")[0:-1])
        if not parentpath:
            parentpath = "/"
        try:
            if subpath in self.listdir(parentpath):
                return True
            else:
                return False
        except Exception, e:
            print e
            return False

    def has_content(self, content, dfile):
        cmd = "cat %s | grep \'%s\'" %(dfile, content)
        res = self.execute(cmd)
        if res["output"]:
            return True
        else:
            return False

    def close(self):
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
        if self._transport_live:
            self._transport.close()
            self._transport_live = False