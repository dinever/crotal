import os
from threading import Thread

class Collector(Thread):

    def process_directory(self, directory):
        print directory
        '''
        This method returns the list of all the source files in the directory
        indicated. Notice that filename started with '-' or '.' will not be
        included.
        '''
        filenames = []
        for dir_, _, files in os.walk(directory):
            for filename in files:
                relative_dir = os.path.relpath(dir_, directory)
                relative_file = os.path.join(relative_dir, filename)
                absolute_file = os.path.join(dir_, filename)
                if relative_file.startswith('_') is False and \
                        filename.startswith('.') is False:
                    filepath = os.path.join(directory, relative_file)
                    filenames.append(filepath)
        return filenames

    def detect_new_filenames(self, source_type):
        '''
        This method distinguishs new, old and removed files.
        new_filenames: The filenames user just added or updated.
        old_filenames: The filenames which haven't been changed.
        removed_filenames: The filenames which is removed.(Existed in db.json,
            but not in source folder.)
        '''
        filenames = getattr(self, source_type+'_files')
        db_filenames = self.database.load(source_type)
        new_filenames = list(set(filenames) - set(db_filenames))
        old_filenames = list(
            set(db_filenames) - (set(db_filenames) - set(filenames)))
        removed_filenames = list(set(db_filenames) - set(filenames))
        for filename in old_filenames:
            last_mod_time = os.path.getmtime(filename)
            last_mod_time_in_db = self.database.db[
                source_type][filename]['last_mod_time']
            if last_mod_time != last_mod_time_in_db:
                new_filenames.append(filename)
                old_filenames.remove(filename)
        return new_filenames, old_filenames, removed_filenames
