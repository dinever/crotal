from __future__ import print_function, unicode_literals

import os

from crotal.models import Model
from crotal.models.base import ObjectManager
from crotal.models.fields import *


class Static(Model):
    PATH = ['static/', 'themes/{theme}/static/']

    path = CharField()

    @classmethod
    def from_file(cls, file_path, config):
        return cls.parse_content(file_path, config)

    @classmethod
    def parse_content(cls, file_path, config):
        return cls(path = file_path)

    def __init__(self, path=""):
        self.path = path
        self.identify_output_path(self.PATH)

    def generate_url(self):
        url = []
        for item in self.output_path.split(os.path.sep):
            url.append(item)
        return "/".join(url)

    def identify_output_path(self, source_path):
        if isinstance(source_path, list):
            for path in source_path:
                if self.path.startswith(path):
                    self.output_path = os.path.relpath(self.path, path)
        else:
            self.output_path = os.path.relpath(self.path, source_path)
        self.url = self.generate_url()

class Category(object):
    URL_PATTERN = 'categories/:id'

    @classmethod
    def add(cls, name, obj):
        name = name.strip()
        slug = name.lower().replace(' ', '_')
        if hasattr(cls, 'objects'):
            object_manager = getattr(cls, 'objects')
            if slug in object_manager:
                object_manager[slug].insert(obj)
            else:
                object_manager[slug] = cls(name)
                object_manager[slug].insert(obj)
            return object_manager[slug]
        else:
            object_manager = ObjectManager()
            new_instance = cls(name)
            new_instance.insert(obj)
            object_manager.add(slug, new_instance)
            setattr(cls, 'objects', object_manager)
            return new_instance

    def __init__(self, name):
        self.name = name.strip()
        self.id = name.lower().replace(' ', '_')
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

    def insert(self, obj):
        if not filter(lambda x: x.path == obj.path, self.posts):
            self.posts.append(obj)

class Tag(object):
    URL_PATTERN = 'tags/:id'

    @classmethod
    def add(cls, name, obj):
        name = name.strip()
        slug = name.lower().replace(' ', '_')
        if hasattr(cls, 'objects'):
            object_manager = getattr(cls, 'objects')
            if slug in object_manager:
                object_manager[slug].insert(obj)
            else:
                object_manager[slug] = cls(name)
                object_manager[slug].insert(obj)
            return object_manager[slug]
        else:
            object_manager = ObjectManager()
            new_instance = cls(name)
            new_instance.insert(obj)
            object_manager.add(slug, new_instance)
            setattr(cls, 'objects', object_manager)
            return new_instance

    def __init__(self, name):
        self.name = name.strip()
        self.id = name.lower().replace(' ', '_')
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

    @classmethod
    def get_objects(cls):
        return cls.objects.values()

    def generate_url(self):
        url = []
        for item in self.URL_PATTERN.split('/'):
            if item.startswith(':'):
                url.append(getattr(self, item[1:]).lower())
            else:
                url.append(item)
        return '/'.join(url)

    def insert(self, obj):
        if not filter(lambda x: x.path == obj.path, self.posts):
            self.posts.append(obj)


class Archive(object):
    URL_PATTERN = 'archives/:year/:month'

    @classmethod
    def add(cls, datetime, obj):
        new_archive = cls(datetime)
        new_archive.insert(obj)
        if hasattr(cls, 'objects'):
            object_manager = getattr(cls, 'objects')
            if new_archive.__repr__() in object_manager:
                object_manager[new_archive.__repr__()].insert(obj)
            else:
                object_manager[new_archive.__repr__()] = new_archive
        else:
            object_manager = ObjectManager()
            object_manager.add(new_archive.__repr__(), new_archive)
            setattr(cls, 'objects', object_manager)

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

    def insert(self, obj):
        if not filter(lambda x: x.path == obj.path, self.posts):
            self.posts.append(obj)

    def generate_url(self):
        url = []
        for item in self.URL_PATTERN.split('/'):
            if item.startswith(':'):
                url.append(getattr(self, item[1:]).lower())
            else:
                url.append(item)
        return '/'.join(url)
