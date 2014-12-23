import os
import git

from datetime import datetime

from crotal.utils import copy_dir
from crotal import settings
from crotal import logger

def rsync_deploy():
    print 'Deploying by Rsync ...'
    print settings.DEPLOY_DIR
    os.system("rsync -avz %s %s:%s" % (settings.DEPLOY_DIR + '/', settings.ip, settings.remote_dir))

def git_deploy():
    '''
    I'm still working on this.
    '''
    
    if not hasattr(settings, 'deploy_branch'):
        return setup_github_pages()
    try:
        os.mkdir(settings.DEPLOY_DIR)
    except:
        pass
    copy_dir('_sites', '.deploy')
    deploy_branch = "master"
    os.chdir(settings.DEPLOY_DIR)
    repo = git.Repo.init(".")
    repo.git.add(".")
    message = "Site updated at %s" % datetime.strftime(
        datetime.now(),
        "%Y-%m-%d %H:%M:%S")
    print message
    print "Github Pages deploy complete"
    repo.git.commit(m=message)
    repo.git.push(force=True, origin=deploy_branch)

def setup_github_pages():
    try:
        repo = git.Repo(settings.BASE_DIR)
        repo.git.checkout("master")
        copy_dir(settings.PUBLISH_DIR, settings.BASE_DIR)
        repo.git.add(".")
        repo.git.reset("_sites") #forget `_sites' folder
        repo.git.reset("db.json") #forget `db.json' too.
        message = "Site Updated at %s" %\
                   datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S %Z")
        if not repo.remotes:
            print "Enter the read/write url for your repository"
            print "(For example, 'git@github.com:your_username/your_username.github.io.git)"
            repo_url = raw_input("Repository url: ")
            try:
                repo.create_remote("origin", repo_url)
            except git.GitCommandError, giterr:
                logger.warning(giterr)
        repo.git.commit(m=message)
        #Push `source' as well as `master'
        repo.git.push("origin", all=True)
    except Exception, ex:
        logger.warning(ex)
    else:
        logger.success("GitHub pages deployed")
    finally:
        #Go back to `source'
        repo.git.checkout("source")
