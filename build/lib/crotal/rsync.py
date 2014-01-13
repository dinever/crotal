import os

def rsync_deploy(dir, config):
    print 'Deploying by Rsync ...'
    os.system("rsync -avz %s %s:%s" % (dir, config.ip, config.deploy_dir))

if __name__ == '__main__':
    rsync_deploy(dir)
