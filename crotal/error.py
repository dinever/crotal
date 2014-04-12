from termcolor import colored
import sys


class ErrorReporter:

    def exit(self):
        sys.exit()

    def no_site_dected(self):
        print colored('[Error]', 'red'), colored('No site detected.', 'green')
        print colored('Please make sure that you are in a Crotal site.', 'green')
        self.exit()
