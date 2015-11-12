# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from markdown import markdown

from crotal.models import Model
from crotal.models.fields import *


class Page(Model):
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
        html_content: The html format post content genearted from markdown
    file(raw_content).
        short_html_content: A short version of the `html_content`, which
    may be represented on the index page.

    """
    PATH = ['source/pages/']
    FILE_EXTENSIONS = ['.md', '.markdown']

    title = CharField(max_length=200)
    slug = CharField(max_length=200)
    url = CharField()
    date = DateTimeField(format="%Y-%m-%d %H:%M")
    tags = ListField(content_type=str)
    categories = ListField(content_type=str)
    raw_content = TextField()
    html_content = TextField()
    short_html_content = TextField()

    def create(self):
        self.content = markdown(self.content, extensions=['fenced_code', 'codehilite', 'tables'])
