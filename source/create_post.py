#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from _models.posts import Posts
from _plugins.pinyin.pinyin import PinYin
from _models.posts import Posts
from datetime import datetime
import settings

author = 'dinever'

SAMPLE = """---
title: "%s"
date: %s
category:
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
