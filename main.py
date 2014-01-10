import os, sys, timeit
from unipath import Path

import settings
from turtpress.views import Views
from turtpress.copydir import copy_dir

dir = Path(__file__).ancestor(1).absolute()

def remove_site():
    '''
    Remove site.
    '''
    import shutil
    try:
        shutil.rmtree(dir + '/' + '_sites/')
    except:
        pass

def generate_site():
    remove_site()
    start = timeit.default_timer()
    copy_dir('themes/' + settings.theme + '/static','_sites')
    copydir_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Static Files Copied', copydir_time - start)

    view = Views()
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
            from turtpress import server
            server.dir = dir
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
