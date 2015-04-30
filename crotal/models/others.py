from __future__ import print_function, unicode_literals

import os

from crotal.models import Model, Post


class Static(Model):

    def __init__(self, path, config):
        self.path = path
        self.url = ''
        self.output_path = ''

    def generate_url(self):
        url = []
        for item in self.output_path.split(os.path.sep):
            url.append(item)
        return "/".join(url)

    @classmethod
    def from_file(cls, path, config):
        return cls.from_text(path, config, None)

    @classmethod
    def from_text(cls, path, config, text):
        return cls(path, config)

    def identify_output_path(self, source_path):
        if isinstance(source_path, list):
            for path in source_path:
                if self.path.startswith(path):
                    self.output_path = os.path.relpath(self.path, path)
        else:
            self.output_path = os.path.relpath(self.path, source_path)
        self.url = self.generate_url()

class Category(object):
    URL_PATTERN = 'categories/:name'

    def __init__(self, name):
        self.name = name.strip()
        self.url = self.generate_url()
        self.posts = []

    def __eq__(self, other):
        return other.url == self.url

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.name)

    def __delitem__(self, key):
        for post in self.posts:
            if post.file_path == key:
                self.posts.remove(post)

    def generate_url(self):
        url = []
        for item in self.URL_PATTERN.split('/'):
            if item.startswith(':'):
                url.append(getattr(self, item[1:]).lower())
            else:
                url.append(item)
        return '/'.join(url)

    def add(self, post):
        if isinstance(post, Post):
            self.posts.append(post)


class Tag(Category):
    URL_PATTERN = 'tags/:name'


class Archive(object):
    URL_PATTERN = 'archives/:year/:month'

    def __init__(self, datetime):
        self.datetime = datetime
        self.year = datetime.strftime("%Y")
        self.month = datetime.strftime("%m")
        self.url = self.generate_url()
        self.posts = []

    def __repr__(self):
        return '{0}: {1}-{2}'.format(self.__class__.__name__, self.datetime.year, self.datetime.month)

    def __gt__(self, other):
        if self.datetime > other.datetime:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.datetime < other.datetime:
            return True
        else:
            return False

    def __eq__(self, other):
        return other.datetime.year == self.datetime.year and other.datetime.month == self.datetime.month

    def generate_url(self):
        url = []
        for item in self.URL_PATTERN.split('/'):
            if item.startswith(':'):
                url.append(getattr(self, item[1:]).lower())
            else:
                url.append(item)
        return '/'.join(url)
