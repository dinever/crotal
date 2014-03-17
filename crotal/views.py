# -*- coding:utf-8 -*-
import os.path
import time
import json
import re

import yaml
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from crotal.models.posts import Post
from crotal.models.pages import Page
from crotal.models.categories import Category
from crotal.plugins.markdown.jinja_markdown import MarkdownExtension


class Views():

    def __init__(self, config, dir, full):
        self.config = config
        self.db = {}
        self.dir = dir
        self.posts_dir = os.path.normpath(
            os.path.join(
                self.dir,
                'source/posts'))
        self.pages_dir = os.path.normpath(
            os.path.join(
                self.dir,
                'source/pages'))
        self.template_dir = os.path.normpath(
            os.path.join(
                self.dir,
                '.private'))
        self.posts = []
        self.pages = []
        self.page_number = 0
        self.categories = {}
        self.templates_path = []
        self.templates = []  # html files start not with '_'
        self.other_files = []  # html files start with '_'
        os.path.walk(
            repr(
                self.template_dir)[
                1:-
                1],
            self.processDirectory,
            None)
        self.j2_env = Environment(
            loader=FileSystemLoader(
                self.template_dir),
            trim_blocks=True,
            extensions=[MarkdownExtension])
        self.post_template = self.j2_env.get_template('_layout/post.html')
        if full:
            self.db = {'posts': {}, 'pages': {}}
        else:
            try:
                self.db = json.loads(
                    open(
                        'db.json',
                        'r').read().encode('utf8'))
            except Exception as e:
                print 'Generating the full site...Please be patient :)'
                self.db = {'posts': {}, 'pages': {}}

    def processDirectory(self, args, dirname, filenames):
        for filename in filenames:
            file_path = os.path.join(dirname, filename)
            file_relative_path = os.path.relpath(file_path, self.template_dir)
            if not file_relative_path.startswith('_'):
                if filename.endswith('.html'):
                    self.templates_path.append(file_relative_path)
                elif filename.endswith('.xml'):
                    self.templates_path.append(file_relative_path)
                elif filename.endswith('.txt'):
                    self.templates_path.append(file_relative_path)
                elif not filename.startswith('_'):
                    self.other_files.append(file_relative_path)

    def get_templates(self):
        pass

    def get_full_template_content(self, layout_content, parameter):
        header = ''
        template_info = {}
        if layout_content.startswith("---"):
            get_header = re.compile(r'---[\s\S]*?---')
            header = get_header.findall(layout_content)[0]
            layout_content = layout_content.replace(header, '', 1)
            header = header.replace('---', '')
            template_info = yaml.load(header)
        parameter = dict(parameter.items() + template_info.items())
        rendered = self.j2_env.from_string(layout_content).render(**parameter)
        if header != '':
            parameter['content'] = rendered
            fname = os.path.normpath(
                os.path.join(
                    self.template_dir,
                    '_layout/',
                    parameter['layout']))
            if not parameter['layout'].endswith(".html"):
                fname += '.html'
            template_layout_content = open(fname, 'r').read().decode('utf8')
            rendered = self.get_full_template_content(
                template_layout_content,
                parameter)
        return rendered

    def save(self, posts, categories):
        '''
        Save rendered files except posts.
        '''
        def md(pth):
            try:
                os.makedirs(pth)
            except Exception:
                pass

        for item in self.other_files:
            md(os.path.normpath(os.path.join(self.dir, "_sites/", item)))

        for item in self.templates_path:
            input_name = os.path.normpath(
                os.path.join(
                    self.template_dir,
                    item))
            template_layout_content = open(
                input_name,
                'r').read().decode('utf8')

            parameter = dict(
                posts=posts,
                site=self.config,
                categories=categories,
                current_page=1,
                page_number=self.page_number,
                pages=self.pages)
            rendered = self.get_full_template_content(
                template_layout_content,
                parameter)

            output_name = os.path.normpath(
                os.path.join(
                    self.dir,
                    "_sites/",
                    item))
            md(os.path.dirname(output_name))
            open(output_name, 'w+').write(rendered.encode('utf8'))

        self.save_index_pages()

    def get_new_filenames(self, filenames, db_filenames, source_type):
        new_filenames = list(set(filenames) - set(db_filenames))
        old_filenames = list(
            set(db_filenames) - (set(db_filenames) - set(filenames)))
        for filename in old_filenames:
            if source_type == 'posts':
                last_mod_time = os.path.getmtime(
                    os.path.join(
                        self.posts_dir,
                        filename))
            else:
                last_mod_time = os.path.getmtime(
                    os.path.join(
                        self.pages_dir,
                        filename))
            last_mod_time_in_db = self.db[
                source_type][filename]['last_mod_time']
            if last_mod_time != last_mod_time_in_db:
                new_filenames.append(filename)
                old_filenames.remove(filename)
        return new_filenames, old_filenames

    def get_posts(self):
        '''
        Get posts from markdown files
        '''
        filenames = [
        ]  # filenames is a list of the markdown file's name from the posts' directory
        for filename in os.listdir(self.posts_dir):
            if not filename.startswith('.'):
                filenames.append(filename)

        # db_filenames is a list of the filenames read from db.json
        db_filenames = []
        for db_filename in self.db['posts']:
            db_filenames.append(db_filename.encode('utf8'))
        new_filenames, old_filenames = self.get_new_filenames(
            filenames, db_filenames, 'posts')
        categories_tmp = {}
        post_content = {}
        posts_dict = {}
        for filename in old_filenames:
            post_content = dict(self.db['posts'][filename]['content'])
            post_tmp = Post(self.config)
            post_tmp.get_from_db(post_content)
            self.posts.append(post_tmp)
            for category in post_tmp.categories:
                if category in self.categories:
                    self.categories[category].add_post(post_tmp)
                else:
                    self.categories[category] = Category(self.config, category)
                    self.categories[category].add_post(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(
                post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.posts_dir,
                    filename))
            posts_dict[filename] = {
                'last_mod_time': last_mod_time,
                'content': post_dict}
        for filename in new_filenames:
            post_tmp = Post(self.config)
            post_tmp.save(
                open(
                    os.path.join(
                        self.posts_dir,
                        filename),
                    'r').read().decode('utf8'))
            self.posts.append(post_tmp)
            for category in post_tmp.categories:
                if category in self.categories:
                    self.categories[category].add_post(post_tmp)
                else:
                    self.categories[category] = Category(self.config, category)
                    self.categories[category].add_post(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(
                post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.posts_dir,
                    filename))
            posts_dict[filename] = {
                'last_mod_time': last_mod_time,
                'content': post_dict}
        self.db['posts'] = posts_dict
        self.posts_sort()
        self.page_number = len(self.posts) / 5

    def save_posts(self, posts):
        '''
        Save posts .html files.
        '''
        input_file = os.path.normpath(
            os.path.join(
                self.template_dir,
                '_layout/',
                'post.html'))
        post_layout_content = open(input_file, 'r').read().decode('utf8')
        for post in posts:
            self.save_post_file(
                post,
                post_layout_content,
                os.path.join(
                    self.dir,
                    '_sites'))

    def get_pages(self):
        '''
        Get pages from pages directory
        '''
        categories_tmp = []
        pages_filenames = []
        pages_dict = {}
        for dirpath, dirnames, filenames in os.walk(self.pages_dir):
            for filename in filenames:
                if not filename.startswith('.'):
                    file_path = os.path.join(dirpath, filename)
                    rel_file = os.path.relpath(file_path, self.pages_dir)
                    pages_filenames.append(rel_file)
        # db_filenames is a list of the filenames read from db.json
        db_filenames = []

        if 'pages' in self.db:
            pass
        else:
            self.db['pages'] = {}
        for db_filename in self.db['pages']:
            db_filenames.append(db_filename.encode('utf8'))

        new_filenames, old_filenames = self.get_new_filenames(
            pages_filenames, db_filenames, 'pages')

        for filename in old_filenames:
            page_content = dict(self.db['pages'][filename]['content'])
            page_tmp = Page(self.config)
            page_tmp.get_from_db(page_content)
            self.pages.append(page_tmp)
            for category in page_tmp.categories:
                categories_tmp.append(category)
            page_dict = page_tmp.__dict__.copy()
            page_dict['pub_time'] = time.mktime(
                page_dict['pub_time'].timetuple())
            page_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.pages_dir,
                    filename))
            pages_dict[filename] = {
                'last_mod_time': last_mod_time,
                'content': page_dict}

        for filename in new_filenames:
            file_path = os.path.join(self.dir, filename)
            page_tmp = Page(self.config)
            page_tmp.save(
                open(
                    os.path.join(
                        self.pages_dir,
                        filename),
                    'r').read().decode('utf8'))
            self.pages.append(page_tmp)
            for category in page_tmp.categories:
                categories_tmp.append(category)
            page_dict = page_tmp.__dict__.copy()
            page_dict['pub_time'] = time.mktime(
                page_dict['pub_time'].timetuple())
            page_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.pages_dir,
                    filename))
            pages_dict[filename] = {
                'last_mod_time': last_mod_time,
                'content': page_dict}
        self.pages_sort()
        self.db['pages'] = pages_dict

    def save_db(self):
        db_to_save = json.dumps(self.db)
        open('db.json', 'w+').write(db_to_save.encode('utf8'))

    def get_prev_and_next(self, iterable):
        iterator = iter(iterable)
        prev = None
        item = iterator.next()  # throws StopIteration if empty.
        for next in iterator:
            yield (prev, item, next)
            prev = item
            item = next
        yield (prev, item, None)

    def pages_sort(self):
        for i in range(len(self.pages)):
            for j in range(len(self.pages)):
                if self.pages[i].order < self.pages[j].order:
                    self.pages[i], self.pages[j] = self.pages[j], self.pages[i]
        for prev, current, next in self.get_prev_and_next(self.pages):
            current.prev = prev
            current.next = next

    def posts_sort(self):
        for i in range(len(self.posts)):
            for j in range(len(self.posts)):
                if self.posts[i].pub_time > self.posts[j].pub_time:
                    self.posts[i], self.posts[j] = self.posts[j], self.posts[i]

    def save_posts(self, posts):
        '''
        Save posts .html files.
        '''
        input_file = os.path.normpath(
            os.path.join(
                self.template_dir,
                '_layout/',
                'post.html'))
        post_layout_content = open(input_file, 'r').read().decode('utf8')
        for post in posts:
            self.save_post_file(
                post,
                post_layout_content,
                os.path.join(
                    self.dir,
                    '_sites'))

    def save_pages(self, pages):
        '''
        Save pages .html file
        '''
        input_file = os.path.normpath(
            os.path.join(
                self.template_dir,
                '_layout/',
                'page.html'))
        page_layout_content = open(input_file, 'r').read().decode('utf8')
        for page in pages:
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
                    self.dir,
                    '_sites'))

    def save_post_file(self, post, post_layout_content, dir):
        parameter = dict(
            post=post,
            posts=self.posts,
            site=self.config,
            categories=self.categories,
            current_page=1,
            page_number=self.page_number,
            pages=self.pages)
        dname = os.path.join(dir, post.url.strip("/\\"))
        if not os.path.exists(dname):
            os.makedirs(dname)
        file_content = self.get_full_template_content(
            post_layout_content,
            parameter)
        open(os.path.join(dname, 'index.html'),
             'w+').write(file_content.encode('utf8'))

    def save_page_file(self, page, page_layout_content, dir):
        parameter = dict(
            page=page,
            posts=self.posts,
            site=self.config,
            categories=self.categories,
            current_page=1,
            page_number=self.page_number,
            pages=self.pages)
        dname = os.path.join(dir, page.url.strip("/\\"))
        if not os.path.exists(dname):
            os.makedirs(dname)
        file_content = self.get_full_template_content(
            page_layout_content,
            parameter)
        open(os.path.join(dname, 'index.html'),
             'w+').write(file_content.encode('utf8'))

    def save_index_pages(self):
        '''
        Generate pagnition like 'http://localhost:8000/blog/page/2/'
        '''
        for i in range(1, self.page_number):
            dname = os.path.normpath(
                os.path.join(self.dir, '_sites/blog/page/', str(i + 1)))

            if not os.path.exists(dname):
                os.makedirs(dname)
            index_template = open(
                os.path.join(
                    self.template_dir,
                    'index.html'),
                'r+').read().decode('utf8')
            parameter = dict(posts=self.posts[i * 5:(i + 1) * 5],
                             site=self.config,
                             current_page=i + 1,
                             page_number=self.page_number)
            file_content = self.get_full_template_content(
                index_template,
                parameter)
            open(os.path.join(dname, 'index.html'),
                 'w+').write(file_content.encode('utf8'))
