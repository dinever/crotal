#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from crotal.views import Views

author = 'dinever'

SAMPLE = """{%% extends "_layout/base.html" %%}
{%% block title %%}
%s
{%% endblock %%}
{%% block description %%}
%s
{%% endblock %%}
{%% block content %%}
<h2 class="page-title">%s</h2>
<article class="post">

{%% markdown %%}

Please write down you content right here.

To edit this page, check `/public/%s/index.html`.

Remember to add a link to this page in `/public/_layout/base.html`.(For example, in the navigation bar)

{%% endmarkdown %%}

{%% endblock %%}

"""

def create_page(config):
    flag = 0
    if len(sys.argv) == 1:
        title = raw_input('Page Title:')
        slug = raw_input('Page Slug(For URL):')
        description = raw_input('Page Description(For SEO):')
        try:
            os.makedirs('public/'+slug)
        except:
            pass
        open('public/'+ slug +'/index.html', 'w+').write(SAMPLE % (title, description, title, slug))
        print 'You can check browse the page by ' + config.url + '/' + slug + '/' + ' After generating the site.'

    elif len(sys.argv) != 1:
        open('_posts/' + file_title, 'w+').write(new_post)
    else:
        usraccount = sys.argv[1]
        passwd = sys.argv[2]

if __name__ == '__main__':
    create_page()
