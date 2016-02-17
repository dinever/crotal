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
    """
    ObjectManager is a implementation of sorted dictionary, I didn't use
    ``collections.OrderedDict`` as it is new in Python 2.7.

    Example usage:

        .. testcode::

            from crotal.models import ObjectManager

            objects = ObjectManager()
            objects['foo'] = 'bar'
    """

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
        if not callable(key):
            sort_key = lambda x: getattr(x, key)
        else:
            sort_key = key
        self._keys.sort(key=lambda x: sort_key(self._objects[x]), reverse=reverse)


class ModelMeta(type):

    def __new__(mcs, name, bases, attrs):
        """
        This metaclass for `Model` adds a ``_fields`` attribute to the host class,
        ``_fields`` contains the fields which should be defined in host class.
        """
        fields = {}
        for attr_name, attr_value in attrs.iteritems():
            if isinstance(attr_value, Field):
                fields[attr_name] = attr_value
        attrs['objects'] = ObjectManager()
        attrs['_fields'] = fields
        attrs['name'] = name
        return super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        if 'PATH' in attrs:
            # Replace '/' with ``os.sep`` so that it will work in windows.
            setattr(cls, 'PATH', [path.replace('/', os.sep) for path in attrs['PATH']])
            del attrs['PATH']
        super(ModelMeta, cls).__init__(name, bases, attrs)


