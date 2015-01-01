#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Crotal - A static site generator
-----------------------------------

usage::

    crotal --help

"""
import os
import sys
import shutil
import argparse

from crotal import utils
from crotal import server
from crotal import deploy
from crotal import settings
from crotal import core
from crotal.version import __version__

def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="""A tool to generate static blogs,
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
    parser_server.add_argument('port', nargs='?', help='Indicate another port you want to preview the site on.', default=8000)

    parser_new_post = subparsers.add_parser('new_post', help='Create a new post.')
    parser_new_post.add_argument('"post_title"', help='Title of the post you want to create.', type=str)

    parser_new_page = subparsers.add_parser('new_page', help='Create a new page.')

    parser_deploy = subparsers.add_parser('deploy', help='Deploy the site Crotal generated.')
    return parser.parse_args(argv[1:])


def main():
    args = parse_arguments(sys.argv)
    sub_command = sys.argv[1]
    if sub_command == 'init':
        core.Command.init()
    else:
        if sub_command == 'generate':
            core.Command.generate(full=args.full)
        elif sub_command == 'server':
            server.main(settings)
        elif sub_command == 'new_page':
            core.Command.create_page()
        elif sub_command == 'new_post':
            core.Command.create_post()
        elif sub_command == 'deploy':
            utils.load_config_file()
            if settings.deploy_default == 'rsync':
                settings.PUBLISH_DIR = settings.DEPLOY_DIR
                core.Command.generate(full=True, is_preview=False)
                deploy.rsync_deploy()
            elif settings.deploy_default == 'git':
                deploy.git_deploy()
            else:
                print 'Only support rsync for now.'

if __name__ == '__main__':
    pass
