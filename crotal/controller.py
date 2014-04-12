# -*- coding:utf-8 -*-
import os.path
import time
import json

from crotal.copy_dir import copy_dir
from crotal.models.posts import Post
from crotal.models.pages import Page
from crotal.plugins.markdown.jinja_markdown import MarkdownExtension
from crotal.reporter import Reporter
from crotal.collector.post_collector import PostCollector
from crotal.collector.page_collector import PageCollector
from crotal.collector.template_collector import TemplateCollector
from crotal.template_engine import Engine
from crotal.db import Database

reporter = Reporter()

class Controller():

    def __init__(self, config, dir, full=False):
        self.config = config
        self.database = Database(full)
        self.current_dir = dir
        self.posts_dir = os.path.normpath(
            os.path.join(
                self.current_dir, 'source', 'posts'))
        self.pages_dir = os.path.normpath(
            os.path.join(
                self.current_dir, 'source', 'pages'))
        self.template_dir = os.path.normpath(
                os.path.join(
                    self.current_dir,
                    'themes',
                    config.theme,
                    'public'
                    )
                )
        self.engine = Engine(self.template_dir)

    def copy_static_files(self):
        copy_dir(os.path.join('themes', self.config.theme , 'static'), '_sites')
        copy_dir('static', '_sites')

    def get(self):
        self.get_posts()
        self.get_pages()
        self.get_templates()
        self.post_collector.join()
        self.page_collector.join()
        self.template_collector.join()
        self.default_parameter = dict(
            posts=self.post_collector.posts,
            pages=self.page_collector.pages,
            categories=sorted(self.post_collector.categories.values(), key=lambda x:-x.posts.__len__()),
            tags=sorted(self.post_collector.tags.values(), key=lambda x:-x.posts.__len__()),
            current_page=1,
            site=self.config,
            page_number=self.post_collector.page_number
            )

    def get_posts(self):
        self.post_collector = PostCollector(self.current_dir, self.database, self.config)
        self.post_collector.start()

    def get_pages(self):
        self.page_collector = PageCollector(self.current_dir, self.database, self.config)
        self.page_collector.start()

    def get_templates(self):
        self.template_collector = TemplateCollector(self.current_dir, self.database, self.config)
        self.template_collector.start()

    def post_or_page_modified(self):
        if self.post_collector.new_posts == [] and \
                self.page_collector.new_pages == [] and \
                self.post_collector.removed_posts == [] and \
                self.page_collector.removed_pages == []:
            return False
        else:
            return True

    def template_modified(self):
        if self.template_collector.new_templates == {}:
            return False
        else:
            return True

    def save_template_file(self, template_path, template_content):
        rendered = self.engine.render(
            template_content,
            self.default_parameter)
        relativ_path = os.path.relpath(template_path, self.template_dir)
        output_path = os.path.join(self.current_dir, '_sites', relativ_path)
        self.make_dirs(os.path.join(self.current_dir, '_sites', output_path))
        open(output_path, 'w+').write(rendered.encode('utf8'))


    def save(self):
        if self.post_or_page_modified():
            for template_path, template_content in self.template_collector.templates.iteritems():
                self.save_template_file(template_path, template_content)
        else:
            for template_path, template_content in self.template_collector.new_templates.iteritems():
                self.save_template_file(template_path, template_content)
        self.save_index_pages()

    def make_dirs(self, filepath):
        dir_path = os.path.dirname(filepath)
        try:
            os.makedirs(dir_path)
        except Exception:
            pass

    def remove_items(self):
        self.post_collector.remove_posts()
        self.page_collector.remove_pages()

    def save_post_file(self, post, post_layout_content, site_dir):
        parameter = dict(self.default_parameter.items()
                + {'post': post}.items()
                )
        dname = os.path.join(site_dir, post.url.strip("/\\"))
        if not os.path.exists(dname):
            os.makedirs(dname)
        file_content = self.engine.render(
            post_layout_content,
            parameter)
        open(os.path.join(dname, 'index.html'),
             'w+').write(file_content.encode('utf8'))

    def save_posts(self):
        input_file = os.path.normpath(os.path.join(self.template_dir,
                '_layout/', 'post.html'))
        post_layout_content = open(input_file, 'r').read().decode('utf8')
        if self.template_modified():
            for post in self.post_collector.posts:
                self.save_post_file(post, post_layout_content,
                    os.path.join(self.current_dir, '_sites'))
        else:
            for post in self.post_collector.new_posts:
                self.save_post_file(post, post_layout_content,
                    os.path.join(self.current_dir, '_sites'))

    def save_page_file(self, page, page_layout_content, site_dir):
        parameter = dict(self.default_parameter.items()
                + {'page': page, 'title': page.title}.items()
                )
        dname = os.path.join(site_dir, page.url.strip("/\\"))
        if not os.path.exists(dname):
            os.makedirs(dname)
        file_content = self.engine.render(
            page_layout_content,
            parameter)
        open(os.path.join(dname, 'index.html'),
             'w+').write(file_content.encode('utf8'))

    def parse_page_file(self, page):
        if page.layout != "page":
            fname = os.path.normpath(
                os.path.join(
                    self.template_dir,
                    '_layout/',
                    page.layout))
            if not page.layout.endswith(".html"):
                fname += ".html"
            page_layout_content = open(fname, 'r').read().decode('utf8')
        self.save_page_file(
            page,
            page_layout_content,
            os.path.join(
                self.current_dir,
                '_sites'))

    def save_pages(self):
        '''
        Save pages .html file
        '''
        input_file = os.path.normpath(
            os.path.join(
                self.template_dir,
                '_layout/',
                'page.html'))
        page_layout_content = open(input_file, 'r').read().decode('utf8')
        if self.template_modified():
            for page in self.page_collector.pages:
                self.parse_page_file(page)
        else:
            for page in self.page_collector.new_pages:
                self.parse_page_file(page)

    def save_index_pages(self):
        '''
        Generate pagnition like 'http://localhost:8000/blog/page/2/'
        '''
        for i in range(1, self.post_collector.page_number+1):
            dname = os.path.normpath(
                os.path.join(self.current_dir, '_sites/blog/page/', str(i + 1)))

            if not os.path.exists(dname):
                os.makedirs(dname)
            index_template = open(
                os.path.join(
                    self.template_dir,
                    'index.html'),
                'r+').read().decode('utf8')
            parameter = dict(self.default_parameter.items() + \
                            dict(posts=self.post_collector.posts[i * 5:(i + 1) * 5],
                                 site=self.config,
                                 current_page=i + 1,
                                 page_number=self.post_collector.page_number).items())
            file_content = self.engine.render(index_template, parameter)
            open(os.path.join(dname, 'index.html'),
                 'w+').write(file_content.encode('utf8'))

    def save_db(self):
        self.database.save()
