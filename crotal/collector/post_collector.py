import os

import time

from crotal.models.posts import Post
from crotal.models.others import Category, Tag, Archive
from crotal.collector import Collector
from crotal import logger
from crotal import settings


class PostCollector(Collector):
    def __init__(self, database):
        super(PostCollector, self).__init__()
        self.database = database
        self.posts = []
        self.new_posts = []
        self.removed_posts = []
        self.categories = {}
        self.tags = {}
        self.archives = []
        self.posts_files = self.process_directory(settings.POSTS_DIR)
        self.page_number = 0

    def run(self):
        new_filenames, old_filenames, removed_filenames = self.detect_new_filename_list('posts')
        self.parse_removed_posts(removed_filenames)
        self.parse_old_posts(old_filenames)
        self.parse_new_posts(new_filenames)
        self.posts_sort()
        self.collect_others()
        self.save_others()
        self.page_number = len(self.posts) / 5

    def collect_others(self):
        '''
        Collect categories and tags in post object list.
        '''
        self.collect_categories()
        self.collect_tags()

    def collect_categories(self):
        '''
        Collect the categories in a sigle post object.
        '''
        for post in self.posts:
            if hasattr(post, 'categories'):
                for category in post.categories:
                    if category in self.categories:
                        self.categories[category].add_post(post)
                    else:
                        self.categories[category] = Category(category)
                        self.categories[category].add_post(post)

    def collect_tags(self):
        '''
        Collect the tags in a sigle post object.
        '''
        for post in self.posts:
            if hasattr(post, 'tags'):
                for tag in post.tags:
                    if tag in self.tags:
                        self.tags[tag].add_post(post)
                    else:
                        self.tags[tag] = Tag(tag)
                        self.tags[tag].add_post(post)

    def collect_archives(self, post): # TODO
        '''
        Collect the archives in a sigle post object.
        (This method has not been used)
        '''
        Archive(post.pub_time)
        self.archives.append(Archive(post.pub_time))

    def save_others(self):
        '''
        After all of the tags is collected
        '''
        for tag in self.tags.values():
            tag.save()

    def parse_old_posts(self, filenames):
        for filename in filenames:
            post_content = self.database.get_item('posts', filename)['content']
            post_tmp = Post(filename=filename)
            post_tmp.parse_from_db(post_content)
            self.posts.append(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(
                post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(filename))
            post_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': post_dict}
            self.database.set_item('posts', filename, post_dict_in_db)

    def parse_new_posts(self, filenames):
        for filename in filenames:
            try:
                post_content = self.database.get_item('posts', filename)['content']
                post_tmp = Post(filename=filename)
                post_tmp.parse_from_db(post_content)
                dname = os.path.join(settings.PUBLISH_DIR, post_tmp.url.strip("/\\"))
                filepath = os.path.join(dname, 'index.html')
                try:
                    os.remove(filepath)
                except Exception, e:
                    logger.warn("Field to remove file: '{0}".format(post_tmp.title))
            except Exception, e:
                pass
            post_tmp = Post(filename=filename)
            file_content = open(os.path.join(filename),'r')\
                .read().decode('utf8')
            if not post_tmp.check_illegal(file_content, filename=filename):
                # If the post_content is not illegal, pass it.
                logger.warn("This post doesn't have a correct format: '{0}".format(filename))
                continue
            else:
                post_tmp.parse()
            self.posts.append(post_tmp)
            self.new_posts.append(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(
                post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(filename))
            post_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': post_dict}
            self.database.set_item('posts', filename, post_dict_in_db)

    def parse_removed_posts(self, filenames):
        for filename in filenames:
            post_content = self.database.get_item('posts', filename)['content']
            post_tmp = Post(filename=filename)
            post_tmp.parse_from_db(post_content)
            self.database.remove_item('posts', filename)
            self.removed_posts.append(post_tmp)
            dname = os.path.join(settings.PUBLISH_DIR, post_tmp.url.strip("/\\"))
            filepath = os.path.join(dname, 'index.html')
            try:
                os.remove(filepath)
            except Exception, e:
                logger.warn("Field to remove file: '{0}".format(post_tmp.title))


    def posts_sort(self):
        self.posts.sort(key=lambda c:c.pub_time)
        self.posts.reverse()
