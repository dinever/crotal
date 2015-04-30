# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from datetime import datetime

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import ImagePattern, IMAGE_LINK_RE

from crotal.plugins.pinyin.pinyin import PinYin
from crotal.models import Model



class CheckImagePattern(ImagePattern):

    def __init__(self, IMAGE_LINK_RE, md, config):
        self.config = config
        super(CheckImagePattern, self).__init__(IMAGE_LINK_RE, md)

    def handleMatch(self, m):
        node = ImagePattern.handleMatch(self, m)
        image_src = node.attrib['src']
        if not image_src.startswith('http'):
            if image_src.startswith('/'):
                node.attrib['src'] = "{0}{1}".format(self.config.root_path, image_src[1:])
        return node

FIELD_NAME_CONVERT = {
    'category': 'raw_categories',
    'categories': 'raw_categories',
    'tags': 'raw_tags',
    'tag': 'raw_tags',
    'date': 'pub_time',
    'datetime': 'pub_time'
}


# First create the treeprocessor

class ImgExtractor(Treeprocessor):

    def run(self, doc):
        "Find all images and append to markdown.images. "
        self.markdown.images = []
        for image in doc.findall('.//img'):
            self.markdown.images.append(image.get('src'))


class ImgExtExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        img_ext = ImgExtractor(md)
        md.treeprocessors.add('imgext', img_ext, '>inline')


class Post(Model):

    def __init__(self, path, config, title, date='', categories='', tags='', content='', slug='', **extras):
        self.path = path
        self.title = title
        self.pub_time = datetime.strptime(date, "%Y-%m-%d %H:%M")
        self.categories = []
        self.raw_categories = self.__class__.generate_list(categories)
        self.tags = []
        self.raw_tags = self.__class__.generate_list(tags)
        md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables', ImgExtExtension()])
        md.config = config
        md.inlinePatterns['image_link'] = CheckImagePattern(IMAGE_LINK_RE, md, config)
        self.content = md.convert(content)
        self.images = md.images
        self.front_content = self.content.split('<!--more-->')[0]
        self.author = extras['author'] if 'author' in extras else config.author
        if slug:
            self.slug = slug
        else:
            pinyin = PinYin()
            pinyin.load_word()
            self.slug = pinyin.hanzi2pinyin_split(string=self.title, split='-').lower()
        self.url = self.generate_url(config.permalink)
        for name, value in extras.iteritems():
            setattr(self, name, value)

    @staticmethod
    def generate_list(string):
        """
        This method generates a list from a string with the format of "word1, word2, word3"
        """
        if string and (isinstance(string, str) or isinstance(string, unicode)):
            return [a.strip() for a in string.split(',')]
        elif isinstance(string, list):
            return [a.strip() for a in string]
        else:
            return list()

    def generate_url(self, permalink):
        """
        Save the post url, refering to the permalink in the config file.
        The permalink is seperated into servel parts from '/'.
        If one part of it startswith ':', then we should find whether there
            is attribute with the same name in the post.
        If not, we regard it as a string

        example:
        post/:year/:month/:title
        will be generated to a url like 'crotal.org/post/2013/11/hello-world/'
        """
        url = ''
        for item in permalink.split('/'):
            if item.startswith(':'):
                url = url + \
                    self.escape_keywords(item.replace(':', '')) + '/'
            else:
                url = url + item + '/'
        return url.decode('utf8')

    def escape_keywords(self, word):
        return {
            'year': self.pub_time.strftime('%Y'),
            'month': self.pub_time.strftime('%m'),
            'day': self.pub_time.strftime('%d'),
            'title': str(self.slug),
            'category': self.raw_categories[0].lower() if self.raw_categories else 'null',
        }[word]
