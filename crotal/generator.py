import os
import timeit
import shutil

from crotal.controller import Controller
from crotal import reporter
from crotal.remove_dir import remove_dir
from crotal.config import config

class Generator:

    def generate_site(self, full=False, silent=False, is_preview=True):
        start = timeit.default_timer()

        controller = Controller(full=full)
        copydir_time = timeit.default_timer()
        print '{0:20} in {1:3.3f} seconds'.format('Static Files Copied', copydir_time - start)
        if not silent:
            reporter.info_report('Static files copied.')

        controller.get(is_preview)
        if not silent:
            reporter.info_report('Source loaded.')

        get_posts_time = timeit.default_timer()
        print '{0:20} in {1:3.3f} seconds'.format('Posts & Pages got', get_posts_time - copydir_time)

        controller.save()
        save_other_files_time = timeit.default_timer()
        print '{0:20} in {1:3.3f} seconds'.format('Other files saved', save_other_files_time - get_posts_time)

        controller.save_posts()
        if not silent:
            reporter.info_report('Posts saved.')
        controller.save_pages()
        if not silent:
            reporter.info_report('Pages saved.')

        save_posts_time = timeit.default_timer()
        print '{0:20} in {1:3.3f} seconds'.format('Posts saved', save_posts_time - save_other_files_time)
        controller.save_db()
        remove_dir(config.publish_dir)

        print '{0:20} in {1:3.3f} seconds'.format('Site Generated', save_posts_time - start)
        if not silent:
            reporter.info_report('%d posts generated.' % len(controller.post_collector.posts))
            reporter.info_report('%d pages generated.' % len(controller.page_collector.pages))
            reporter.info_report('Site generated, master %s!' % config.author)

        # print str(len(controller.posts)) + ' posts published.'
