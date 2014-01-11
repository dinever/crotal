#!/usr/bin/python

import os

from unipath import Path

def get_init_dierctory():
    dir = Path(__file__).ancestor(1).absolute() + '/init'
    return dir
