# -*- coding:utf-8 -*-
import os.path, time, json

from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from crotal.models.posts import Post
from crotal.models.pages import Page
from crotal.models.categories import Category
from crotal.plugins.markdown.jinja_markdown import MarkdownExtension

private_dir = '.private/'

class Views():
    def __init__(self, config, dir):
        self.config = config
        self.dir = dir
        self.posts_dir = self.dir + '/source/posts/'
        self.pages_dir = self.dir + '/source/pages/'
        self.posts = []
        self.pages = []
        self.page_number = 0
        self.categories = {}
        self.templates_path = []
        self.templates = [] #html files start not with '_'
        self.other_files = [] #html files start with '_'
        os.path.walk(repr(private_dir)[1:-1], self.processDirectory, None)
        self.j2_env = Environment(loader=FileSystemLoader(private_dir), trim_blocks=True, extensions=[MarkdownExtension])
        self.post_template = self.j2_env.get_template('_layout/post.html')

    def processDirectory(self, args, dirname, filenames):
        for filename in filenames:
            file_path = dirname + '/' + filename
            file_relative_path = file_path.replace(private_dir, '')
            if not file_path.replace(private_dir, '').startswith('_'):
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

    def save(self, posts, categories):
        '''
        Save rendered files except posts.
        '''
        for item in self.other_files:
            try:
                os.mkdir(self.dir + '/' + '_sites/' + item)
            except Exception:
                pass
        for item in self.templates_path:
            rendered = self.j2_env.get_template(item).render(posts = posts, site = self.config, categories = categories, current_page = 1, page_number = self.page_number, pages = self.pages)
            open(self.dir + '/_sites/' + item, 'w+').write(rendered.encode('utf8'))
        self.save_index_pages()

    def get_posts(self):
        '''
        Get posts from markdown files
        '''
        filenames = [] # filenames is a list of the markdown file's name from the posts' directory
        for filename in os.listdir(self.posts_dir):
            if not filename.startswith('.'):
                filenames.append(filename)
        try:
            db = json.loads(open('db.json','r').read().encode('utf8'))
        except Exception, e:
            print 'Generating the site for the first time...Please be patient :)'
            db = {'posts':{}}
        db_filenames = [] # db_filenames is a list of the filenames read from db.json
        for db_filename in db['posts']:
            db_filenames.append(db_filename.encode('utf8'))
        new_filenames = list(set(filenames) - set(db_filenames))
        old_filenames = list(set(db_filenames) - (set(db_filenames) - set(filenames)))
        for filename in old_filenames:
            last_mod_time = os.path.getmtime(self.posts_dir + filename)
            last_mod_time_in_db = db['posts'][filename]['last_mod_time']
            if last_mod_time != last_mod_time_in_db:
                new_filenames.append(filename)
                old_filenames.remove(filename)
        categories_tmp = {}
        post_content = {}
        posts_dict = {}
        for filename in old_filenames:
            post_content = dict(db['posts'][filename]['content'])
            post_tmp = Post(self.config)
            post_tmp.get_from_db(post_content)
            self.posts.append(post_tmp)
            for category in post_tmp.categories:
                if self.categories.has_key(category):
                    self.categories[category].add_post(post_tmp)
                else:
                    self.categories[category] = Category(self.config, category)
                    self.categories[category].add_post(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(self.posts_dir + filename)
            posts_dict[filename] = { 'last_mod_time': last_mod_time, 'content': post_dict }
        for filename in new_filenames:
            post_tmp = Post(self.config)
            post_tmp.save(open(self.posts_dir  + filename, 'r').read().decode('utf8'))
            self.posts.append(post_tmp)
            for category in post_tmp.categories:
                if self.categories.has_key(category):
                    self.categories[category].add_post(post_tmp)
                else:
                    self.categories[category] = Category(self.config, category)
                    self.categories[category].add_post(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(self.posts_dir + filename)
            posts_dict[filename] = { 'last_mod_time': last_mod_time, 'content': post_dict }
        db['posts'] = posts_dict
        db = json.dumps(db)
        open('db.json', 'w+').write(db.encode('utf8'))
        self.posts_sort()
        self.page_number = len(self.posts)/5 + 1

    def get_pages(self):
        '''
        Get pages from pages directory
        '''
        categories_tmp = []
        for dirpath, dirnames, filenames in os.walk(self.pages_dir):
            for filename in [f for f in filenames if f.endswith('.md') or f.endswith('.markdown')]:
                file_path = os.path.join(dirpath, filename)
                page_tmp = Page(self.config)
                page_tmp.save(open(file_path, 'r').read().decode('utf8'))
                self.pages.append(page_tmp)
                for category in page_tmp.categories:
                    categories_tmp.append(category)

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

    def save_pages(self, pages):
        '''
        Save pages .html file
        '''
        for page in pages:
            self.save_page_file(page, self.dir + '/_sites')

    def save_post_file(self, post, dir):
        if not os.path.exists(dir + post.url):
            os.makedirs(dir + post.url)
        rendered = self.post_template.render(post = post, posts = self.posts, site = self.config, pages = self.pages)
        open(dir + post.url + '/index.html', 'w+').write(rendered.encode('utf8'))

    def save_page_file(self, page, dir):
        page_template = self.j2_env.get_template('_layout/' + page.layout)
        if not os.path.exists(dir + page.url):
            os.makedirs(dir + page.url)
        rendered = page_template.render(page = page, pages = self.pages, site = self.config, posts = self.posts)
        open(dir + page.url + '/index.html', 'w+').write(rendered.encode('utf8'))

    def save_index_pages(self):
        '''
        Generate pagnition like 'http://localhost:8000/blog/page/2/'
        '''
        index_template = self.j2_env.get_template('index.html')
        for i in range(1, self.page_number):
            if not os.path.exists(self.dir + '/_sites/blog/page/' + str(i+1)):
                os.makedirs(self.dir + '/_sites/blog/page/' + str(i+1))
            rendered = index_template.render(posts = self.posts[i*5:(i+1)*5], site = self.config, current_page = i+1, page_number = self.page_number)
            open(self.dir + '/_sites/blog/page/' + str(i+1) + '/index.html', 'w+').write(rendered.encode('utf8'))
