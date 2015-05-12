import os
import unittest


class BaseTest(unittest.TestCase):

    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.path.dirname(__file__), 'test_data')

