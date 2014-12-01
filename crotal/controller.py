# -*- coding:utf-8 -*-
import os.path

from crotal.collector.post_collector import PostCollector
from crotal.collector.page_collector import PageCollector
from crotal.collector.template_collector import TemplateCollector
from crotal.collector.static_collector import StaticCollector
from crotal.template_engine import Engine
from crotal.db import Database
from crotal import settings


class Controller(object):

    def __init__(self, full=False):
        self.database = Database(full)
        self.engine = Engine()
        self.static_collector = StaticCollector(self.database)
        self.post_collector = PostCollector(self.database)
        self.page_collector = PageCollector(self.database)
        self.template_collector = TemplateCollector(self.database)


    def load(self, is_preview=True):
        self.static_collector.run()
        self.post_collector.run()
        self.page_collector.run()
        self.template_collector.run()

        self.default_parameter = dict(
            posts=self.post_collector.posts,
            pages=self.page_collector.pages,
            categories=sorted(self.post_collector.categories.values(), key=lambda x: -x.posts.__len__()),
            tags=sorted(self.post_collector.tags.values(), key=lambda x: -x.posts.__len__()),
            recent_posts=self.post_collector.posts,
            current_page=1,
            site=settings,
            page_number=self.post_collector.page_number
        )

        if is_preview:
            self.default_parameter['ROOT_PATH'] = ""
        else:
            if settings.url.endswith('/'):
                self.default_parameter['ROOT_PATH'] = "http://" + settings.root_url[:-1]
            else:
                self.default_parameter['ROOT_PATH'] = "http://" + settings.root_url

    @property
    def post_or_page_modified(self):
        if self.post_collector.new_posts == [] and \
                self.page_collector.new_pages == [] and \
                self.post_collector.removed_posts == [] and \
                self.page_collector.removed_pages == []:
            return False
        else:
            return True

    @property
    def post_or_page_title_modified(self):
        for post in self.post_collector.new_posts:
            try:
                post_title = self.database.get_item_content('posts', post.filename)['title']
            except:
                return True  # New posts added.
            if post.title != post_title:
                return True  # Post title modified
        return False

    @property
    def template_modified(self):
        if not self.template_collector.new_templates:
            return False
        else:
            return True

    def save_template_file(self, template_path, template_content):
        rendered = self.engine.render(
            template_content,
            self.default_parameter)
        relative_path = os.path.relpath(template_path, settings.TEMPLATES_DIR)
        output_path = os.path.join(settings.PUBLISH_DIR, relative_path)
        self.make_dirs(os.path.join(settings.PUBLISH_DIR, output_path))
        open(output_path, 'w+').write(rendered.encode('utf8'))

    def save(self):
        if self.post_or_page_modified:
            for template_path, template_content in self.template_collector.templates.iteritems():
                self.save_template_file(template_path, template_content)
            self.save_index_pages()
        else:
            for template_path, template_content in self.template_collector.new_templates.iteritems():
                self.save_template_file(template_path, template_content)

    @staticmethod
    def make_dirs(file_path):
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def save_post_file(self, post, post_layout_content):
        parameter = dict(self.default_parameter.items() +
                         {'post': post}.items()
                         )
        dir_name = os.path.join(settings.PUBLISH_DIR, post.url.strip("/\\"))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_content = self.engine.render(
            post_layout_content,
            parameter)
        open(os.path.join(dir_name, 'index.html'),
             'w+').write(file_content.encode('utf8'))

    def save_posts(self):
        input_file = os.path.normpath(os.path.join(settings.TEMPLATES_DIR,
                                      '_layout/', 'post.html'))
        post_layout_content = open(input_file, 'r').read().decode('utf8')
        if self.template_modified or self.post_or_page_title_modified:
            for post in self.post_collector.posts:
                self.save_post_file(post, post_layout_content)
        else:
            for post in self.post_collector.new_posts:
                self.save_post_file(post, post_layout_content)

    def save_page_file(self, page, page_layout_content):
        parameter = dict(self.default_parameter.items()
                         + {'page': page, 'title': page.title}.items()
                         )
        dname = os.path.join(settings.PUBLISH_DIR, page.url.strip("/\\"))
        if not os.path.exists(dname):
            os.makedirs(dname)
        file_content = self.engine.render(
            page_layout_content,
            parameter)
        open(os.path.join(dname, 'index.html'),
             'w+').write(file_content.encode('utf8'))

    def parse_page_file(self, page):
        fname = os.path.normpath(
            os.path.join(
                settings.TEMPLATES_DIR,
                '_layout/', page.layout))
        if not page.layout.endswith(".html"):
            fname += ".html"
        page_layout_content = open(fname, 'r').read().decode('utf8')
        self.save_page_file(
            page, page_layout_content)

    def save_pages(self):
        """
        Save pages .html file
        """
        if self.template_modified or self.post_or_page_modified:
            for page in self.page_collector.pages:
                self.parse_page_file(page)
        else:
            for page in self.page_collector.new_pages:
                self.parse_page_file(page)

    def save_index_pages(self):
        """
        Generate pagnition like 'http://localhost:8000/blog/page/2/'
        """
        for i in range(1, self.post_collector.page_number+1):
            dir_name = os.path.join(settings.PUBLISH_DIR, 'blog/page/', str(i + 1))

            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            index_template = open(
                os.path.join(
                    settings.TEMPLATES_DIR,
                    'index.html'),
                'r+').read().decode('utf8')
            parameter = dict(self.default_parameter.items() +
                             dict(site=settings,
                                  posts=self.post_collector.posts[i*5:],
                                  current_page=i + 1,
                                  page_number=self.post_collector.page_number).items())
            file_content = self.engine.render(index_template, parameter)
            open(os.path.join(dir_name, 'index.html'),
                 'w+').write(file_content.encode('utf8'))

    def save_db(self):
        self.database.save()

    def save_categories(self):
        for c in self.post_collector.categories.values():
            parameter = self.get_parameter(category=c)
            self.save_category_file(c, parameter)

    def save_category_file(self, c, parameter):
        pass

    def get_parameter(self, **parameter):
        return dict(self.default_parameter.items() + parameter.items())

    def save_tags(self):
        pass
