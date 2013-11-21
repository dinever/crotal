import os
import sys
from unipath import Path

import settings
from turtpress.models.posts import Posts
from turtpress.views import Views
from turtpress.copydir import copyDir

posts = []
categories = []
dir = Path(__file__).ancestor(1).absolute()

def make_site():
    posts_titles = os.listdir(dir.child('_posts'))
    templates = os.listdir(dir)
    categories_tmp = []
    for post_title in posts_titles:
        post_tmp = Posts()
        post_tmp.save(open(dir + '/_posts/' + post_title, 'r').read().decode('utf8'))
        posts.append(post_tmp)
        for category in post_tmp.categories:
            categories_tmp.append(category)

    categories = sorted({}.fromkeys(categories_tmp).keys())
    posts_sort()
    view = Views()
    view.save(posts, categories)
    view.save_posts(posts)
    view.save_get_more(posts)

def posts_sort():
    for i in range(len(posts)):
        for j in range(len(posts)):
            if  posts[i].pub_time > posts[j].pub_time:
                posts[i], posts[j] = posts[j], posts[i]

def usage():
    print 'Usage:'
    print 'to generate the site:    python main.py make'
    print 'to create a new post:    python main.py new_post "your title here"'
    print 'to create a new page:    python main.py new_page'
    print 'to start the server:     python main.py server'
    print 'to deploy the site:      python main.py deploy'
    print '                         python main.py server 8080'

if __name__ == '__main__':
    flag = 0
    if len(sys.argv) == 1:
        usage()
    elif len(sys.argv) != 1:
        if sys.argv[1] == 'make':
            import shutil
            shutil.rmtree(dir + '/' + '_sites/')
            copyDir('_static','_sites')
            print 'Static Files Copied.'
            make_site()
            print 'Site Generated.'
        elif sys.argv[1] == 'server':
            del sys.argv[1]
            from turtpress import server
            server.main()
        elif sys.argv[1] == 'new_page':
            del sys.argv[1]
            from turtpress import create_pages
            create_pages.create_page()
        elif sys.argv[1] == 'new_post':
            del sys.argv[1]
            from turtpress import create_post
            create_post.create_post()
        elif sys.argv[1] == 'deploy':
            if settings.deploy_default == 'rsync':
                from turtpress import rsync
                rsync.rsyncDeploy(str(dir) + '/_sites/')
            elif settings.deploy_default == 'git':
                from turtpress import git
                git.rsyncDeploy()
            else:
                print 'Only support rsync for now.'
        else:
            usage()
    else:
        usage()
