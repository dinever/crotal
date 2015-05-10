# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from crotal import db
from crotal import utils
from crotal.config import Config
from crotal.renderer import Renderer
from crotal.loader import PostLoader, PageLoader, TemplateLoader, StaticLoader


class Site(object):

    LoaderClass = [PostLoader, PageLoader, TemplateLoader, StaticLoader]

    def __init__(self, path=os.getcwd(), full=False, output=None):
        self.config = Config(path, output)
        if full:
            self.database = db.Database.from_file(self.config.db_path)
        else:
            self.database = db.Database(dict(), self.config.db_path)
        self.data = {}
        self.site_content = {}
        self.loaders = []
        for Loader in self.LoaderClass:
            loader = Loader(self.database, self.config)
            loader.load(self.update_data)
            self.loaders.append(loader)

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
        loader = self.detect_file_type(file_path)
        loader.single_file_on_change(file_path, event_type, self.update_data)
        self.generate()

    def detect_file_type(self, file_path):
        for loader in self.loaders:
            for path in loader.path:
                if file_path.startswith(path):
                    return loader

    def render(self):
        renderer = Renderer(self.config, **self.data)
        self.site_content = renderer.run()

    def write(self):
        for path in self.site_content:
            utils.output_file(os.path.join(self.config.publish_dir, path), self.site_content[path])

    def save(self):
        self.database.save()

