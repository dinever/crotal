# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import sys
import yaml

from crotal import logger


class Config(object):

    def __init__(self, path, output=None):
        if path is None or (not self.check_config(path)):
            logger.error("Config file '_config.yml' can not be loaded in the current directory and its parents.")
            sys.exit()
        self.base_dir = os.path.join(path)
        self.working_dir = os.getcwd()
        self.config_path = os.path.join(self.base_dir, '_config.yml')

        self.posts_dir = os.path.join('source', 'posts')
        self.pages_dir = os.path.join('source', 'pages')
        self.static_dir = os.path.join('static')

        self.db_path = os.path.join(self.base_dir, 'db.json')
        if output:
            self.publish_dir = os.path.join(self.base_dir, output)
        else:
            self.publish_dir = os.path.join(self.base_dir, 'preview')
        self.deploy_dir = os.path.join(self.base_dir, 'deploy')

        self.read_from_file()

    def __getattr__(self, item):
        return self.__dict__.get(item, None)

    def read_from_file(self):
        config_file = open(self.config_path, 'r').read()
        for item, value in yaml.load(config_file).iteritems():
            setattr(self, item, value)
        self.theme_dir = os.path.join('themes', self.theme)
        self.templates_dir = os.path.join(self.theme_dir, 'public')
        self.static_dir = os.path.join(self.theme_dir, 'static')

    def check_config(self, path):
        if not os.path.exists(os.path.join(path, '_config.yml')):
            return False
        else:
            return True
