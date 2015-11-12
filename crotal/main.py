#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Crotal - A static site generator
-----------------------------------

usage::

    crotal --help

"""
from __future__ import unicode_literals, print_function

import sys
import argparse

from crotal.command import Command
from crotal.version import __version__


DEFAULT_PORT = 1124

commands = {
    'generate': Command.generate,
    'init': Command.init_site,
    'server': Command.start_server,
    'new_post': Command.create_post,
    'new_page': Command.create_page,
    'deploy': Command.deploy,
}

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""A tool to generate static blogs,
        with markdown files.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', '--version', action='version', version=__version__,
                        help='Print the Crotal version and exit.')

    subparsers = parser.add_subparsers(help='help')

    parser_init = subparsers.add_parser('init', help='Create & initiate a new site.')
    parser_init.add_argument('site_name', help='Name of the site you want to create.', type=str)

    parser_generate = subparsers.add_parser('generate', help='Generate the site, default in incremental mode.')
    parser_generate.add_argument('-f', '--full', action='store_true', help='Generate the full site, which takes a little longer.')
    parser_generate.add_argument('-o', '--output', help='Indicate the directory where you want to place the site generated.', type=str)

    parser_server = subparsers.add_parser('server', help='Start the Crotal server.')
    parser_server.add_argument('-p', '--port', help='Indicate another port you want to preview the site on.', default=DEFAULT_PORT, type=int)

    parser_new_post = subparsers.add_parser('new_post', help='Create a new post.')
    parser_new_post.add_argument('post_title', help='Title of the post you want to create.', type=str)

    parser_new_page = subparsers.add_parser('new_page', help='Create a new page.')

    parser_deploy = subparsers.add_parser('deploy', help='Deploy the site Crotal generated.')
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_arguments()
    main_command = sys.argv[1]
    func = commands[main_command]
    func(**vars(args))

if __name__ == '__main__':
    main()
