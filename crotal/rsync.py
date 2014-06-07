import os

from crotal.config import config


def rsync_deploy():
    print 'Deploying by Rsync ...'
    print config.deploy_dir
    os.system("rsync -avz %s %s:%s" % (config.publish_dir, config.ip, config.deploy_dir))
