import os
import sys
import timeit
import shutil

from . import config
from crotal.views import Views
from crotal.copy_dir import copy_dir
from crotal.config import Config

dir = os.getcwd()


def generate_site(config, full):
    try:
        shutil.rmtree(os.path.join(dir, '_sites'))
    except Exception as e:
        pass
    start = timeit.default_timer()
    copy_dir(os.path.join('themes', config.theme, 'static'), '_sites')
    copy_dir('static', '_sites')
    copydir_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Static Files Copied', copydir_time - start)

    try:
        os.mkdir('.private/')
    except Exception as e:
        pass
    copy_dir(os.path.join('themes', config.theme, 'public'), '.private')
    copy_dir('public/', '.private')

    view = Views(config, dir, full)
    view.get_posts()
    view.get_pages()
    view.save_db()
    get_posts_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Posts & Pages got', get_posts_time - copydir_time)

    view.save(view.posts, view.categories)
    save_other_files_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Other files saved', save_other_files_time - get_posts_time)

    view.save_posts(view.posts)
    view.save_pages(view.pages)
    save_posts_time = timeit.default_timer()
    print '{0:20} in {1:3.3f} seconds'.format('Posts saved', save_posts_time - save_other_files_time)

    print '-------------------------------------'
    print '{0:20} in {1:3.3f} seconds'.format('Site Generated', save_posts_time - start)
    print str(len(view.posts)) + ' posts published.'

    try:
        shutil.rmtree(os.path.join(dir, '.private'))
    except Exception as e:
        pass


def deploy(config):
    if config.deploy_default == 'rsync':
        from crotal import rsync
        rsync.rsync_deploy(str(dir) + '/_sites/', config)
    elif config.deploy_default == 'git':
        from crotal import git
        git.git_deploy(config)
    elif config.deploy_default == 'scp':
        from crotal import scp
        scp.scp_deploy(str(dir) + '/_sites/', config)
    else:
        print 'Only support rsync, git and scp for now.'


def usage():
    print 'Usage:'
    print 'to init a new site:      crotal init you_site_name'
    print 'to generate the site:    crotal generate'
    print 'to create a new post:    crotal new_post "your title here"'
    print 'to create a new page:    crotal new_page'
    print 'to start the server:     crotal server'
    print 'to deploy the site:      crotal deploy'


def main():
    flag = False  # flag indicates whether the _config.yml file is loaded.
    try:
        config = Config(dir)
        flag = True
    except Exception as e:
        pass

    if flag:
        if len(sys.argv) == 1:
            usage()
        elif len(sys.argv) != 1:
            if sys.argv[1] == 'generate':
                if len(sys.argv) == 3:
                    if sys.argv[2] == '-f' or sys.argv[2] == '--full':
                        generate_site(config, True)
                else:
                    generate_site(config, False)
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
                create_post.create_post(config)
            elif sys.argv[1] == 'deploy':
                deploy(config)
            else:
                usage()
        else:
            usage()
    else:
        if len(sys.argv) == 1:
            usage()
        else:
            if sys.argv[1] == 'init':
                site_name = sys.argv[2]
                from crotal.init_site import init_site
                init_site(site_name)
            else:
                usage()

if __name__ == '__main__':
    pass
