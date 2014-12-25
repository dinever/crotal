import os
import re

import fnmatch
from threading import Thread
import crotal.logger as logger

file_exts = ["*.*~", "*.swp", "*.swx"]
EXCLUDE_PATTERN = r'|'.join([fnmatch.translate(pat) for pat in file_exts]) or r'$.'

class Collector(Thread):

    def process_directory(self, directory):
        """
        This method returns the list of all the source files in the directory
        indicated. Notice that filename started with '-' or '.' will not be
        included.
        """
        filename_list = []
        for dir_, _, files in os.walk(directory):
            for filename in files:
                if re.match(EXCLUDE_PATTERN, filename):
                    logger.info("skip %s" % filename)
                    continue
                relative_dir = os.path.relpath(dir_, directory)
                relative_file = os.path.join(relative_dir, filename)
                absolute_file = os.path.join(dir_, filename)
                if relative_file.startswith('_') is False and \
                        filename.startswith('.') is False:
                    filepath = os.path.join(directory, relative_file)
                    filename_list.append(os.path.normpath(filepath))
        return filename_list

    def detect_new_filename_list(self, source_type):
        """
        This method distinguishs new, old and removed files.
        new_filename_list: The filename_list user just added or updated.
        old_filename_list: The filename_list which haven't been changed.
        removed_filename_list: The filename_list which is removed.(Existed in db.json,
            but not in source folder.)
        """
        filename_list = getattr(self, source_type+'_files')
        db_filename_list = self.database.load(source_type)
        new_filename_list = list(set(filename_list) - set(db_filename_list))
        old_filename_list = list(
            set(db_filename_list) - (set(db_filename_list) - set(filename_list)))
        removed_filename_list = list(set(db_filename_list) - set(filename_list))
        for filename in old_filename_list:
            last_mod_time = os.path.getmtime(filename)
            last_mod_time_in_db = self.database.db[
                source_type][filename]['last_mod_time']
            if last_mod_time != last_mod_time_in_db:
                new_filename_list.append(filename)
                old_filename_list.remove(filename)
        return new_filename_list, old_filename_list, removed_filename_list
