# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function

import os

from crotal.models import Static
from crotal.loader import BaseLoader


class StaticLoader(BaseLoader):
    name = 'static_files'
    Model = Static

    @property
    def path(self):
        return [os.path.join('static'), self.config.static_dir]

    def load_extra_items(self):
        for path, static_file in self.data_mapping[self.name].iteritems():
            static_file.identify_output_path(self.path)
