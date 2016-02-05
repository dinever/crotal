#!/usr/bin/env python
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
        """
        Site is an abstraction of a Crotal site.

        Example usage:

        .. testcode::

            from crotal.site import Site

            site = Site(path='path_to_the_crotal_site', full=False, output='publish')
            site.generate()

        :param path: The root path of the site.
        :param full: Set as `true` to do a full build, `false` to do an
            incremental build.
        :param output: Indicating the path of the output folder.
        :return: None
        """
        self.config = Config(path, output)
        if full:
            self.database = db.Database(self.config.db_path)
        else:
            self.database = db.Database.from_file(self.config.db_path)
        # self.site_content is a dictionary which stores the content of
        # generated files, with file path as key and file content as value.
        self.site_content = {}
        # self.static_files is a list containing path of static files.
        self.static_files = []
        self.models = [Page, Post, Template, Static]
        self.load_modules()
        for model in self.models:
            model.load(self.database, self.config)
            # self.models.append(model)

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

    def generate(self):
        """
        Generate the site, first render the templates, then write the rendered
        files in the output path, then save the database json file `db.json`.

        :return: None
        """
        self.render()
        self.write()
        self.save()

    def parse_single_file(self, file_path, event_type):
        """
        This method is used when single file change was detected during the server
        running.

        When a single file is modified, created or deleted, the crotal server calls
        this function and pass the `file_path` and `event_type` into it. Then the
        model(e.g. Post or Page or Template) of the file will be found based on
        `file_path` and model will be called to react to the file change, and the
        output will be rewrite.

        :param file_path: The path of the modified file.
        :param event_type: Type of the event, can be `modified`, `created` or
            `deleted`.
        :return:
        """

        print(event_type)

        file_path = os.path.relpath(file_path, self.config.base_dir)
        model = self.detect_file_type(file_path)
        model.single_file_on_change(file_path, event_type, self.config)
        self.generate()

    def detect_file_type(self, file_path):
        """
        Decide which model the file belongs to.

        :param file_path: Path of the file.
        :return: `model` that the file belongs to.
        """
        for model in self.models:
            for path in model.PATH:
                if file_path.startswith(path):
                    return model

    def render(self):
        """
        Render the content of the site based on templates.
        :return: None
        """
        renderer = self.Renderer(self.config)
        self.site_content, self.static_files = renderer.run()

    def write(self):
        """
        Write the site content based on `self.site_content`.

        :return: None
        """
        for root, dirs, files in os.walk(self.config.publish_dir):
            root_dir = os.path.relpath(root, self.config.publish_dir)
            if root_dir.startswith('.') and root_dir != '.':
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in self.site_content and \
                        file_path not in self.static_files:
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
        """
        Save the database content into `db.json`.
        :return: None
        """
        self.database.save()

