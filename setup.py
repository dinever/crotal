#coding:utf-8
import os
import sys

from setuptools import setup, find_packages
from crotal import version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "crotal",
    version = version.__version__,
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
    install_requires = ['mako', 'markdown>=2.3.1', 'PyYAML>=3.10','Pygments>=1.6', 'clint>=0.4.1', 'watchdog>=0.8.1'],
    author = "Dinever",
    author_email = 'dingpeixuan911@gmail.com',
    url = "http://github.com/dinever/crotal",
    description = 'A static site framework written in Python. Fast, powerful, and easy as 1, 2, 3.',
    long_description = read('README.md'),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only'
    ],
)
