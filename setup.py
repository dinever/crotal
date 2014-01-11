#coding:utf-8
import os
import sys

from setuptools import setup, find_packages


setup(
    name = "crotal",
    version = "0.0.1",
    packages = find_packages(),

    include_package_data = True,

    entry_points = {
        'console_scripts' : [
            'crotal = crotal.main:main'
        ],
    },
    package_data = {
        'crotal' : [ '*.data' ]
    },
    install_requires = ['Jinja2==2.7.1','markdown==2.3.1','unipath==1.0','PyYAML==3.10'],
    author = "Dinever",
    author_email = 'dingpeixuan911@gmail.com',
    url = "http://www.dinever.com",
    description = 'a demo for setuptools',
)
