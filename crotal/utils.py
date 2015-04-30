__author__ = 'dinever'

import os
import shutil


def make_dirs(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def copy_file(src_dir, tar_dir):
    make_dirs(tar_dir)
    shutil.copyfile(src_dir, tar_dir)


def copy_dir(src_dir, tar_dir):
    for item in os.listdir(src_dir):
        source_file = os.path.join(src_dir, item)
        target_file = os.path.join(tar_dir, item)

        if os.path.isfile(source_file):
            if not os.path.exists(tar_dir):
                os.makedirs(tar_dir)
            if not os.path.exists(tar_dir) or (os.path.exists(tar_dir) and (os.path.getsize(source_file))):
                open(target_file, "wb").write(open(source_file, "rb").read())
            else:
                pass
        if os.path.isdir(source_file):
            copy_dir(source_file, target_file)


def output_file(file_path, file_content):
    make_dirs(file_path)
    open(file_path, 'w+').write(file_content)


def generate_path(url, output_path='', site_root=''):
    """
    Generates a path based on url.
    :param output_path:
    Example:
        >>> generate_path('/category/programming/', output_path='/home/user/', site_root='/demo/')
        "/home/user/demo/category/programming/index.html"
    """
    path = [] if not site_root else [site_root.replace('/', '')]
    for item in url.split('/'):
        if item:
            path.append(item)
    if '.' not in path[-1] and path[-1].split('.'):
        path.append('index.html')
    return os.path.join(output_path, *path)
