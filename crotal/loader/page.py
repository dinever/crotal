# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function

import os

from crotal.loader import BaseLoader
from crotal.models.page import Page
from crotal.models.others import Category


class PageLoader(BaseLoader):
    name = 'pages'
    Model = Page
    path = [os.path.join('source', 'pages')]

    def sort_data(self, data):
        data['pages'] = data['pages'].values()
        return data
