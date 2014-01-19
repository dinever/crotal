# -*- coding:utf-8 -*-
import os.path
import re
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from crotal.models.posts import Posts
from crotal.plugins.markdown.jinja_markdown import MarkdownExtension

private_dir = '.private/'

class Views():
    def __init__(self, config):
        self.config = config
        self.dir = ''
        self.posts = []
        self.page = 0
        self.categories = []
        self.templates_path = []
        self.templates = [] #html files start not with '_'
        self.other_files = [] #html files start with '_'
        os.path.walk(repr(private_dir)[1:-1], self.processDirectory, None)
        self.j2_env = Environment(loader=FileSystemLoader(private_dir), trim_blocks=True, extensions=[MarkdownExtension])
        self.post_template = self.j2_env.get_template('_layout/post.html')

    def get_directory(self, dir):
        self.dir = dir

    def processDirectory(self, args, dirname, filenames):
        for filename in filenames:
            file_path = dirname + '/' + filename
            if len(re.compile(r'\.html$').findall(file_path)) != 0 and len(re.compile(r'^_.*').findall(file_path.replace(private_dir, ''))) == 0:
                self.templates_path.append(file_path.replace(private_dir, ''))
            elif len(re.compile(r'\.xml$').findall(file_path)) != 0 and len(re.compile(r'^_.*').findall(file_path.replace(private_dir, ''))) == 0:
                self.templates_path.append(file_path.replace(private_dir, ''))
            elif len(re.compile(r'^_.*').findall(filename)) == 0:
                self.other_files.append(file_path.replace(private_dir, ''))

    def get_templates(self):
        pass

    def save(self, posts, categories):
        '''
        Save rendered files except posts.
        '''
        for item in self.other_files:
            try:
                os.mkdir(self.dir + '/' + '_sites/' + item)
            except Exception:
                pass
        self.page = len(self.posts)/5 + 1
        for item in self.templates_path:
            rendered = self.j2_env.get_template(item).render(posts = posts, config = self.config, categories = categories, current_page = 1, page = self.page)
            open(self.dir + '/_sites/' + item, 'w+').write(rendered.encode('utf8'))
        self.save_index_pages()

    def get_posts(self):
        '''
        Get posts from markdown files
        '''
        posts_titles = []
        categories_tmp = []
        posts_dir = self.dir + '/_posts/'
        for item in os.listdir(posts_dir):
            if not item.startswith('.'):
                post_tmp = Posts(self.config)
                post_tmp.save(open(posts_dir  + item , 'r').read().decode('utf8'))
                self.posts.append(post_tmp)
                for category in post_tmp.categories:
                    categories_tmp.append(category)
        self.categories = sorted({}.fromkeys(categories_tmp).keys()) #Sort the categories, remove the repeat items.
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
            self.save_post_file(post, self.dir + '/_sites/')

    def save_post_file(self, post, dir):
        if not os.path.exists(dir + post.url):
            os.makedirs(dir + post.url)
        rendered = self.post_template.render(post = post ,posts=self.posts, config = self.config)
        open(dir + post.url + '/index.html', 'w+').write(rendered.encode('utf8'))

    def save_index_pages(self):
        '''
        Generate pagnition like 'http://localhost:8000/blog/page/2/'
        '''
        index_template = self.j2_env.get_template('index.html')
        for i in range(1, self.page):
            if not os.path.exists(self.dir + '/_sites/blog/page/' + str(i+1)):
                os.makedirs(self.dir + '/_sites/blog/page/' + str(i+1))
            rendered = index_template.render(posts = self.posts[i*5:(i+1)*5], config = self.config, current_page = i+1, page = self.page)
            open(self.dir + '/_sites/blog/page/' + str(i+1) + '/index.html', 'w+').write(rendered.encode('utf8'))
