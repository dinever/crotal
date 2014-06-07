#!/usr/bin/python

import os
from crotal.collector import Collector

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
        new_filenames, old_filenames, removed_filenames = self.detect_new_filenames('static')
        self.parse_new_filenames(new_filenames, src_dir, tar_dir)
        self.parse_removed_files(removed_filenames, src_dir)
        print new_filenames
        print old_filenames
        print removed_filenames
        for filename in new_filenames:
            dir_path = os.path.dirname(filename)
            print dir_path
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
            print filename
            self.database.remove_item('static', filename)
            os.remove(filename)

if __name__ == '__main__':
    copy_dir(src_dir, tar_dir)
