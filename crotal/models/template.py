# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from crotal.models import Model
from crotal.models.fields import *


class Template(Model):
    PATH = ['themes/{theme}/public/']

    path = CharField()
    layout = CharField()
    content = TextField()

    @classmethod
    def parse_content(cls, file_path, content, config):
        attributes = {}
        attributes['content'] = content
        attributes['path'] = file_path
        cls.parse_attributes(file_path, config, attributes)
        return cls(**attributes)
