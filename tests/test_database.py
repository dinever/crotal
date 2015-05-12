# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function

import os
import unittest

from crotal.db import Table, Database
from base import BaseTest


class TestDatabase(BaseTest):

    def setUp(self):
        self.db_file_path = 'db.json'
        self.db = Database(dict(), self.db_file_path)

    def test_database_init(self):
        pass

    def test_table_set(self):
        self.db['table']['test_key'] = 'test_value'
        self.assertEqual(self.db.get_item('table', 'test_key'), 'test_value')

    def test_table_del(self):
        self.db['table']['test_key'] = 'test_value'
        del self.db['table']['test_key']
        self.assertIsNone(self.db.get_item('table', 'test_key'))

    def test_db_dump(self):
        self.db['table']['test_key'] = 'test_value'
        self.assertEqual(self.db.dump(), '{"table": {"test_key": "test_value"}}')

    def test_db_get_none(self):
        self.assertIsNone(self.db['table'].get('test_key_2'))


if __name__ == "__main__":
    unittest.main()
