# -*- coding:utf-8 -*-
import os.path
import re
from unipath import Path
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from turtpress.models.posts import Posts
from turtpress.plugins.markdown.jinja_markdown import MarkdownExtension
import settings

dir = Path(__file__).ancestor(2).absolute()

class Views():
    def __init__(self):
        """docstring for __init__"""
        self.posts = []
        self.categories = []
        self.templates_path = []
        self.templates = [] #html files start not with '_'
        self.other_files = [] #html files start with '_'
        os.path.walk(r'public', self.processDirectory, None)
        self.j2_env = Environment(loader=FileSystemLoader(dir + '/public/'), trim_blocks=True, extensions=[MarkdownExtension])

    def processDirectory(self, args, dirname, filenames):
        for filename in filenames:
            file_path = dirname + '/' + filename
            if len(re.compile(r'\.html$').findall(file_path)) != 0 and len(re.compile(r'^_.*').findall(file_path.replace('public/', ''))) == 0:
                self.templates_path.append(file_path.replace('public/', ''))
            elif len(re.compile(r'\.xml$').findall(file_path)) != 0 and len(re.compile(r'^_.*').findall(file_path.replace('public/', ''))) == 0:
                self.templates_path.append(file_path.replace('public/', ''))
            elif len(re.compile(r'^_.*').findall(filename)) == 0:
                self.other_files.append(file_path.replace('public/', ''))

    def get_templates(self):
        pass

    def save(self, posts, categories):
        '''
        Save rendered files except posts.
        '''
        for item in self.other_files:
            try:
                os.mkdir(dir + '/' + '_sites/' + item)
            except Exception:
                pass
        for item in self.templates_path:
            rendered = self.j2_env.get_template(item).render(posts=posts, settings = settings, categories = categories)
            open(dir + '/_sites/' + item, 'w+').write(rendered.encode('utf8'))

    def get_posts(self):
        '''
        Get posts from markdown files
        '''
        posts_titles = []
        for item in os.listdir(dir.child('_posts')):
            if not item.startswith('.'):
                posts_titles.append(item)
        templates = os.listdir(dir)
        categories_tmp = []
        for post_title in posts_titles:
            post_tmp = Posts()
            post_tmp.save(open(dir + '/_posts/' + post_title, 'r').read().decode('utf8'))
            self.posts.append(post_tmp)
            for category in post_tmp.categories:
                categories_tmp.append(category)

        categories = sorted({}.fromkeys(categories_tmp).keys())
        self.posts_sort()

    def posts_sort(self):
        for i in range(len(self.posts)):
            for j in range(len(self.posts)):
                if  self.posts[i].pub_time > self.posts[j].pub_time:
                    self.posts[i], self.posts[j] = self.posts[j], self.posts[i]


    def save_posts(self, posts):
        '''
        Save posts .html files.
        '''
        for post in posts:
            if not os.path.exists(dir + '/_sites' + post.url):
                os.makedirs(dir + '/_sites' + post.url)
            rendered = self.j2_env.get_template('_layout/post.html').render(post = post ,posts=posts, settings = settings)
            open(dir + '/_sites' + post.url + '/index.html', 'w+').write(rendered.encode('utf8'))
