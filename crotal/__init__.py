# -*- coding:utf-8 -*-
"""Crotal - A static site generator
-----------------------------------

usage::

    crotal --help

"""
import os
import sys
import timeit
import argparse

from . import config
from crotal.config import Config
from crotal.reporter import Reporter
from crotal.generator import Generator

__version__ = "0.7.0"

dir = os.getcwd()

reporter = Reporter()
generator = Generator()

def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="""A tool to generate a static blog,
        with markdown files.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', '--version', action='version', version=__version__,
                        help='Print the pelican version and exit.')


    subparsers = parser.add_subparsers(help='help')

    parser_init = subparsers.add_parser('init', help='Create & initiate a new site.')
    parser_init.add_argument('site_name', help='Name of the site you want to create.', type=str)

    parser_generate = subparsers.add_parser('generate', help='Generate the site, default in incremental mode.')
    parser_generate.add_argument('-f', '--full', action='store_true', help='Generate the full site, which takes a little longer.')
    parser_generate.add_argument('-o', '--output', help='Indicate the directory where you want to place the site generated.', type=str)

    parser_server = subparsers.add_parser('server', help='Start the Crotal server.')
    parser_server.add_argument('-p', '--port', help='Indicate another port you want to preview the site on.', type=int)

    parser_new_post = subparsers.add_parser('new_post', help='Create a new post.')
    parser_new_post.add_argument('"post_title"', help='Title of the post you want to create.', type=str)

    parser_new_page = subparsers.add_parser('new_page', help='Create a new page.')

    parser_deploy = subparsers.add_parser('deploy', help='Deploy the site Crotal generated.')
    return parser.parse_args(argv[1:])


def main():
    args = parse_arguments(sys.argv)
    sub_command = sys.argv[1]
    if sub_command == 'init':
        site_name = sys.argv[2]
        from crotal.init_site import init_site
        init_site(site_name)
    else:
        try:
            config = Config(dir)
        except Exception as e:
            reporter.no_site_dected()
        if sub_command == 'generate':
            if args.full is True:
                generator.generate_site(config, full=True)
            else:
                generator.generate_site(config)
        elif sub_command == 'server':
            from crotal import server
            server.main()
        elif sub_command == 'new_page':
            from crotal import create_pages
            create_pages.create_page(config)
        elif sub_command == 'new_post':
            from crotal import create_post
            create_post.create_post(config)
        elif sub_command == 'deploy':
            if config.deploy_default == 'rsync':
                from crotal import rsync
                rsync.rsync_deploy(str(dir) + '/_sites/', config)
            elif config.deploy_default == 'git':
                from crotal import git
                git.git_deploy(config)
            else:
                print 'Only support rsync for now.'

if __name__ == '__main__':
    pass
