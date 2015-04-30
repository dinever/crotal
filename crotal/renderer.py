# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
from inspect import ismethod

from crotal import utils
from crotal.template_engine import TemplateEngine


class Renderer(object):

    def __init__(self, config, data, templates, static_files):
        self.data = data
        self.config = config
        self.site_content = {}
        self.templates = templates
        self.static_files = static_files
        self.variables = data.copy()
        self.variables.update({
            'site': self.config,
            'sidebar': True,
            'max_page': 5,
        })
        self.template_engine = TemplateEngine(self.config, templates)

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
        for path, static_file in self.static_files.iteritems():
            source_path = os.path.join(self.config.base_dir, path)
            path = utils.generate_path(static_file.url,
                                       output_path=self.config.publish_dir,
                                       site_root=self.config.root_path
                                       )
            utils.copy_file(source_path, path)

    def render_template(self):
        for path, template in self.templates.iteritems():
            rel_path = os.path.relpath(template.path, self.config.templates_dir)
            if not rel_path.startswith('_'):
                content = self.template_engine.render(template.path, self.variables)
                output_path = os.path.join(self.config.root_path.replace('/', ''), rel_path)
                self.site_content[output_path] = content

    def render_post(self):
        layout_file = self._layout_file('post.html')
        for post in self.data['posts']:
            content = self.template_engine.render(layout_file, self._update_variables({'post': post}))
            path = utils.generate_path(post.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_page(self):
        layout_file = self._layout_file('page.html')
        for page in self.data['pages']:
            content = self.template_engine.render(layout_file, self._update_variables({'page': page}))
            path = utils.generate_path(page.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_category_pages(self):
        layout_file = self._layout_file('categories.html')
        for category in self.data['categories']:
            content = self.template_engine.render(
                layout_file,
                self._update_variables({'category': category, 'title': category.name})
            )
            path = utils.generate_path(category.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_tag_pages(self):
        layout_file = self._layout_file('tags.html')
        for tag in self.data['tags']:
            content = self.template_engine.render(
                layout_file,
                self._update_variables({'tag': tag, 'title': tag.name})
            )
            path = utils.generate_path(tag.url, output_path=self.config.publish_dir, site_root=self.config.root_path)
            self.site_content[path] = content

    def render_archive_pages(self):
        layout_file = self._layout_file('archives.html')
        for archive in self.data['archives']:
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

    def run(self):
        for name in dir(self):
            if name.startswith('render'):
                function = getattr(self, name)
                if ismethod(function):
                    function()
        return self.site_content
