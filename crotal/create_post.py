# -*- coding:utf-8 -*-

import os
import sys
from crotal.models.posts import Post
from crotal.plugins.pinyin.pinyin import PinYin
from datetime import datetime

SAMPLE = """---
title: "%s"
date: %s
categories:
slug: %s
---

"""


def usage():
    print 'Usage:'
    print 'crotal new_post "you title here"'
    print '#You post will be created in _posts/'


def create_post(config):
    flag = 0
    if len(sys.argv) == 1:
        usage()
    elif len(sys.argv) != 1:
        post = Post(config)
        pinyin = PinYin()
        pinyin.load_word()
        string = sys.argv[1]  # Assume that argv[1] is the title user inputed.
        post.title = string
        post.slug = pinyin.hanzi2pinyin_split(string=string, split="-")
        dt = datetime.now()
        post.pub_time = dt.strftime("%Y-%m-%d %H:%M")
        new_post = SAMPLE % (post.title, post.pub_time, post.slug)
        file_title = dt.strftime("%Y-%m-%d") + '-' + post.slug + '.markdown'
        target = os.path.normpath(os.path.join('source/posts', file_title))
        open(target, 'w+').write(new_post)
    else:
        usage()

if __name__ == '__main__':
    create_post()
