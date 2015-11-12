# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest
import datetime

from crotal.models import Post


SAMPLE_POST = """
---
title: A Sample Post
date: 2010-01-01 10:00
categories: Sample, Test
tags: Unit Test
slug: a-sample-post
---

This is the content of a post for test.

"""

SAMPLE_POST_WITH_WRONG_FORMAT = """
---
title: A Sample Post
date: 2010-01-01 10:00
categories:Sample, Test
tags: Unit Test
slug: a-sample-post
---

This is the content of a post for test.
"""


class FakeConfig(object):
    permalink = ":title"
    author = "John Doe"


class TestPost(unittest.TestCase):

    def setUp(self):
        self.config = FakeConfig()
        Post.config = self.config
        self.sample_path = 'source/posts/sample.md'
        self.post = Post.from_text(self.sample_path, SAMPLE_POST, self.config)

    def test_post_with_wrong_format(self):
        post = Post.from_text(self.sample_path, SAMPLE_POST_WITH_WRONG_FORMAT, self.config,)
        self.assertIsNone(post)

    def test_post_categories(self):
        self.assertEqual(self.post.raw_categories, ['Sample', 'Test'])

    def test_post_tags(self):
        self.assertEqual(self.post.raw_tags, ['Unit Test'])

    def test_date(self):
        self.assertEqual(self.post.date, datetime.datetime(2010, 1, 1, 10, 00))

    def test_url(self):
        self.assertEqual(self.post.url, 'a-sample-post/')

    def test_url_with_different_permalink(self):
        self.config.permalink = "blog/:category/:year/:month/:day/:title"
        post = Post.from_text(self.sample_path, SAMPLE_POST, self.config)
        self.assertEqual(post.url, "blog/sample/2010/01/01/a-sample-post/")

