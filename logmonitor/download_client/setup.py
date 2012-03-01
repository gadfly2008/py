#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*", "email", "sendmail"]

options = {"py2exe":
                {
                   "compressed": 1,
                   "optimize": 2,
                   "includes": includes,
                   "bundle_files": 1,
                   "packages": ["email", "sendmail"],
               }
}

setup(
    version = "0.1.0",
    description = "download client",
    name = "download client",
    options = options,
    zipfile = None,
    console=[{"script": "main.py", "icon_resources": [(0, "download.ico")]}],
    data_files = [
            ("conf", ["conf/main.cfg", "conf/logging.conf"]),
            ("logs", ["logs/core.log"]),
    ]
)