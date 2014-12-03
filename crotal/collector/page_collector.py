import os

import time

from crotal.models.pages import Page
from crotal.collector import Collector
from crotal import logger
from crotal import settings


class PageCollector(Collector):
    def __init__(self, database):
        Collector.__init__(self)
        self.database = database
        self.pages = []
        self.removed_pages = []
        self.new_pages = []
        self.pages_files = self.process_directory(settings.PAGES_DIR)

    def run(self):
        new_filename_list, old_filename_list, removed_filename_list = \
            self.detect_new_filename_list('pages')
        self.parse_removed_pages(removed_filename_list)
        self.parse_old_pages(old_filename_list)
        self.parse_new_pages(new_filename_list)
        self.pages_sort()

    def parse_old_pages(self, filename_list):
        for filename in filename_list:
            page_content = self.database.get_item('pages', filename)['content']
            page_tmp = Page(filename)
            page_tmp.parse_from_db(page_content)
            self.pages.append(page_tmp)
            page_dict = page_tmp.__dict__.copy()
            page_dict['pub_time'] = time.mktime(
                page_dict['pub_time'].timetuple())
            page_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(filename))
            page_dict_in_db  = {
                'last_mod_time': last_mod_time,
                'content': page_dict}
            self.database.set_item('pages', filename, page_dict_in_db)

    def parse_new_pages(self, filename_list):
        for filename in filename_list:
            try:
                page_content = self.database.get_item('pages', filename)['content']
                page_tmp = Page(filename=filename)
                page_tmp.parse_from_db(page_content)
                dname = os.path.join(settings.PUBLISH_DIR, page_tmp.url.strip("/\\"))
                filepath = os.path.join(dname, 'index.html')
                if os.path.exists(filepath):
                    os.remove(filepath)
                else:
                    logger.warning("Field to remove file: '{0}".format(page_tmp.title))
            except Exception, e:
                pass
            page_tmp = Page(filename)
            page_tmp.save(
                open(os.path.join(filename),
                    'r').read().decode('utf8'))
            self.pages.append(page_tmp)
            self.new_pages.append(page_tmp)
            page_dict = page_tmp.__dict__.copy()
            page_dict['pub_time'] = time.mktime(
                page_dict['pub_time'].timetuple())
            page_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(filename))
            page_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': page_dict}
            self.database.set_item('pages', filename, page_dict_in_db)

    def parse_removed_pages(self, filename_list):
        for filename in filename_list:
            page_content = self.database.get_item('pages', filename)['content']
            page_tmp = Page(filename)
            page_tmp.parse_from_db(page_content)
            self.database.remove_item('pages', filename)
            self.removed_pages.append(page_tmp)
            dname = os.path.join(settings.PUBLISH_DIR, page_tmp.url.strip("/\\"))
            filepath = os.path.join(dname, 'index.html')
            try:
                os.remove(filepath)
            except:
                logger.warning("Field to remove file: '{0}".format(page_tmp.title))

    def pages_sort(self):
        for i in range(len(self.pages)):
            for j in range(len(self.pages)):
                if self.pages[i].order < self.pages[j].order:
                    self.pages[i], self.pages[j] = self.pages[j], self.pages[i]
        for prev, current, next in self.get_prev_and_next(self.pages):
            current.prev = prev
            current.next = next

    def get_prev_and_next(self, iterable):
        iterator = iter(iterable)
        prev = None
        item = iterator.next()  # throws StopIteration if empty.
        for next in iterator:
            yield (prev, item, next)
            prev = item
            item = next
        yield (prev, item, None)
