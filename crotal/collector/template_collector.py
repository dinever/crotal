import os

from crotal.collector import Collector
from crotal import settings


class TemplateCollector(Collector):
    def __init__(self, database):
        Collector.__init__(self)
        self.database = database
        self.templates = {}
        self.removed_templates = []
        self.templates_files = []
        self.new_templates = {}
        self.other_template_files = []
        self.templates_files = []
        self.process_directory(settings.TEMPLATES_DIR)

    def process_directory(self, directory):
        for dir_, _, files in os.walk(directory):
            for filename in files:
                relDir = os.path.relpath(dir_, directory)
                relFile = os.path.join(relDir, filename)
                absoluteFile = os.path.join(dir_, filename)
                if filename.startswith('.') is False:
                    if relFile.startswith('_') is False:
                        pass
                    else:
                        self.other_template_files.append(absoluteFile)
                    self.templates_files.append(absoluteFile)

    def run(self):
        new_filenames, old_filenames, removed_filenames = self.detect_new_filename_list('templates')
        new_other_template_filenames = list(set(self.other_template_files) - set(old_filenames))
        if new_other_template_filenames != []:
            new_filenames = list(set(self.templates_files) - set(self.other_template_files))
            old_filenames = []
        else:
            new_filenames = list(set(new_filenames) - set(self.other_template_files))
            old_filenames = list(set(old_filenames) - set(self.other_template_files))
        self.parse_old_templates(old_filenames)
        self.parse_new_templates(new_filenames)
        self.parse_removed_templates(removed_filenames)
        self.set_db()

    def set_db(self):
        for filename in self.templates_files:
            last_mod_time = os.path.getmtime(
                filename)
            template_layout_content = open(
                filename,
                'r').read().decode('utf8')
            template_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': template_layout_content}
            self.database.set_item('templates', filename, template_dict_in_db)

    def parse_old_templates(self, filenames):
        for filename in filenames:
            self.templates[filename] = self.database.get_item('templates', filename)['content']

    def parse_new_templates(self, filenames):
        for filename in filenames:
            last_mod_time = os.path.getmtime(
                filename)
            template_layout_content = open(
                filename,
                'r').read().decode('utf8')
            last_mod_time = os.path.getmtime(filename)
            self.templates[filename] = template_layout_content
            self.new_templates[filename] = template_layout_content

    def parse_removed_templates(self, filenames):
        for filename in filenames:
            self.database.remove_item('templates', filename)
