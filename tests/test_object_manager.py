# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest

from crotal.models import ObjectManager


class Number(object):
    """
    A class for testing purpose.
    """
    def __init__(self, num):
        self.num = num

class TestObjectManager(unittest.TestCase):

    def setUp(self):
        self.objects = ObjectManager()

    def test_add(self):
        self.objects.add('one', 1)
        self.objects.add('two', 2)
        self.objects['three'] =  3
        self.assertItemsEqual([1, 2, 3], self.objects.all())
        self.assertEqual(3, self.objects['three'])

    def test_sort(self):
        self.objects.add('five', Number(5))
        self.objects.add('three', Number(3))
        self.objects.add('four', Number(4))
        self.objects.add('two', Number(2))
        self.objects.add('one', Number(1))
        self.objects.sort(key='num')
        self.assertEqual([1, 2, 3, 4, 5], [obj.num for obj in self.objects.all()])

    def test_remove(self):
        self.objects.add('one', Number(1))
        self.objects.add('two', Number(2))
        self.objects.remove('one')
        self.assertItemsEqual([2], [obj.num for obj in self.objects.all()])
