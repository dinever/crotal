import os
import sys
import yaml
import timeit
import shutil
from datetime import datetime

from crotal import utils
from crotal import logger
from crotal import settings
from crotal.utils import remove_dir
from crotal.controller import Controller
from crotal.plugins.pinyin.pinyin import PinYin

LOGO = \
"""  ____ ____   ___ _____  _    _
 / ___|  _ \\ / _ \\_   _|/ \\  | |
| |   | |_) | | | || | / _ \\ | |
| |___|  _ <| |_| || |/ ___ \\| |___
 \____|_| \_\\\\___/ |_/_/   \\_\\_____|
"""

POST_SAMPLE =\
"""---
title: "{0}"
date: {1}
categories:
slug: {2}
---

"""

PAGE_SAMPLE = \
"""---
layout: page.html
title: "{0}"
date: {1}
url: {2}
description: {3}
---

## A demo page!

This is a demo page.
"""


class Command(object):

    @staticmethod
    def generate(full=False, silent=False, is_preview=True):
        if full and os.path.exists(settings.PUBLISH_DIR):
            shutil.rmtree(settings.PUBLISH_DIR)
        utils.load_config_file()
        setattr(settings, 'THEME_DIR', os.path.join('themes', settings.theme))
        setattr(settings, 'TEMPLATES_DIR', os.path.join(settings.THEME_DIR, 'public'))
        setattr(settings, 'THEME_STATIC_DIR', os.path.join(settings.THEME_DIR, 'static'))
        start = timeit.default_timer()

        controller = Controller(full=full)
        copydir_time = timeit.default_timer()
        if not silent:
            logger.info('Static files copied.')

        controller.load(is_preview)
        if not silent:
            logger.info('Source loaded.')

        get_posts_time = timeit.default_timer()

        controller.save()
        save_other_files_time = timeit.default_timer()

        controller.save_posts()
        if not silent:
            logger.info('Posts saved.')
        controller.save_pages()
        if not silent:
            logger.info('Pages saved.')
        controller.save_categories()
        controller.save_tags()

        save_posts_time = timeit.default_timer()
        controller.save_db()
        remove_dir(settings.PUBLISH_DIR)

        if not silent:
            logger.info('%d posts generated.' % len(controller.post_collector.posts))
            logger.info('%d pages generated.' % len(controller.page_collector.pages))
            logger.info('Site generated, master %s!' % settings.author)


    @staticmethod
    def init():
        if len(sys.argv) != 3:
            site_name = 'crotal'
        else:
            site_name = sys.argv[2]
        curr = os.path.dirname(os.path.abspath(__file__))
        dir = os.path.join(curr, "init")
        utils.copy_dir(dir, site_name)
        logger.blue_text(message=LOGO)
        utils.init_git_repo(site_name)
        logger.success('Site created.')

    @staticmethod
    def create_post():
        if not os.path.exists(settings.CONFIG_PATH):
            logger.error('No "_config.yml" file found for the current directory.')
            sys.exit()
        if len(sys.argv) != 3:
            logger.error('Please specify the post title.')
        else:
            title = sys.argv[2]
            now = datetime.now()
            pub_time = now.strftime('%Y-%m-%d %H:%M')
            pinyin = PinYin()
            pinyin.load_word()
            slug = pinyin.hanzi2pinyin_split(string=title, split='-')
            new_post = POST_SAMPLE.format(title, pub_time, slug)
            file_title = now.strftime("%Y-%m-%d") + '-' + slug + '.markdown'
            file_path = os.path.join(settings.POSTS_DIR, file_title)
            open(os.path.join(settings.BASE_DIR, file_path), 'w+').write(new_post)
            logger.success(' '.join([file_path, 'created.']))

    @staticmethod
    def create_page():
        if not os.path.exists(settings.CONFIG_PATH):
            logger.error('No "_config.yml" file found for the current directory.')
            sys.exit()
        title = logger.info_input('Page Title')
        url = logger.info_input('Page URL (.e.g, /foo/bar/):')
        description = logger.info_input('Page Description:')
        pinyin = PinYin()
        slug = pinyin.hanzi2pinyin_split(string=title, split="-")
        now = datetime.now()
        pub_date = now.strftime("%Y-%m-%d %H:%M")
        page = PAGE_SAMPLE.format(title, pub_date, url, description)
        file_path = os.path.join(settings.PAGES_DIR, slug + '.markdown')
        open(os.path.join(settings.BASE_DIR, file_path), 'w+').write(page)
        logger.success('You can browse the page by {0} After generating the site.'.format(url))
