from termcolor import colored
import sys


def exit():
    sys.exit()

def empty_folder_remove(file_path):
    warning_report('Empty floder removed: %s' % file_path)

def db_create_new_key(source_type):
    warning_report('db.json doesn\'t have key %s' % source_type,
        'key %s created in db.json.' % source_type)

def failed_to_remove_file(source_type, title):
    warning_report('Failed to remove %s: %s. ' % (source_type, title))

def source_illegal(source_type, filename):
    error_report('%s illegal: %s.' % (source_type.title(), filename),
        'Please check it\'s configuration block.')

def no_site_dected():
    error_report('No site detected.',
        'Please make sure that you are in a Crotal folder.')
    exit()

def error_report(message, plus_message=None):
    print colored('[Error]', 'red'), colored(message)
    if plus_message:
        print colored(plus_message)
    exit()

def warning_report(message, plus_message=None):
    print colored('[warning]', 'yellow'), \
        colored(message)
    if plus_message:
        print colored('key', 'green'), \
            colored(plus_message, 'blue')

def info_report(message, plus_message=None, info='info'):
    print colored('['+info+']', 'green'), \
        colored(message)
    if plus_message:
        print colored('key', 'green'), \
            colored(plus_message, 'blue')
