# -*- coding:utf-8 -*-
import os.path
import re
from unipath import Path
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from _plugins.markdown.jinja_markdown import MarkdownExtension
import settings

dir = Path(__file__).ancestor(1).absolute()


class Views():
    def __init__(self):
        """docstring for __init__"""
        self.templates_path = []
        self.templates = []
        self.other_files = []
        os.path.walk(r'source', self.processDirectory, None)
        self.j2_env = Environment(loader=FileSystemLoader(dir + '/source/'), trim_blocks=True, extensions=[MarkdownExtension])

    def processDirectory(self, args, dirname, filenames):
        for filename in filenames:
            file_path = dirname + '/' + filename
            if len(re.compile(r'\.html$').findall(file_path)) != 0 and len(re.compile(r'^_.*').findall(file_path.replace('source/', ''))) == 0:
                self.templates_path.append(file_path.replace('source/', ''))
            elif len(re.compile(r'\.xml$').findall(file_path)) != 0 and len(re.compile(r'^_.*').findall(file_path.replace('source/', ''))) == 0:
                self.templates_path.append(file_path.replace('source/', ''))
            elif len(re.compile(r'^_.*').findall(filename)) == 0:
                self.other_files.append(file_path.replace('source/', ''))

    def get_templates(self):
        pass

    def save(self, posts, categories):
        for item in self.other_files:
            try:
                os.mkdir(dir + '/' + '_sites/' + item)
            except Exception:
                pass
        for item in self.templates_path:
            rendered = self.j2_env.get_template(item).render(posts=posts, settings = settings, categories = categories)
            open(dir + '/_sites/' + item, 'w+').write(rendered.encode('utf8'))

    def save_posts(self, posts):
        for post in posts:
            if not os.path.exists(dir + '/_sites' + post.url):
                os.makedirs(dir + '/_sites' + post.url)
            print post.url
            rendered = self.j2_env.get_template('_layout/post.html').render(post = post ,posts=posts, settings = settings)
            open(dir + '/_sites' + post.url + '/index.html', 'w+').write(rendered.encode('utf8'))

    def save_get_more(self, posts):
        try:
            os.mkdir(dir+'/'+'_sites/'+'getmoreposts/')
        except:
            pass
        i = 0
        j = 0
        for post in posts:
            i+=1
            if i == 4:
                i =0
                try:
                    os.mkdir(dir+'/'+'_sites/'+'getmoreposts/'+str(j))
                except:
                    pass
                rendered = self.j2_env.get_template('_layout/get_more_posts.html').render(posts = posts[5*(j+1):5*(j+1)+5])
                open(dir + '/' + '_sites/' + 'getmoreposts/' + str(j) + '/' + 'index.html', 'w+').write(rendered.encode('utf-8'))
                for post in posts[5 * (j):5 * (j) + 5]:
                    print post.title
                j += 1
