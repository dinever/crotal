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
    os.system("git commit -m '%s'" % message)
    os.system("git push origin %s" % deploy_branch --force)
    print "Github Pages deploy complete"

def setupGithubPages():
    print "Enter the read/write url for your repository"
    print "(For example, 'git@github.com:your_username/your_username.github.io)"
    repo_url = raw_inpout("Repository url: ")

if __name__ == '__main__':
    rsyncDeploy(dir)

#  if args.repo
#    repo_url = args.repo
#  else
#    puts "Enter the read/write url for your repository"
#    puts "(For example, 'git@github.com:your_username/your_username.github.io)"
#    repo_url = get_stdin("Repository url: ")
#  end
#  user = repo_url.match(/:([^\/]+)/)[1]
#  branch = (repo_url.match(/\/[\w-]+\.github\.(?:io|com)/).nil?) ? 'gh-pages' : 'master'
#  project = (branch == 'gh-pages') ? repo_url.match(/\/([^\.]+)/)[1] : ''
#  unless (`git remote -v` =~ /origin.+?octopress(?:\.git)?/).nil?
#    # If octopress is still the origin remote (from cloning) rename it to octopress
#    system "git remote rename origin octopress"
#    if branch == 'master'
#      # If this is a user/organization pages repository, add the correct origin remote
#      # and checkout the source branch for committing changes to the blog source.
#      system "git remote add origin #{repo_url}"
#      puts "Added remote #{repo_url} as origin"
#      system "git config branch.master.remote origin"
#      puts "Set origin as default remote"
#      system "git branch -m master source"
#      puts "Master branch renamed to 'source' for committing your blog source files"
#    else
#      unless !public_dir.match("#{project}").nil?
#        system "rake set_root_dir[#{project}]"
#      end
#    end
#  end
#