class Model(object):
    """
    This is the model of the data in crotal site. It is a simple ORM in which
    the database layer is replaced with static file reader. The pattern is
    designed to go with Django.

    Example usage:

        .. ::

            from crotal.models import Model
            from crotal.models.fields import CharField


            class Post(Model):
                title = CharField(max_length=8)

            p = Post(title="This is a long title")

            print(p.title)


    We have defined the max length of the title as 8, so the result is:

        .. ::

            This is

    """
    __metaclass__ = ModelMeta

    def __init__(self, **attributes):
        for attr, field in self._fields.iteritems():
            if attr in attributes:
                setattr(self, attr, field.parse(attributes[attr]))
            else:
                for other_name in field.other_names:
                    if other_name in attributes:
                        setattr(self, attr, field.parse(attributes[other_name]))
            if attr not in attributes:
                setattr(self, attr, attributes[attr])
        self.create()

    def create(self):
        """
        This function is called after the model has successfully load the
        documents from the folder indicated, it should be overridden if
        you want to do some extra operation on the data.

        For example, if you want to convert the post content into markdown
        format, then you should define it in the method ``create`` under
        ``Post`` class.
        """
        pass

    def serialize(self):
        return cPickle.dumps(self)

    def to_db(self, absolute_path):
        """
        Convert the data from object into crotal database format for data
        persistence and serialization.

        :param absolute_path: Absolute file path of the source file.
        :return: A dictionary to be stored in crotal database.
        """
        return {
            'content': self.serialize().encode('base64'),
            'last_mod_time': os.path.getmtime(absolute_path),
        }

    @classmethod
    def load(cls, database, config):
        """
        This method loads the static files indicated by ``cls.PATH`` of each
        model, then parse them into objects.

        :param database: A crotal database instance.
        :param config: A configuration instance.
        :return: None
        """
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
        """
        This method classifies the static files into 3 types: ``unmodified``,
        ``modified`` and ``removed`` by comparing the last modified time of
        the file read from file system with the last modified time stored in
        database.
        """
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
    def single_file_on_change(cls, file_path, event_type, config):
        """
        This method is called by the crotal server. If there is a file
        change when the server is running, the server will call this
        method to let the model responding to the change of file.

        :param file_path: The path of the designated file.
        :param event_type: A string indicating the event type, can be
            ``created``, ``modified`` or ``deleted``.
        :param config: A configuration instance.
        :return:
        """
        if event_type in ('created', 'modified'):
            obj = cls.load_single_file(file_path, config)
            if obj:
                cls.objects.add(file_path, obj)
            else:
                logger.error(message="Incorrect file format: {0}".format(file_path))
        elif event_type == 'deleted':
            cls.remove_single_file(file_path)
        if callable(getattr(cls, 'load_extra_items', None)):
            cls.load_extra_items(config)

    @classmethod
    def load_main_items(cls, config):
        """
        This method handles 3 types of source file differently, loads the
        fields of each source file, build objects and add them into the
        object manager.

        If the file is ``unmodified``, then load it from crotal database;
        If the field is ``modified``, then load it from the file system;
        If the field is ``removed``, then remove it from the crotal database;

        As ``unmodified`` file is stored in crotal database which can be
        accessed from memory, loading an ``unmodified`` file can be much faster
        than loading a ``modified`` file from the file system(hard drive).
        This is also known as incremental build, which makes Crotal fast.

        :param config: A configuration instance.
        :return:
        """
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
        """
        This method is called after all static files are load. If you want to
        load some other fields from the files in addition to the main fields,
        please override this function.

        For more information please refer to the implementation of ``models.Post``

        :param config: A configuration instance.
        :return:
        """
        pass

    @classmethod
    def load_single_file(cls, file_path, config):
        """
        This method is used to load a single file from the ``file_path``.

        :param file_path: The path of the designated file.
        :param config: A configuration instance.
        :return: An object of the loaded file.
        """
        return cls.from_file(file_path, config)

    @classmethod
    def remove_single_file(cls, file_path):
        """
        This method is used to remove a single file from the object manager
        and the database.

        :param file_path: The path of the designated file.
        """
        if file_path in cls.objects:
            cls.objects.remove(file_path)
        if file_path in cls._table:
            del cls._table[file_path]

    @classmethod
    def from_db(cls, path, config, row):
        """
        This method is used to load a single object directly from the
        database.

        :param path: Path of the designated file, which is not used.
        :param config: A configuration instance.
        :param row: A dictionary which contains the serialized
            information of the object.
        :return: An object of the designated file.
        """
        serial = row['content'].decode('base64')
        return cPickle.loads(str(serial))

    @classmethod
    def from_file(cls, file_path, config):
        """
        This method is used to load a single object from the file system.

        :param file_path: The path of the designated file.
        :param config: A configuration instance.
        :return: An object of the loaded file.
        """
        with open(file_path, 'r') as f:
            content = f.read().decode('utf8')
        return cls.parse_content(file_path, content, config)

    @classmethod
    def from_text(cls, file_path, text, config):
        """
        This method is used to load a single object from a string.

        :param file_path: The path of the designated file.
        :param text: The string containing object information.
        :param config: A configuration instance.
        :return: The object of the loaded file.
        """
        return cls.parse_content(file_path, text, config)

    @classmethod
    def parse_content(cls, file_path, content, config):
        """
        Parse the content from a string and return an model object.

        :param file_path: The path of the designated file.
        :param content: The string containing object information.
        :param config: A configuration instance.
        :return:
        """
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
            obj = cls.__new__(cls)
            for attr, value in attributes.iteritems():
                setattr(obj, attr, value)
            obj.create()
            return obj
        else:
            logger.error("Can not find header area: {0}".format(file_path))
            return None

    @classmethod
    def parse_attributes(cls, file_path, config, attributes):
        """
        For each attributes read from the static file, find the corresponding
        field and parse the attribute by the ``parse`` method under the field.

        :param file_path: The path of the designated file.
        :param config: A configuration instance.
        :param attributes: Attributes read from the designated file.
        :return: None
        """
        for attr, field in cls._fields.iteritems():
            if attr in attributes:
                attributes[attr] = field.parse(attributes[attr])
            else:
                for other_name in field.other_names:
                    if other_name in attributes:
                        attributes[attr] = field.parse(attributes[other_name])
            if attr not in attributes:
                attributes[attr] = field.parse(None)

    @staticmethod
    def get_file_list(base_dir, path_list):
        """
        This method returns the list of all the source files in the directory
        indicated. Notice that there be multiple paths passed as a list and
        files started with '.' will be ignored.

        :param base_dir: The base directory of the crotal site.
        :param path_list: A list of paths that files will be looked up.
        :return: None
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

