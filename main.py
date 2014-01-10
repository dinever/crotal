import os, sys, timeit
from unipath import Path

import config
from crotal.views import Views
from crotal.copydir import copy_dir
from crotal.config import Config

dir = Path(__file__).ancestor(1).absolute()
config = Config(dir)

def remove_site():
    '''
    Remove site.
    '''
    import shutil
    try:
        shutil.rmtree(dir + '/_sites/')
    except:
        pass

def generate_site():

    #Read config file
    print config.theme

    remove_site()
    start = timeit.default_timer()
    copy_dir('themes/' + config.theme + '/static','_sites')
    copydir_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Static Files Copied', copydir_time - start)

    view = Views(config)
    view.get_directory(dir)
    view.get_posts()
    get_posts_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Posts got', get_posts_time - copydir_time)

    view.save(view.posts, view.categories)
    save_other_files_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Other files saved', save_other_files_time - get_posts_time)

    view.save_posts(view.posts)
    save_posts_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Posts saved', save_posts_time - save_other_files_time)

    print '-------------------------------------'
    print '{0:20} in {1:3.3f} seconds'.format('Site Generated', save_posts_time - start)

def usage():
    print 'Usage:'
    print 'to generate the site:    python main.py generate'
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
        if sys.argv[1] == 'generate':
            generate_site()
        elif sys.argv[1] == 'server':
            del sys.argv[1]
            from crotal import server
            server.dir = dir
            server.main()
        elif sys.argv[1] == 'new_page':
            del sys.argv[1]
            from crotal import create_pages
            create_pages.create_page(config)
        elif sys.argv[1] == 'new_post':
            del sys.argv[1]
            from crotal import create_post
            create_post.create_post()
        elif sys.argv[1] == 'deploy':
            if config.deploy_default == 'rsync':
                from crotal import rsync
                rsync.rsync_deploy(str(dir) + '/_sites/', config)
            elif config.deploy_default == 'git':
                from crotal import git
                git.rsync_deploy()
            else:
                print 'Only support rsync for now.'
        elif sys.argv[1] == 'init':
            ##TODO
            pass
        else:
            usage()
    else:
        usage()
