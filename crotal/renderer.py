# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
from inspect import ismethod

from crotal import utils
from crotal.template_engine import TemplateEngine
from crotal.models import *


class Renderer(object):

    def __init__(self, config):
        self.config = config
        self.site_content = {}
        self.templates = Template.objects.all()
        self.static_files = []
        self.variables = {
            'posts': Post.objects.all(),
            'pages': Page.objects.all(),
            'archives': Archive.objects.all(),
            'tags': Tag.objects.all(),
            'categories': Category.objects.all(),
        }
        self.variables.update({
            'site': self.config,
            'sidebar': True,
            'max_page': 5,
        })
        self.template_engine = TemplateEngine(self.config, self.templates)

    @utils.memoize
    def _layout_file(self, filename):
        if not filename.endswith('.html'):
            filename += '.html'
        return os.path.normpath(os.path.join(self.config.templates_dir,
                                             '_layout/', filename))

    def _update_variables(self, new_variables):
        v = self.variables.copy()
        v.update(new_variables)
        return v

    def render_static(self):
        for static_file in Static.objects.all():
            source_path = os.path.join(self.config.base_dir, static_file.path)
            path = utils.generate_path(static_file.url,
                                       output_path=self.config.publish_dir,
                                       site_root=self.config.root_path
                                       )
            self.static_files.append(path)
            utils.copy_file(source_path, path)

    def render_template(self):
        for template in self.templates:
            rel_path = os.path.relpath(template.path, self.config.templates_dir)
            if not rel_path.startswith('_'):
                content = self.template_engine.render(template.path, self.variables)
                path = utils.generate_path(rel_path, output_path=self.config.publish_dir, site_root=self.config.root_path)
                self.site_content[path] = content

    def render_post(self):
        layout_file = self._layout_file('post.html')
        for post in Post.objects.all():
            content = self.template_engine.render(layout_file, self._update_variables({'post': post}))
            path = utils.generate_path(post.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_page(self):
        for page in Page.objects.all():
            layout_file = self._layout_file(page.layout)
            content = self.template_engine.render(layout_file, self._update_variables({'page': page}))
            path = utils.generate_path(page.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_category_pages(self):
        layout_file = self._layout_file('categories.html')
        for category in Category.objects.all():
            content = self.template_engine.render(
                layout_file,
                self._update_variables({'category': category, 'title': category.name})
            )
            path = utils.generate_path(category.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_tag_pages(self):
        layout_file = self._layout_file('tags.html')
        for tag in Tag.objects.all():
            content = self.template_engine.render(
                layout_file,
                self._update_variables({'tag': tag, 'title': tag.name})
            )
            path = utils.generate_path(tag.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_archive_pages(self):
        layout_file = self._layout_file('archives.html')
        for archive in Archive.objects.all():
            content = self.template_engine.render(
                layout_file,
                self._update_variables({'archive': archive})
            )
            path = os.path.join('archives',
                                '{:04d}'.format(archive.datetime.year),
                                '{:02d}'.format(archive.datetime.month),
                                'index.html'
                                )
            path = utils.generate_path(archive.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_index_pages(self):
        """
        render pages like '/page/2/'
        """
        layout_file = self._layout_file('index.html')
        page_number = len(self.variables['posts']) / self.config.paginate
        for i in range(page_number + 1):
            v = self._update_variables({
                'index_posts': self.variables['posts'][i * self.config.paginate: i * self.config.paginate + self.config.paginate],
                'current_page': i + 1,
                'max_page': page_number + 1
            })
            content = self.template_engine.render(layout_file, v)
            if not i:
                path = utils.generate_path('index.html', output_path=self.config.publish_dir, site_root=self.config.root_path)
            else:
                path = utils.generate_path("page/{0}/".format(str(i+1)), output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    @utils.stop_watch
    def run(self):
        for name in dir(self):
            if name.startswith('render'):
                function = getattr(self, name)
                if ismethod(function):
                    function()
        return self.site_content, self.static_files
