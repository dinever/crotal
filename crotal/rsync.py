import os


def rsync_deploy(dir, config):

    if config.ip and config.ip is not None:
        print 'Deploying by Rsync to %s:%s ...' % (config.ip, config.deploy_dir)
        os.system("rsync -avz %s %s:%s" % (dir, config.ip, config.deploy_dir))
    else:
        print 'Deploying by Rsync to %s ...' % config.deploy_dir
        os.system("rsync -avz %s %s" % (dir, config.deploy_dir))

if __name__ == '__main__':
    rsync_deploy(dir)
