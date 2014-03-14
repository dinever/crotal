#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from crotal.views import Views
from crotal.plugins.pinyin.pinyin import PinYin
from datetime import datetime

author = 'dinever'

SAMPLE = """---
layout: page.html
title: "%s"
date: %s
url: %s
description: %s
---
"""

def create_page(config):
    flag = 0
    if len(sys.argv) == 1:
        title = raw_input('Page Title:')
        url = raw_input('Page URL(For example, /foo/bar/):')
        description = raw_input('Page Description(For SEO):')
        pinyin = PinYin()
        slug = pinyin.hanzi2pinyin_split(string=title, split="-")
        dt = datetime.now()
        date = dt.strftime("%Y-%m-%d %H:%M")
        target = os.path.normpath(os.path.join("source/pages", slug + '.markdown'))
        open(target, 'w+').write(SAMPLE % (title, date, url, description))
        print 'You can check browse the page by ' + config.url + '/' + url + ' After generating the site.'

    elif len(sys.argv) != 1:
        open(os.path.join('_posts', file_title), 'w+').write(new_post)
    else:
        usraccount = sys.argv[1]
        passwd = sys.argv[2]

if __name__ == '__main__':
    create_page()
