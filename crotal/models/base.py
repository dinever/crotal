# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re
import yaml
import cPickle

from crotal import logger
from crotal.models.fields import *

ENCODING = 'base64'


class ObjectManager(object):

    def __init__(self):
        self._keys = []
        self._objects = {}

    def __contains__(self, item):
        return item in self._keys

    def __getitem__(self, item):
        return self._objects[item]

    def __setitem__(self, key, value):
        if key not in self._objects:
            self._keys.append(key)
        self._objects[key] = value

    def add(self, key, value):
        if key in self._keys:
            self._objects[key] = value
        else:
            self._keys.append(key)
            self._objects[key] = value

    def get(self, key, default=None):
        return self._objects.get(key, default)

    def remove(self, key):
        if key in self._keys:
            self._keys.remove(key)
            del self._objects[key]

    def all(self):
        return [self._objects[key] for key in self._keys]

    def sort(self, key, reverse=False):
        sort_key = lambda x: getattr(x, key)
        self._keys.sort(key=lambda x: sort_key(self._objects[x]), reverse=reverse)


class BaseModel(type):

    def __new__(cls, name, bases, attrs):
        return super(BaseModel, cls).__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):

        fields = {}
        for attr_name, attr_value in attrs.iteritems():
            if isinstance(attr_value, Field):
                fields[attr_name] = attr_value
        for attr_name, field in fields.iteritems():
            delattr(cls, attr_name)
        setattr(cls, '_fields', fields)
        setattr(cls, 'name', name)
        setattr(cls, 'objects', ObjectManager())
        super(BaseModel, cls).__init__(name, bases, attrs)


class Model():
    __metaclass__ = BaseModel

    def __init__(self, **attributes):
        for attr, value in attributes.iteritems():
            setattr(self, attr, value)
        self.create()

    def create(self):
        pass

    def serialize(self):
        return cPickle.dumps(self)

    def to_db(self, absolute_path):
        return {
            'content': self.serialize().encode('base64'),
            'last_mod_time': os.path.getmtime(absolute_path),
        }

    @classmethod
    def load(cls, database, config, update_data):
        cls.config = config
        if isinstance(cls.PATH, list):
            cls.PATH = [path.format(**config.__dict__) for path in cls.PATH]
        elif isinstance(cls.PATH, str):
            cls.PATH = [cls.PATH]
        cls._table = database.get_table(cls.__name__)
        cls.file_list = cls.get_file_list(config.base_dir, cls.PATH)
        cls.classify_files()
        cls.load_main_items(config)
        cls.load_extra_items(config)

    @classmethod
    def classify_files(cls):
        db_file_list = cls._table.content
        cls.modified_file_list = list(set(cls.file_list) - set(db_file_list))
        cls.unmodified_file_list = list(set(db_file_list) - (set(db_file_list) - set(cls.file_list)))
        cls.removed_file_list = list(set(db_file_list) - set(cls.file_list))
        for file_path in cls.unmodified_file_list:
            absolute_file_path = os.path.join(cls.config.base_dir, file_path)
            last_mod_time = os.path.getmtime(absolute_file_path)
            last_mod_time_in_db = cls._table.get(file_path)['last_mod_time']
            if last_mod_time != last_mod_time_in_db:
                cls.modified_file_list.append(file_path)
                cls.unmodified_file_list.remove(file_path)

    @classmethod
    def load_main_items(cls, config):
        for file_path in cls.modified_file_list:
            obj = cls.load_single_file(file_path, config)
            if obj:
                cls.objects.add(file_path, obj)
            else:
                logger.error(message="Incorrect file format: {0}".format(file_path))

        for file_path in cls.unmodified_file_list:
            cls.objects.add(file_path, Model.from_db(file_path, cls.config, cls._table[file_path]))

        for file_path in cls.removed_file_list:
            cls.remove_single_file(file_path)

        for obj in cls.objects.all():
            absolute_path = os.path.join(config.base_dir, obj.path)
            cls._table[obj.path] = obj.to_db(absolute_path)

    @classmethod
    def load_extra_items(cls, config):
        pass

    @classmethod
    def load_single_file(cls, file_path, config):
        item = cls.from_file(file_path, config)
        return item

    @classmethod
    def from_db(cls, path, config, row):
        serial = row['content'].decode('base64')
        return cPickle.loads(str(serial))

    @classmethod
    def from_file(cls, file_path, config):
        with open(file_path, 'r') as f:
            content = f.read().decode('utf8')
        return cls.parse_content(file_path, content, config)

    @classmethod
    def from_text(cls, file_path, text, config):
        return cls.parse_content(file_path, text, config)

    @classmethod
    def parse_content(cls, file_path, content, config):
        header = re.compile(r'---[\s\S]*?---').findall(content)
        if header:
            try:
                attributes = yaml.load(header[0].replace('---', ''))
            except yaml.YAMLError, e:
                logger.error("Wrong format inside the header area: {0}".format(file_path))
                return None
            attributes['content'] = content.replace(header[0], '', 1)
            attributes['path'] = file_path
            cls.parse_attributes(file_path, config, attributes)
            return cls(**attributes)
        else:
            logger.error("Can not find header area: {0}".format(file_path))
            return None

    @classmethod
    def parse_attributes(cls, file_path, config, attributes):
        for attr, field in cls._fields.iteritems():
            if attr in attributes:
                attributes[attr] = field.parse(attributes[attr])
            else:
                for other_name in field.other_names:
                    if other_name in attributes:
                        attributes[attr] = field.parse(attributes[other_name])

    @staticmethod
    def get_file_list(base_dir, path_list):
        """
        This method returns the list of all the source files in the directory
        indicated. Notice that file started with '.' will not be
        included.
        """
        file_list = []
        for path in path_list:
            absolute_path = os.path.join(base_dir, path)
            for dir_, _, files in os.walk(absolute_path):
                for file_name in files:
                    absolute_file = os.path.join(dir_, file_name)
                    if not file_name.startswith('.'):
                        file_path = os.path.relpath(absolute_file, base_dir)
                        file_list.append(file_path)
        return file_list

    @classmethod
    def single_file_on_change(cls, file_path, event_type, config):
        if event_type in ('created', 'modified'):
            obj = cls.load_single_file(file_path, config)
            if obj:
                cls.objects.add(file_path, obj)
            else:
                logger.error(message="Incorrect file format: {0}".format(file_path))
        elif event_type == 'deleted':
            cls.remove_single_file(file_path, config)
        if callable(getattr(cls, 'load_extra_items', None)):
            cls.load_extra_items(config)

    @classmethod
    def remove_single_file(cls, file_path):
        if file_path in cls.objects:
            cls.objects.remove(file_path)
        del cls._table[file_path]
