import re
from datetime import datetime

from markdown import markdown
import yaml
from crotal.plugins.pinyin.pinyin import PinYin

class Post():

    def __init__(self, config):
        self.config = config
        self.header = ''
        self.title = ''
        self.pub_time = datetime
        self.categories = []
        self.content = ''
        self.html = ''
        self.front_html = ''
        self.author = ''
        self.slug = ''
        self.url = ''
        self.draft = False

    def save(self, content):
        get_header = re.compile(r'---[\s\S]*?---')
        self.header = get_header.findall(content)[0]
        self.content = content.replace(self.header, '', 1)
        self.save_html()
        self.header = self.header.replace('---','')
        post_info = yaml.load(self.header)
        for item in post_info:
            '''
            if item is date, convert it to datetime object, then save it to post.pub_time.
            if item is categories, to save it to post.categories as a list.
            if item is tags, save it to post.tags as a list, too.
            '''
            if item == 'date':
                pub_time = datetime.strptime(post_info['date'],"%Y-%m-%d %H:%M")
                setattr(self, 'pub_time', pub_time)
            elif item == 'categories' or item == 'tags':
                if type(post_info[item]) == str:
                    setattr(self, item, post_info[item].split(','))
                elif type(post_info[item]) == list:
                    setattr(self, item, post_info[item])
                else:
                    setattr(self, item, [])
            elif item == 'title' or item == 'slug':
                if type(item) is int:
                    setattr(self, item, str(post_info[item]))
                else:
                    setattr(self, item, post_info[item])
            else:
                setattr(self, item, post_info[item])

        if not post_info.has_key('author'):
            self.author = self.config.author

        if not post_info.has_key('slug'):
            '''
            if there is key "slug" in post_info, use it as the url.
            if there isn't, we generate post url from title.
            PinYin is used for converting Chinese to Chinese pinyin.
            '''
            slug = PinYin()
            slug.load_word()
            self.slug = slug.hanzi2pinyin_split(string = self.title, split="-")
        self.generate_url()

    def generate_url(self):
        for item in self.config.permalink.split('/'):
            '''
            Save the post url, refering to the permalink in the config file.
            The permalink is seperated into servel parts from '/'.
            If one part of it startswith ':', then we should find whether there
                is attribute with the same name in the post.
            If not, we regard it as a string

            example:
            post/:year/:month/:title
            will be generated to a url like 'crotal.org/post/2013/11/hello-world/'
            '''
            if item.startswith(':'):
                self.url = self.url + '/' + self.escape_keywords(item.replace(':',''))
            else:
                self.url = self.url + '/' + item
        self.url = self.url.decode('utf8')

    def escape_keywords(self, word):
        return {
            'year': self.pub_time.strftime('%G'),
            'month': self.pub_time.strftime('%m'),
            'day': self.pub_time.strftime('%d'),
            'title': str(self.slug),
        }[word]

    def save_html(self):
        self.html = markdown(self.content, extensions=['fenced_code','codehilite','tables'])
        self.front_html = self.html.split('<!--more-->')[0]
