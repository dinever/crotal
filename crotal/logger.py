# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from clint.textui import colored

def info(message):
    print("{0} {1}".format(colored.green('[info]'.format(info)),  message))

def warning(message):
    print("{0} {1}".format(colored.yellow('[warning]'.format(info)),  message))

def error(message):
    print("{0} {1}".format(colored.red('[error]'.format(info)),  message))

def success(message):
    print("{0} {1}".format(colored.blue('[success]'.format(info)),  message))

def yellow_text(info='', message=''):
    if info:
        print("{0} {1}".format(colored.yellow('[{0}]'.format(info)),  message))
    else:
        print(colored.yellow(message))

def red_text(info='', message=''):
    if info:
        print("{0} {1}".format(colored.red('[{0}]'.format(info)),  message))
    else:
        print(colored.red(message))

def blue_text(info='', message=''):
    if info:
        print("{0} {1}".format(colored.blue('[{0}]'.format(info)),  message))
    else:
        print(colored.blue(message))

def green_text(info='', message=''):
    colored_text = colored.green('[{0}]'.format(info))
    if info:
        print(colored.green('[{0}] '.format(info)) + message.encode('utf8'))
    else:
        print(colored.green(message))

def info_input(message):
    return raw_input(colored.green('[{0}]: '.format(message)))
