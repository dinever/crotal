# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest
from datetime import datetime

from crotal.models import Page

SAMPLE_PAGE = """
---
title: A Sample Post
date: 2010-01-01 10:00
url: /unit/test/
---

This is the content of a post for test.
"""

SAMPLE_PAGE_WITH_WRONG_FORMAT = """
---
title: A Sample Post
date:2010-01-01 10:00
url: /unit/test/
---

This is the content of a post for test.
"""

class FakeConfig(object):
    permalink = ":title"
    author = "John Doe"


class TestPost(unittest.TestCase):

    def setUp(self):
        self.config = FakeConfig()
        self.sample_path = 'source/posts/sample.md'
        self.page = Page.from_text(self.sample_path, SAMPLE_PAGE, self.config)

    def test_page_with_wrong_format(self):
        page = Page.from_text(self.sample_path, SAMPLE_PAGE_WITH_WRONG_FORMAT, self.config)
        self.assertIsNone(page)

    def test_page_url(self):
        self.assertEqual('/unit/test/', self.page.url)

    def test_date(self):
        self.assertEqual(self.page.date, datetime.datetime(2010, 1, 1, 10, 00))
