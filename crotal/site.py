# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
try:
   from hashlib import md5
except ImportError:
   from md5 import md5
import imp

from crotal import db
from crotal import utils
from crotal import logger
from crotal.config import Config
from crotal.models import Page, Post, Template, Static


class Site(object):

    def __init__(self, path=os.getcwd(), full=False, output='preview'):
        self.config = Config(path, output)
        if full:
            self.database = db.Database(self.config.db_path)
        else:
            self.database = db.Database.from_file(self.config.db_path)
        self.data = {}
        self.site_content = {}
        self.static_files = []
        self.models = []
        self.load_modules()
        for model in [Page, Post, Template, Static]:
            model.load(self.database, self.config, self.update_data)
            self.models.append(model)

    def load_modules(self):
        renderer_path = os.path.join(self.config.base_dir, 'modules', 'renderer.py')
        if os.path.exists(renderer_path):
            try:
                self.Renderer = imp.load_source('renderer', renderer_path).Renderer
            except IOError:
                logger.error("Can not import {0}".format(renderer_path))
                from crotal import renderer
                self.Renderer = renderer.Renderer
        else:
            from crotal import renderer
            self.Renderer = renderer.Renderer

    def update_data(self, data):
        self.data.update(data)

    def generate(self):
        self.render()
        self.write()
        self.save()

    def parse_single_file(self, file_path, event_type):
        """
        This method is used when single file change was detected during the server
        running.
        """
        file_path = os.path.relpath(file_path, self.config.base_dir)
        model = self.detect_file_type(file_path)
        model.single_file_on_change(file_path, event_type, self.config)
        self.generate()

    def detect_file_type(self, file_path):
        for model in self.models:
            for path in model.PATH:
                if file_path.startswith(path):
                    return model

    def render(self):
        renderer = self.Renderer(self.config)
        self.site_content, self.static_files = renderer.run()

    def write(self):
        for root, dirs, files in os.walk(self.config.publish_dir):
            root_dir = os.path.relpath(root, self.config.publish_dir)
            if root_dir.startswith('.') and root_dir != '.':
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path in self.site_content and \
                    not file_path in self.static_files:
                    os.unlink(file_path)
            if not os.listdir(root):
                os.rmdir(root)

        digest_table = self.database.get_table('digest')
        for path in self.site_content:
            digest = md5(self.site_content[path]).hexdigest()
            output_path = os.path.join(self.config.publish_dir, path)
            utils.output_file(output_path, self.site_content[path])
            digest_table[path] = digest

    def save(self):
        self.database.save()

