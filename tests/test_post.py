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

SAMPLE_POST_SERIALIZED = \
    'Y2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAxCihjY3JvdGFsLm1vZGVscy5wb3N0ClBvc3QKcDIK\n' \
    'Y19fYnVpbHRpbl9fCm9iamVjdApwMwpOdFJwNAooZHA1ClMncmF3X2NhdGVnb3JpZXMnCnA2Cihs\n' \
    'cDcKVlNhbXBsZQpwOAphVlRlc3QKcDkKYXNTJ2F1dGhvcicKcDEwClZKb2huIERvZQpwMTEKc1Mn\n' \
    'dGFncycKcDEyCihscDEzCnNTJ3VybCcKcDE0ClZhLXNhbXBsZS1wb3N0LwpwMTUKc1MndGl0bGUn\n' \
    'CnAxNgpTJ0EgU2FtcGxlIFBvc3QnCnAxNwpzUydmcm9udF9jb250ZW50JwpwMTgKVjxwPlRoaXMg\n' \
    'aXMgdGhlIGNvbnRlbnQgb2YgYSBwb3N0IGZvciB0ZXN0LjwvcD4KcDE5CnNTJ2NvbnRlbnQnCnAy\n' \
    'MApnMTkKc1MncmF3X3RhZ3MnCnAyMQoobHAyMgpWVW5pdCBUZXN0CnAyMwphc1MncHViX3RpbWUn\n' \
    'CnAyNApjZGF0ZXRpbWUKZGF0ZXRpbWUKcDI1CihTJ1x4MDdceGRhXHgwMVx4MDFcblx4MDBceDAw\n' \
    'XHgwMFx4MDBceDAwJwp0UnAyNgpzUydpbWFnZXMnCnAyNwoobHAyOApzUydwYXRoJwpwMjkKVnNv\n' \
    'dXJjZS9wb3N0cy9zYW1wbGUubWQKcDMwCnNTJ3NsdWcnCnAzMQpTJ2Etc2FtcGxlLXBvc3QnCnAz\n' \
    'MgpzUydjYXRlZ29yaWVzJwpwMzMKKGxwMzQKc2Iu\n'


class FakeConfig(object):
    permalink = ":title"
    author = "John Doe"


class TestPost(unittest.TestCase):

    def setUp(self):
        self.config = FakeConfig()
        self.sample_path = 'source/posts/sample.md'
        self.post = Post.from_text(self.sample_path, self.config, SAMPLE_POST)

    def test_post_with_wrong_format(self):
        post = Post.from_text(self.sample_path, self.config, SAMPLE_POST_WITH_WRONG_FORMAT)
        self.assertIsNone(post)

    def test_post_categories(self):
        self.assertEqual(self.post.raw_categories, ['Sample', 'Test'])

    def test_post_tags(self):
        self.assertEqual(self.post.raw_tags, ['Unit Test'])

    def test_pub_time(self):
        self.assertEqual(self.post.pub_time, datetime.datetime(2010, 1, 1, 10, 00))

    def test_url(self):
        self.assertEqual(self.post.url, 'a-sample-post/')

    def test_url_with_different_permalink(self):
        self.config.permalink = "blog/:category/:year/:month/:day/:title"
        post = Post.from_text(self.sample_path, self.config, SAMPLE_POST)
        self.assertEqual(post.url, "blog/sample/2010/01/01/a-sample-post/")

    def test_serialize(self):
        print([self.post.serialize().encode('base64')])
        self.assertEqual(self.post.serialize().encode('base64'), SAMPLE_POST_SERIALIZED)


