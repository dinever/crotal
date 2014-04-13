#! /usr/bin/env python
import os, sys

from crotal import reporter

def remove_dir(path):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_dir(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        reporter.empty_folder_remove(path)
        os.rmdir(path)
