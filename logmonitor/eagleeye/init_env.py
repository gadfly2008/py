#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from os import walk, remove
from os.path import join

if __name__ == "__main__":
    for rootdir, dirnames, files in walk("."):
        for f in files:
            if f.endswith("pyc"):
                remove(join(rootdir, f))