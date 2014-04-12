import re
from datetime import datetime

from markdown import markdown
import yaml
from crotal.plugins.pinyin.pinyin import PinYin


class Page():

    def __init__(self, filename, config):
        self.config = config
        self.filename = filename
        self.header = ''
        self.title = ''
        self.pub_time = datetime
        self.categories = []
        self.html = ''
        self.url = ''
        self.draft = False

    def parse_from_db(self, content):
        for key in content:
            if key == 'pub_time':
                setattr(self, key, datetime.fromtimestamp(content[key]))
            else:
                setattr(self, key, content[key])

    def save(self, content):
        get_header = re.compile(r'---[\s\S]*?---')
        self.header = get_header.findall(content)[0]
        self.content = content.replace(self.header, '', 1)
        self.save_html()
        self.header = self.header.replace('---', '')
        post_info = yaml.load(self.header)
        for item in post_info:
            '''
            if item is date, convert it to datetime object, then save it to post.pub_time.
            if item is categories, to save it to post.categories as a list.
            if item is tags, save it to post.tags as a list, too.
            '''
            if item == 'date':
                pub_time = datetime.strptime(
                    post_info['date'],
                    "%Y-%m-%d %H:%M")
                setattr(self, 'pub_time', pub_time)
            elif item == 'categories' or item == 'tags':
                if isinstance(post_info[item], str):
                    setattr(self, item, post_info[item].split(','))
                elif isinstance(post_info[item], list):
                    setattr(self, item, post_info[item])
                else:
                    setattr(self, item, [])
            elif item == 'title' or item == 'slug':
                if isinstance(item, int):
                    setattr(self, item, str(post_info[item]))
                else:
                    setattr(self, item, post_info[item])
            else:
                setattr(self, item, post_info[item])

        if not hasattr(self, 'order'):
            self.order = 1000

    def save_html(self):
        self.html = markdown(
            self.content,
            extensions=[
                'fenced_code',
                'codehilite',
                'tables'])
        self.front_html = self.html.split('<!--more-->')[0]
