#coding:utf-8
import os
import sys

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "crotal",
    version = "0.8.0",
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
    install_requires = ['mako','markdown>=2.3.1','PyYAML>=3.10','Pygments>=1.6', 'clint>=0.4.1', 'watchdog>=0.8.1'],
    author = "Dinever",
    author_email = 'dingpeixuan911@gmail.com',
    url = "http://github.com/dinever/crotal",
    description = 'A static site generator written in python, Simple, Easy and Fast.',
    long_description = read('README'),
)
