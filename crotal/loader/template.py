# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function
import os

from crotal.loader import BaseLoader
from crotal.models.template import Template


class TemplateLoader(BaseLoader):
    _type = 'templates'
    _name = 'theme_templates'
    _Model = Template

    @property
    def path(self):
        return [os.path.join(self.config.templates_dir)]

    def sort_data(self, data):
        data = data[self._name]
        return data

