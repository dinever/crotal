#!/usr/bin/python

import os

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

if __name__ == '__main__':
    copy_dir(src_dir, tar_dir)
