#!/usr/bin/python

from os import path

def get_init_dierctory():
    dir = path.dirname(path.abspath(__file__)) + '/init'
    return dir
