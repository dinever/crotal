# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from datetime import datetime

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import ImagePattern, IMAGE_LINK_RE

from crotal.lib.pinyin.pinyin import PinYin
from crotal.models import Model
from crotal.models.others import Tag, Category, Archive
from crotal.models.fields import *


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
    'date': 'date',
    'datetime': 'date'
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

MARKDOWN_EXTENSION_CONFIG = \
    {
        'codehilite': {},
    }


class Post(Model):
    """Model `Post` for posts in the blog.

    Attributes:
        PATH: The relative path where this model is related to, please
    use the relative path to this script.
        FILE_EXTENSIONS: Only the files with these file extensions shall
    be read by the model.

        title: Title of the post.
        slug: Slug of the post that may be used in its url.
        pub_date: Publication date of the post.
        tags: A list of Tags that the post is related to.
        categories: A list of Categories that the post belongs to.
        raw_content: The raw markdown content of the post.
        html_content: The html format post content generated from markdown
    file(raw_content).
        short_html_content: A short version of the `html_content`, which
    may be represented on the index page.

    """
    PATH = ['source/posts/']
    FILE_EXTENSIONS = ['.md', '.markdown']

    title = CharField(max_length=200)
    slug = CharField(max_length=200)
    date = DateTimeField(format="%Y-%m-%d %H:%M", other_names=['date'])
    raw_tags = ListField(content_type=str, other_names=['tag', 'tags'])
    raw_categories = ListField(content_type=str, other_names=['category', 'categories'])
    content = TextField()
    short_content = TextField()

    def create(self):
        md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables', ImgExtExtension()], extension_configs=MARKDOWN_EXTENSION_CONFIG)
        md.inlinePatterns['image_link'] = CheckImagePattern(IMAGE_LINK_RE, md, self.config)
        self.url = self.generate_url(self.config.permalink)
        self.content = md.convert(self.content)
        self.images = md.images
        self.short_content = self.content.split('<!--more-->')[0]
        self.categories = [Category.add(item, self) for item in self.raw_categories]
        self.tags = [Tag.add(item, self) for item in self.raw_tags]

    @classmethod
    def load_extra_items(cls, config):
        for object in cls.objects.all():
            Archive.add(object.date, object)
            for category in object.raw_categories:
                Category.add(category, object)
            for tag in object.raw_tags:
                Tag.add(tag, object)
        cls.objects.sort(key='date', reverse=True)

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
            'year': self.date.strftime('%Y'),
            'month': self.date.strftime('%m'),
            'day': self.date.strftime('%d'),
            'title': str(self.slug),
            'category': self.raw_categories[0].lower() if self.raw_categories else 'null',
        }[word]
