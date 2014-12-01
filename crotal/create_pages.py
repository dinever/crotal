#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from datetime import datetime

from crotal.plugins.pinyin.pinyin import PinYin
from crotal.config import config

author = 'dinever'

SAMPLE = """---
layout: page.html
title: "%s"
date: %s
url: %s
description: %s
---

## A demo page!

This is a demo page.
"""

def create_page():
    title = raw_input('Page Title:')
    url = raw_input('Page URL(For example, /foo/bar/):')
    description = raw_input('Page Description:')
    pinyin = PinYin()
    slug = pinyin.hanzi2pinyin_split(string=title, split="-")
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M")
    target = os.path.join(
        config.pages_dir,
            slug + '.markdown')
    open(target, 'w+').write(SAMPLE % (title, date, url, description))
    print 'You can browse the page by ' + config.url + url + ' After generating the site.'

if __name__ == '__main__':
    create_page()
