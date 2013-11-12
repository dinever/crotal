#    system "git add ."
#    system "git add -u"
#    puts "\n## Commiting: Site updated at #{Time.now.utc}"
#    message = "Site updated at #{Time.now.utc}"
#    system "git commit -m \"#{message}\""
#    puts "\n## Pushing generated #{deploy_dir} website"
#    system "git push origin #{deploy_branch} --force"
#    puts "\n## Github Pages deploy complete"

import os
import settings
from datetime import datetime

def rsyncDeploy(dir):
    os.system("git add .")
    os.system("git add -u")
    message = "Site updated at %s" % datetime.strptime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    os.system("git commit -m %s" % message)
    os.system("git push origin %s" % deploy_branch --force)
    print "Github Pages deploy complete"

if __name__ == '__main__':
    rsyncDeploy(dir)
