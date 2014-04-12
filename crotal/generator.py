import os
import timeit
import shutil

from crotal.controller import Controller
from crotal.reporter import *
from crotal.remove_dir import remove_dir

reporter = Reporter()

dir = os.getcwd()

class Generator:

    def generate_site(self, config, full=False):
        start = timeit.default_timer()

        controller = Controller(config, dir, full=full)
        controller.copy_static_files()
        copydir_time = timeit.default_timer()
        # print '{0:20} in {1:3.3f} seconds'.format('Static Files Copied', copydir_time - start)
        reporter.info_report('Static files copied.')
        try:
            os.mkdir('.private/')
        except Exception as e:
            pass

        #self.copy_template_files(config.theme)
        #controller.get_posts()
        #controller.get_pages()
        #controller.get_templates()
        controller.get()
        reporter.info_report('Source loaded.')

        get_posts_time = timeit.default_timer()
        # print '{0:20} in {1:3.3f} seconds'.format('Posts & Pages got', get_posts_time - copydir_time)

        controller.save()
        save_other_files_time = timeit.default_timer()
        # print '{0:20} in {1:3.3f} seconds'.format('Other files saved', save_other_files_time - get_posts_time)

        controller.remove_items()
        controller.save_posts()
        reporter.info_report('Posts saved.')
        controller.save_pages()
        reporter.info_report('Pages saved.')

        save_posts_time = timeit.default_timer()
        # print '{0:20} in {1:3.3f} seconds'.format('Posts saved', save_posts_time - save_other_files_time)
        controller.save_db()
        remove_dir(os.path.join(dir, '_sites'))

        # print '{0:20} in {1:3.3f} seconds'.format('Site Generated', save_posts_time - start)
        reporter.info_report('%d posts generated.' % len(controller.post_collector.posts))
        reporter.info_report('%d pages generated.' % len(controller.page_collector.pages))
        reporter.info_report('Site generated, master %s!' % config.author)

        # print str(len(controller.posts)) + ' posts published.'

        try:
            shutil.rmtree(os.path.join(dir, '.private'))
        except Exception as e:
            pass
