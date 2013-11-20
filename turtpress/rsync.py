import os
import settings

def rsyncDeploy(dir):
    os.system("rsync -avz %s %s:%s" % (dir, settings.ip, settings.deployDir))

if __name__ == '__main__':
    rsyncDeploy(dir)
