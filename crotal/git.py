import os
from datetime import datetime
from unipath import Path

dir = Path(__file__).ancestor(2).absolute()

def rsyncDeploy():
    deploy_dir = dir + "/_sites/"
    deploy_branch = "master"
    os.chdir(deploy_dir)
    os.system("ls")
    os.system("git init")
    os.system("git add .")
    os.system("git add --all *")
    message = "Site updated at %s" % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    print message
    print "Github Pages deploy complete"
    os.system("git remote add origin https://github.com/dinever/dinever.github.io.git")
    os.system("git commit -m '%s'" % message)
    os.system("git push origin %s --force" % deploy_branch )

def setupGithubPages():
    print "Enter the read/write url for your repository"
    print "(For example, 'git@github.com:your_username/your_username.github.io)"
    repo_url = raw_inpout("Repository url: ")

if __name__ == '__main__':
    rsyncDeploy()

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
