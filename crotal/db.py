import json
from crotal.reporter import Reporter

reporter = Reporter()

class Database:
    def __init__(self, full=False):
        if full is True:
            self.init_new_database()
        else:
            try:
                self.get_database_content()
            except Exception as e:
                self.init_new_database()

    def get_database_content(self):
        self.db = json.loads(open(
                'db.json', 'r').read().encode('utf8'))

    def init_new_database(self):
        self.db = {'posts': {}, 'pages': {}, 'templates': {}}

    def load(self, source_type):
        if not self.db.has_key(source_type):
            self.db[source_type] = {}
            reporter.db_create_new_key(source_type)
            return {}
        else:
            return self.db[source_type]

    def get_item_content(self, source_type, filename):
        return self.db[source_type][filename]['content']

    def set_item(self, source_type, filename, item_dict):
        try:
            self.db[source_type][filename] = item_dict
        except Exception, e:
            self.db[source_type] = {}
            self.db[source_type][filename] = item_dict

    def remove_item(self, source_type, filename):
        del self.db[source_type][filename]

    def save(self):
        db_to_save = json.dumps(self.db)
        open('db.json', 'w+').write(db_to_save.encode('utf8'))

