# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re
import time
from datetime import datetime

from markdown import markdown

from crotal import logger
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
