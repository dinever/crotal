import os
import time

from ..models.posts import Post
from ..models.others import Category, Tag, Archive
from .. import reporter
from ..collector import Collector
from crotal.config import config


class StaticCollector(Collector):
    def __init__(self, database, config):
        super(StaticCollector, self).__init__()
        self.database = database
        self.files = []
        self.new_files = []
        self.removed_files = []
        self.static_files = self.process_directory(config.static_dir)
        self.theme_static_files = self.process_directory(config.theme_static_dir)
        print config.theme_static_dir
        print self.theme_static_files
        self.page_number = 0

    def run(self):
        new_filenames, old_filenames, removed_filenames = self.detect_new_filenames('theme_static')
        self.parse_new_static_files(new_filenames, 'theme_static')
        self.parse_removed_static_files(removed_filenames, 'theme_static')
        new_filenames, old_filenames, removed_filenames = self.detect_new_filenames('static')
        print new_filenames
        self.parse_new_static_files(new_filenames, 'static')
        self.parse_removed_static_files(removed_filenames, 'static')

    def parse_new_static_files(self, filenames, static_type):
        for filename in filenames:
            last_mod_time = os.path.getmtime(filename)
            static_dict_in_db = {
                'last_mod_time': last_mod_time
            }
            self.database.set_item(static_type, filename, static_dict_in_db)
            relativ_path = os.path.relpath(filename, getattr(config, static_type + '_dir'))
            output_path = os.path.join(config.publish_dir, relativ_path)
            self.make_dirs(os.path.join(config.publish_dir, output_path))
            print output_path
            open(output_path, "wb").write(open(filename, "rb").read())

    def parse_removed_static_files(self, filenames, static_type):
        for filename in filenames:
            relativ_path = os.path.relpath(filename, getattr(config, static_type + '_dir'))
            output_path = os.path.join(config.publish_dir, relativ_path)
            self.database.remove_item('static', filename)
            try:
                os.remove(output_path)
            except Exception, e:
                reporter.failed_to_remove_file('static file', output_path)

    def make_dirs(self, filepath):
        dir_path = os.path.dirname(filepath)
        try:
            os.makedirs(dir_path)
        except Exception:
            pass
