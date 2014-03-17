#!/usr/bin/python

from os import path

from crotal.copy_dir import copy_dir


def init_site(site_name):
    curr = path.dirname(path.abspath(__file__))
    dir = path.join(curr, "init")
    copy_dir(dir, site_name)
