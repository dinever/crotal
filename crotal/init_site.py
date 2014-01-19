#!/usr/bin/python

from os import path

from crotal.copy_dir import copy_dir

def init_site(site_name):
    dir = path.dirname(path.abspath(__file__)) + '/init'
    copy_dir(dir, site_name)
