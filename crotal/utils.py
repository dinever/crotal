#!/usr/bin/python

import os
import sys
import yaml

from crotal import logger
from crotal import settings
from crotal.collector import Collector

def remove_dir(path):
    if not os.path.isdir(path):
        return

    # remove empty sub-folders
    files = os.listdir(path)
    for f in files:
        full_path = os.path.join(path, f)
        if os.path.isdir(full_path):
            remove_dir(full_path)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        logger.warning("Empty folder removed: '{0}".format(path))
        os.rmdir(path)

def copy_dir(src_dir, tar_dir):
    for item in os.listdir(src_dir):
        srcFile = os.path.join(src_dir, item)
        tarFile = os.path.join(tar_dir, item)

        if os.path.isfile(srcFile):
            if os.path.exists(tar_dir) is False:
                os.makedirs(tar_dir)
            if os.path.exists(tar_dir) is False or (os.path.exists(tar_dir) and (os.path.getsize(srcFile))):
                open(tarFile, "wb").write(open(srcFile, "rb").read())
            else:
                pass
        if os.path.isdir(srcFile):
            copy_dir(srcFile, tarFile)

class FileCopier(Collector):

    def __init__(self, current_dir, database):
        self.current_dir = current_dir
        self.database = database
        self.current_dir = current_dir

    def copy_dir2(self, src_dir, tar_dir):
        self.static_files = self.process_directory(src_dir)
        new_filenames, old_filenames, removed_filenames = self.detect_new_filename_list('static')
        self.parse_new_filenames(new_filenames, src_dir, tar_dir)
        self.parse_removed_files(removed_filenames, src_dir)
        for filename in new_filenames:
            dir_path = os.path.dirname(filename)
        """for item in os.listdir(src_dir):
            srcFile = os.path.join(src_dir, item)
            tarFile = os.path.join(tar_dir, item)

            if os.path.isfile(srcFile):
                if os.path.exists(tar_dir) is False:
                    os.makedirs(tar_dir)
                if os.path.exists(tar_dir) is False or (os.path.exists(tar_dir) and (os.path.getsize(srcFile))):
                    open(tarFile, "wb").write(open(srcFile, "rb").read())
                else:
                    pass
            if os.path.isdir(srcFile):
                self.copy_dir(srcFile, tarFile)"""

    def parse_new_filenames(self, filenames, src_dir, tar_dir):
        for filename in filenames:
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.current_dir,
                    filename))
            static_file_dict_in_db = {
                'last_mod_time': last_mod_time,
                }
            self.database.set_item('static', filename, static_file_dict_in_db)
            src_file = os.path.join(self.current_dir, src_dir, filename)
            tar_file = os.path.join(self.current_dir, tar_dir, filename)
            dir_path = os.path.dirname(tar_file)
            dname = os.path.join(self.current_dir, dir_path.strip("/\\"))
            if not os.path.exists(dname):
                os.makedirs(dname)
            open(tar_file, "wb").write(open(src_file, "rb").read())


    def parse_removed_files(self, filenames, src_dir):
        for filename in filenames:
            self.database.remove_item('static', filename)
            os.remove(filename)


def load_config_file():
    try:
        _config.yml = open(settings.CONFIG_PATH, 'r').read()
    except Exception:
        logger.error('No "_config.yml" file found for the current directory.')
        sys.exit()
    config_dict = yaml.load(_config.yml)
    for item in config_dict:
        setattr(settings, item, config_dict[item])
