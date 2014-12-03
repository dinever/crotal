import os
import json

from crotal import settings
from crotal import logger


class Database(object):
    """
    Database is the interface to the file db.json.
    source_type includes 'posts', 'pages', 'templates', 'static', 'theme_static'.
    """
    def __init__(self, full=False):
        if full or not os.path.exists(settings.DB_PATH):
            self.db = {'posts': {}, 'pages': {}, 'templates': {}, 'static': {}, 'theme_static': {}}
        else:
            self.db = json.loads(open(
                settings.DB_PATH, 'r').read().encode('utf8'))

    def load(self, source_type):
        if not source_type in self.db:
            self.db[source_type] = {}
            logger.warning('New key "{0}" created.'.format(source_type))
            return {}
        else:
            return self.db[source_type]

    def get_item(self, source_type, filename):
        return self.db[source_type][filename]

    def set_item(self, source_type, filename, item_dict):
        self.db[source_type][filename] = item_dict

    def remove_item(self, source_type, filename):
        if filename in self.db[source_tyep]:
            del self.db[source_type][filename]
        else:
            logger.warning("Failed to remove from database: {0}, TYPE: {1}".format(filename, source_type))

    def save(self):
        open(settings.DB_PATH, 'w+').write(json.dumps(self.db).encode('utf8'))
