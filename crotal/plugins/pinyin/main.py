#!/usr/bin/env python
# -*- coding:utf-8 -*-

from .pinyin import PinYin

test = PinYin()
test.load_word()
string = "钓鱼岛是中国的"
print "out: %s" % test.hanzi2pinyin_split(string=string, split="-")
