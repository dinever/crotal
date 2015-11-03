import os

from crotal.site import Site


class Deployer(object):

    def __init__(self, config):
        self.config = config
        self.deploy_method = config.deploy_default

    def deploy(self):
        if (self.deploy_method == "git"):
            self.git_deploy()
        if (self.deploy_method == "rsync"):
            self.rsync()

    def git_deploy(self):
        git_remote = self.config.git_repository
        deploy_dir = os.path.join(self.config.base_dir, '.deploy')
        if not os.path.exists(deploy_dir):
            os.mkdir(deploy_dir)
            os.system("git clone {0} {1}".format(git_remote, deploy_dir))
        os.chdir(os.path.join(self.config.base_dir, '.deploy'))
        os.system("git pull")
        site = Site(full=True, output=deploy_dir)
        site.generate()
        os.system("git add --all *")
        os.system("git commit -m {0}".format("\"Crotal commit.\""))
        os.system("git push origin master")

    def rsync(self):
        os.system("rsync -avz {0}\/* {1}:{2}".format(self.config.publish_dir,
                                                  self.config.ip,
                                                  self.config.remote_dir))
