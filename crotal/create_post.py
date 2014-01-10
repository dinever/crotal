#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from crotal.models.posts import Posts
from crotal.plugins.pinyin.pinyin import PinYin
from datetime import datetime

author = 'dinever'

SAMPLE = """---
title: "%s"
date: %s
categories:
slug: %s
---

"""

def create_post():
    flag = 0
    if len(sys.argv) == 1:
        print 'Usage: deploy'

    elif len(sys.argv) != 1:
        post = Posts()
        test = PinYin()
        test.load_word()
        string = sys.argv[1]
        dt = datetime.now()
        post.title = string
        post.slug = test.hanzi2pinyin_split(string=string, split="-")
        post.pub_time = dt.strftime("%Y-%m-%d %H:%M")
        new_post = SAMPLE % (post.title, post.pub_time, post.slug)
        file_title = dt.strftime("%Y-%m-%d") + '-' + post.slug + '.markdown'
        open('_posts/' + file_title, 'w+').write(new_post)
    else:
        usraccount = sys.argv[1]
        passwd = sys.argv[2]

if __name__ == '__main__':
    create_post()
