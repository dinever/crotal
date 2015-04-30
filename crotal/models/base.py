# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re
import yaml
import cPickle

from crotal import logger

ENCODING = 'base64'


class Model(object):

    @classmethod
    def from_file(cls, path, config):
        absolute_path = os.path.join(config.base_dir, path)
        text = file(absolute_path, 'r').read().decode('utf8')
        return cls.from_text(path, config, text)

    @classmethod
    def from_text(cls, path, config, text):
        header = re.compile(r'---[\s\S]*?---').findall(text)
        if header:
            try:
                attributes = yaml.load(header[0].replace('---', ''))
            except yaml.YAMLError, e:
                logger.error("Wrong format inside the header area: {0}".format(path))
                return None
            attributes['content'] = text.replace(header[0], '', 1)
            return cls(path, config, **attributes)
        else:
            logger.error("Can not find header area: {0}".format(path))
            return None

    @classmethod
    def from_db(cls, path, config, row):
        serial = row['content'].decode('base64')
        return cPickle.loads(str(serial))

    def to_db(self, absolute_path):
        return {
            'content': self.serialize().encode('base64'),
            'last_mod_time': os.path.getmtime(absolute_path),
        }

    def serialize(self):
        return cPickle.dumps(self)

    def __repr__(self):
        return '<{0}:{1}>'.format(self.__class__.__name__, self.path).encode('utf8')
