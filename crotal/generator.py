import timeit

from crotal.controller import Controller
from crotal import reporter
from crotal.remove_dir import remove_dir
from crotal.config import config

class Generator:

    def generate_site(self, full=False, silent=False, is_preview=True):
        start = timeit.default_timer()

        controller = Controller(full=full)
        copydir_time = timeit.default_timer()
        if not silent:
            reporter.info_report('Static files copied.')

        controller.load(is_preview)
        if not silent:
            reporter.info_report('Source loaded.')

        get_posts_time = timeit.default_timer()

        controller.save()
        save_other_files_time = timeit.default_timer()

        controller.save_posts()
        if not silent:
            reporter.info_report('Posts saved.')
        controller.save_pages()
        if not silent:
            reporter.info_report('Pages saved.')

        save_posts_time = timeit.default_timer()
        controller.save_db()
        remove_dir(config.publish_dir)

        if not silent:
            reporter.info_report('%d posts generated.' % len(controller.post_collector.posts))
            reporter.info_report('%d pages generated.' % len(controller.page_collector.pages))
            reporter.info_report('Site generated, master %s!' % config.author)

