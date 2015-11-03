# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from crotal import logger


class BaseLoader(object):
    name = ''

    modified_file_list = []
    unmodified_file_list = []
    removed_file_list = []

    def __init__(self, database, config):
        self.file_list = []
        self.config = config
        self._table = database.get_table(self.name)
        self.data_mapping = {
            self.name: {},
        }
        if not isinstance(self.path, list):
            self.file_list += self.scan_files(self.config.base_dir, self.path)
        else:
            for path in self.path:
                self.file_list += self.scan_files(self.config.base_dir, path)

    @property
    def path(self):
        """
        Static path for loaders can be indicated with '_path' in the
        class, but if you want to define some dynamic path, like a path
        indicates the current theme the user is using, you may leave
        '_path' undefined, and define the logic to generate the
        dynamic path inside this method.
        """
        return ''

    def load(self, update_data):
        self.classify_files()
        self.load_main_items()
        self.load_extra_items()
        update_data(self.sort_data(self.data_mapping.copy()))

    def sort_data(self, data):
        return data

    def load_extra_items(self):
        pass

    def scan_files(self, base_dir, path):
        """
        This method returns the list of all the source files in the directory
        indicated. Notice that file started with '.' will not be
        included.
        """
        file_list = []
        absolute_path = os.path.join(base_dir, path)
        for dir_, _, files in os.walk(absolute_path):
            for file_name in files:
                absolute_file = os.path.join(dir_, file_name)
                if not file_name.startswith('.'):
                    file_path = os.path.relpath(absolute_file, base_dir)
                    file_list.append(file_path)
        return file_list

    def classify_files(self):
        """
        This method distinguishes new, old and removed files.
        modified_file_list: The file_list user just added or updated.
        unmodified_file_list: The file_list which haven't been changed.
        removed_file_list: The file_list which is removed.(Existed in db.json,
            but not in source folder.)
        """
        db_file_list = self._table.content
        self.modified_file_list = list(set(self.file_list) - set(db_file_list))
        self.unmodified_file_list = list(set(db_file_list) - (set(db_file_list) - set(self.file_list)))
        self.removed_file_list = list(set(db_file_list) - set(self.file_list))
        for file_path in self.unmodified_file_list:
            absolute_file_path = os.path.join(self.config.base_dir, file_path)
            last_mod_time = os.path.getmtime(absolute_file_path)
            last_mod_time_in_db = self._table.get(file_path)['last_mod_time']
            if last_mod_time != last_mod_time_in_db:
                self.modified_file_list.append(file_path)
                self.unmodified_file_list.remove(file_path)

    def single_file_on_change(self, file_path, event_type, callback):
        if event_type in ('created', 'modified'):
            self.load_single_file(file_path)
        elif event_type == 'deleted':
            self.remove_single_file(file_path)
        self.load_extra_items()
        callback(self.sort_data(self.data_mapping.copy()))

    def load_single_file(self, file_path):
        if os.path.basename(file_path).startswith('.'):
            return
        item = self.Model.from_file(file_path, self.config)
        if item:
            self.data_mapping[self.name][file_path] = item
            self._table[file_path] = item.to_db(os.path.join(self.config.base_dir, file_path))
        else:
            logger.error(message="Incorrect file format: {0}".format(file_path))

    def remove_single_file(self, file_path):
        if file_path in self.data_mapping[self.name]:
            del self.data_mapping[self.name][file_path]
        del self._table[file_path]

    def load_main_items(self):
        for file_path in self.modified_file_list:
            self.load_single_file(file_path)

        for file_path in self.unmodified_file_list:
            tmp = self.Model.from_db(file_path, self.config, self._table[file_path])
            self.data_mapping[self.name][file_path] = tmp

        for file_path in self.removed_file_list:
            self.remove_single_file(file_path)

        for file_path, item in self.data_mapping[self.name].iteritems():
            absolute_path = os.path.join(self.config.base_dir, file_path)
            self._table[file_path] = item.to_db(absolute_path)
