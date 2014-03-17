import os
from datetime import datetime
from crotal.copy_dir import copy_dir


def git_deploy(config):
    '''
    I'm still working on this.
    '''
    try:
        os.mkdir('.deploy')
    except:
        pass
    deploy_dir = ".deploy/"
    copy_dir('_sites', '.deploy')
    deploy_branch = "master"
    os.chdir(deploy_dir)
    if not hasattr(config, 'deploy_branch'):
        setup_github_pages()
    os.system("git add .")
    os.system("git add --all *")
    message = "Site updated at %s" % datetime.strftime(
        datetime.now(),
        "%Y-%m-%d %H:%M:%S")
    print message
    print "Github Pages deploy complete"
    os.system("git commit -m '%s'" % message)
    os.system("git push origin %s --force" % deploy_branch)


def setup_github_pages():
    deploy_branch = "master"
    os.system("git init")
    print "Enter the read/write url for your repository"
    print "(For example, 'git@github.com:your_username/your_username.github.io)"
    repo_url = raw_input("Repository url: ")
    os.system("git remote add origin %s" % repo_url)
