# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import io
import os
import json

from crotal import logger


class Database(object):
    """
    Database is the interface to the file 'db.json'.
    """
    @classmethod
    def from_file(cls, path):
        """
        Read the database from the path argument.
        :param path: The file path of the designated database file.
        :return: The database object.
        """
        try:
            raw_db = json.loads(open(path, 'r').read())
        except (ValueError, IOError):
            raw_db = {}
        return cls(path, content=raw_db)

    def __init__(self, path, content=None):
        """
        Initalize a new database object.

        :param path: Indicating the path of the file that this database will
            be written to when saving the database.
        :param content: Content of the database if needed to predefine.
        :return: None
        """
        if content:
            self.raw_db = content
        else:
            self.raw_db = {}
        self._path = path
        self._tables = {}
        for field in self.raw_db:
            self._tables[field] = Table(field, content=self.raw_db[field])

    def __getitem__(self, table):
        """
        Fetch a ``table`` from the database.

        :param table: Name of the table acquired.
        :return: A ``table`` object.
        """
        return self.get_table(table)

    def get_table(self, table):
        """
        Get a table object, same to ``self.__getitem__``.

        :param table: Name of the table acquired.
        :return: A ``table`` object.
        """
        if table not in self._tables:
            self._tables[table] = Table(table, content={})
            logger.info('New table "{0}" created.'.format(table))
            return self._tables[table]
        else:
            return self._tables[table]

    def get_item(self, table, key):
        """
        Get the value directly from the database based on key and table name.

        :param table: Name of the table acquired.
        :param key: Name of the key in the indicated table.
        :return: The corresponding value stored in the table.
        """
        return self[table].get(key, {'content': None})

    def set_item(self, table, key, value):
        """
        Set the entry directly from the database based on key and table name.

        :param table: Name of the table acquired.
        :param key: Name of the key in the indicated table.
        :value value: Value to be set in the table.
        :return: The corresponding value stored in the table.
        """
        self[table][key] = value

    def remove_item(self, table, key):
        """
        Remove the entry directly from the database based on key and table name.

        :param table: Name of the table acquired.
        :param key: Name of the key in the indicated table.
        :value value: Value to be set in the table.
        :return: The corresponding value stored in the table.
        """
        if key in self.raw_db[table]:
            del self[table][key]
        else:
            logger.warning("Failed to remove from database: {0}, TYPE: {1}".format(key, table))

    def dumps(self):
        """
        Similar to ``json.dumps``.
        """
        json_output = {}
        for table in self._tables:
            json_output[table] = self._tables[table].content
        json_string = json.dumps(json_output, ensure_ascii=False)
        return json_string

    def save(self):
        """
        Write the content of the database to the file indicated by ``self._path``
        in json format.
        :return:
        """
        io.open(self._path, 'w+', encoding='utf8').write(self.dumps())


class Table(object):

    """
    Table is a wrapper of dictionary. The usage is the same as ``dict``.
    """

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
        try:
            return self[key]
        except KeyError:
            return default
