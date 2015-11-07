import os
import time
import shutil

from crotal import logger


def locate_base_dir():
    current_dir = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current_dir, '_config.yml')):
            return current_dir
        elif current_dir == os.path.dirname(current_dir):
            return None
        else:
            current_dir = os.path.dirname(current_dir)


def make_dirs(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def copy_file(src_dir, tar_dir):
    if os.path.exists(src_dir):
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


def stop_watch(func):
    def count_func_time(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info("Execution Time of {0}: {1:.2f} seconds".format(func.__name__, end - start))
        return result
    return count_func_time


def memoize(function):
    """
    Simply cache function returns.
    """
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


def get_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                           for g in get_subclasses(s)]
