from termcolor import colored
import sys


class Reporter:

    def exit(self):
        sys.exit()

    def empty_folder_remove(self, file_path):
        self.warning_report('Empty floder removed: %s' % file_path)

    def db_create_new_key(self, source_type):
        self.warning_report('db.json doesn\'t have key %s' % source_type,
            'key %s created in db.json.' % source_type)

    def failed_to_remove_file(self, source_type, title):
        self.warning_report('Failed to remove %s: %s. ' % (source_type, title))

    def source_illegal(self, source_type, filename):
        self.error_report('%s illegal: %s.' % (source_type.title(), filename),
            'Please check it\'s configuration block.')

    def no_site_dected(self):
        self.error_report('No site detected.',
            'Please make sure that you are in a Crotal folder.')
        self.exit()

    def error_report(self, message, plus_message=None):
        print colored('[Error]', 'red'), colored(message, 'green')
        if plus_message:
            print colored(plus_message, 'green')
        self.exit()

    def warning_report(self, message, plus_message=None):
        print colored('[warning]', 'yellow'), \
            colored(message)
        if plus_message:
            print colored('key', 'green'), \
                colored(plus_message, 'blue')

    def info_report(self, message, plus_message=None):
        print colored('[info]', 'green'), \
            colored(message)
        if plus_message:
            print colored('key', 'green'), \
                colored(plus_message, 'blue')
