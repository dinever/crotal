from datetime import datetime
import math


class Category():

    def __init__(self, category):
        self.title = category
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

    def __str__(self):
        return self.title.encode('utf8')


class Tag():

    def __init__(self, tag):
        self.title = tag
        self.posts = []
        self.font_size = float

    def add_post(self, post):
        self.posts.append(post)

    def save(self):
        self.font_size = 14 + 8*math.log(self.posts.__len__())


class Archive(datetime):

    def __init__(self, pub_time):
        year = pub_time.year
        month = pub_time.month
        day = pub_time.day
        datetime.__init__(self, year, month, day)
        self.post = []

    def add_post(self, post):
        self.posts.append(post)
