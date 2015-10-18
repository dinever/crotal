# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re
import time
from datetime import datetime

from markdown import markdown

from crotal import logger
from crotal.models import Model


class Template(Model):

    def __init__(self, path, config, layout=None, content="", **extras):
        self.path = path
        self.layout = layout
        self.content = content
        self.extras = extras
        for name, value in extras.iteritems():
            setattr(self, name, value)

    @classmethod
    def from_text(cls, path, config, text):
        return cls(path, config, content=text)

