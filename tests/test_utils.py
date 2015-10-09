from __future__ import unicode_literals, print_function

import os
import unittest

from crotal import utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_generate_path(self):
        path = utils.generate_path('/category/programming/', site_root='/demo/')
        self.assertEqual(path, os.path.join('demo', 'category', 'programming', 'index.html'))

    def test_generate_path_from_file(self):
        path = utils.generate_path('/category/programming/demo.html', site_root='/demo/')
        self.assertEqual(path, os.path.join('demo', 'category', 'programming', 'demo.html'))

    def test_generate_path_without_root(self):
        path = utils.generate_path('/category/programming/')
        self.assertEqual(path, os.path.join('category', 'programming', 'index.html'))

