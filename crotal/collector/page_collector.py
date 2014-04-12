import os
import time

from crotal.models.pages import Page
from crotal.models.categories import Category
from crotal.reporter import Reporter
from crotal.collector import Collector

reporter = Reporter()

class PageCollector(Collector):
    def __init__(self, current_dir, database, config):
        Collector.__init__(self)
        self.config = config
        self.database = database
        self.current_dir = current_dir
        self.pages_dir = os.path.normpath(
            os.path.join(
                self.current_dir, 'source', 'pages'))
        self.pages = []
        self.removed_pages = []
        self.new_pages = []
        self.pages_files = self.process_directory(self.pages_dir)

    def run(self):
        new_filenames, old_filenames, removed_filenames = self.detect_new_filenames('pages')
        self.parse_old_pages(old_filenames)
        self.parse_new_pages(new_filenames)
        self.parse_removed_pages(removed_filenames)
        self.pages_sort()

    def parse_old_pages(self, filenames):
        for filename in filenames:
            page_content = self.database.get_item_content('pages', filename)
            page_tmp = Page(filename, self.config)
            page_tmp.parse_from_db(page_content)
            self.pages.append(page_tmp)
            page_dict = page_tmp.__dict__.copy()
            page_dict['pub_time'] = time.mktime(
                page_dict['pub_time'].timetuple())
            page_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.pages_dir,
                    filename))
            page_dict_in_db  = {
                'last_mod_time': last_mod_time,
                'content': page_dict}
            self.database.set_item('pages', filename, page_dict_in_db)

    def parse_new_pages(self, filenames):
        for filename in filenames:
            file_path = os.path.join(self.current_dir, filename)
            page_tmp = Page(filename, self.config)
            page_tmp.save(
                open(
                    os.path.join(
                        self.pages_dir,
                        filename),
                    'r').read().decode('utf8'))
            self.pages.append(page_tmp)
            self.new_pages.append(page_tmp)
            page_dict = page_tmp.__dict__.copy()
            page_dict['pub_time'] = time.mktime(
                page_dict['pub_time'].timetuple())
            page_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.pages_dir,
                    filename))
            page_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': page_dict}
            self.database.set_item('pages', filename, page_dict_in_db)

    def parse_removed_pages(self, filenames):
        site_dir = os.path.join(self.current_dir, '_sites')
        for filename in filenames:
            page_content = self.database.get_item_content('pages', filename)
            page_tmp = Page(filename, self.config)
            page_tmp.parse_from_db(page_content)
            self.database.remove_item('pages', filename)
            self.removed_pages.append(page_tmp)
            dname = os.path.join(site_dir, page_tmp.url.strip("/\\"))
            filename = os.path.join(dname, 'index.html')

    def remove_pages(self):
        site_dir = os.path.join(self.current_dir, '_sites')
        for page in self.removed_pages:
            dname = os.path.join(site_dir, page.url.strip("/\\"))
            filename = os.path.join(dname, 'index.html')
            try:
                os.remove(filename)
            except:
                reporter.failed_to_remove_file('page', page.title)

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
