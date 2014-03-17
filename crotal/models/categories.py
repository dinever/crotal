from .pages import Page
from .posts import Post


class Category():

    def __init__(self, config, category):
        self.title = category
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)
