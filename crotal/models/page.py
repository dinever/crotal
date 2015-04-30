# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from markdown import markdown

from crotal.models import Model


class Page(Model):

    def __init__(self, path, config, title, url, content, **extras):
        self.path = path
        self.title = title
        self.url = url[1:] if url.startswith('/') else url
        self.content = markdown(content, extensions=['fenced_code', 'codehilite', 'tables'])
        for name, value in extras.iteritems():
            setattr(self, name, value)
