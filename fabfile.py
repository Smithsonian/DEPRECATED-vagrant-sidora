from fabric.api import *
import fabtools
from fabtools.vagrant import vagrant

@task
def deploy():
    # Require SIdora from github
    #fabtools.require.git.working_copy("https://github.com/Smithsonian/sidora.git")
    fabtools.require.git.working_copy("https://github.com/Smithsonian/sidora-deploy")
    #run("git clone https://github.com/Smithsonian/sidora.git")

@task
def setup():
    # Require git
    fabtools.rpm.install('git')
