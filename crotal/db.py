# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import io
import os
import json

from crotal import logger


class Database(object):
    """
    Database is the interface to the file 'db.json'.
    table includes 'posts', 'pages', 'templates', 'static', 'static'.
    """

    @classmethod
    def from_file(cls, path):
        raw_db = json.loads(open(path, 'r').read())
        return cls(raw_db, path)

    def __init__(self, content, path):
        self.raw_db = content
        self._path = path
        self._tables = {}
        for field in self.raw_db:
            self._tables[field] = Table(field, content=self.raw_db[field])

    def __getitem__(self, table):
        return self.get_table(table)

    def get_table(self, table):
        if not table in self._tables:
            self._tables[table] = Table(table, content={})
            logger.info('New table "{0}" created.'.format(table))
            return self._tables[table]
        else:
            return self._tables[table]

    def get_item(self, table, filename):
        return self[table].get(filename, {'content': None})

    def set_item(self, table, filename, item_dict):
        self[table][filename] = item_dict

    def remove_item(self, table, filename):
        if filename in self.db[table]:
            del self[table][filename]
        else:
            logger.warning("Failed to remove from database: {0}, TYPE: {1}".format(filename, table))

    def dump(self):
        json_output = {}
        for table in self._tables:
            json_output[table] = self._tables[table].content
        json_string = json.dumps(json_output, ensure_ascii=False)
        return json_string

    def save(self):
        io.open(self._path, 'w+', encoding='utf8').write(self.dump())


class Table(object):

    def __init__(self, table_name, content=None):
        self._table_name = table_name
        self._mapping = {} if not content else content

    @property
    def content(self):
        return self._mapping

    def __repr__(self):
        return '<%s:%s Keys:%r>' % (
            self.__class__.__name__,
            self._table_name,
            self._mapping.keys()
        )

    def __getitem__(self, item):
        return self._mapping.get(item)

    def __contains__(self, key):
        return key in self._mapping

    def __setitem__(self, key, value):
        self._mapping[key] = value

    def __delitem__(self, key):
        """Remove an item from the cache dict.
        Raise a `KeyError` if it does not exist.
        """
        try:
            del self._mapping[key]
        except KeyError, e:
            raise KeyError

    def keys(self):
        return self._mapping.keys()

    def get(self, key, default=None):
        """Return an item from the cache dict or `default`"""
        try:
            return self[key]
        except KeyError:
            return default
