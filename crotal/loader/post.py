# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function

import os

from crotal.loader import BaseLoader
from crotal.models import Post, Category, Tag, Archive


class PostLoader(BaseLoader):
    name = 'posts'
    Model = Post
    path = [os.path.join('source', 'posts')]

    def sort_data(self, data):
        data[self.name] = data[self.name].values()
        data[self.name].sort(key=lambda x: x.pub_time, reverse=True)
        data['tags'].sort(key=lambda x: len(x.posts), reverse=True)
        data['categories'].sort(key=lambda x: len(x.name))
        data['archives'].sort(key=lambda x: x.datetime, reverse=True)
        return data

    def load_extra_items(self):
        self.load_categories()
        self.load_tags()
        self.load_archives()

    def load_categories(self):
        categories = {}
        for _, post in self.data_mapping[self.name].iteritems():
            post.categories = []
            for category_name in post.raw_categories:
                category_url = category_name.lower()
                if category_url not in categories:
                    category_obj = Category(category_name, category_url)
                    category_obj.add(post)
                    categories[category_url] = category_obj
                else:
                    categories[category_url].add(post)
                post.categories.append(categories[category_url])
        self.data_mapping['categories'] = categories.values()

    def load_tags(self):
        tags = {}
        for _, post in self.data_mapping[self.name].iteritems():
            tag_list = []
            for tag in post.raw_tags:
                tag_url = tag.lower().replace('.', '_')
                if tag_url not in tags:
                    tag_obj = Tag(tag, tag_url)
                    tag_obj.add(post)
                    tags[tag_url] = tag_obj
                    tag_list.append(tag_obj)
                else:
                    tags[tag_url].add(post)
                    tag_list.append(tags[tag_url])
            post.tags = tag_list
        self.data_mapping['tags'] = tags.values()

    def load_archives(self):
        archives = {}
        for _, post in self.data_mapping[self.name].iteritems():
            a = Archive(post.pub_time)
            if a.__repr__() in archives:
                archives[a.__repr__()].posts.append(post)
            else:
                a.posts.append(post)
                archives[a.__repr__()] = a
        self.data_mapping['archives'] = sorted(archives.values())
