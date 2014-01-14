from fabric.api import *
from fabric.contrib import files
from fabric.api import settings
import fabtools
from fabtools.vagrant import vagrant
from fabtools import require


@task
def install():
#     _prepare_rpm()
#     _install_devtools()
#     _install_utilities()
#     _install_java
#     _prepare_fedora
    _install_mysql()

def _perepare_rpm():
    # prepare rpm installations
    fabtools.rpm.update()
    require.rpm.package('redhat-lsb-core-4.0-7.el6.centos.x86_64')

def _install_devtools():    
    # development tools
    require.rpm.repository('rpmforge')    
    fabtools.rpm.groupinstall('Development Tools', options='--skip-broken')

def _install_utilities():    
    # install utilities
    utilities = ['puppet', 'wget', 'mlocate']
    require.rpm.packages(utilities)

def _install_java():    
    # Java
    #run('wget http://download.oracle.com/otn-pub/java/jdk/7u2-b13/jdk-7u2-linux-x64.rpm')
    #sudo('sudo yum install jdk-7u2-linux-x64.rpm')
    require.oracle_jdk.installed(version='7u25-b15')
#    require.oracle_jdk.installed(version='7u2')
    sudo('alternatives --install /usr/bin/java java /usr/java/latest/jre/bin/java 20000')
    sudo('alternatives --install /usr/bin/javaws javaws /usr/java/latest/jre/bin/javaws 20000')
#    sudo('alternatives --install /usr/lib/mozilla/plugins/libjavaplugin.so libjavaplugin.so /usr/java/latest/jre/lib/i386/libnpjp2.so 20000')
#    sudo('alternatives --install /usr/lib64/mozilla/plugins/libjavaplugin.so libjavaplugin.so.x86_64 /usr/java/latest/jre/lib/amd64/libnpjp2.so 20000')

def _prepare_fedora():     
     # prepare Fedora
    if not fabtools.user.exists('fedora'):
        fabtools.user.create('fedora')
        bash = ['export FEDORA_HOME=/usr/local/fedora','export CATALINA_HOME=/usr/local/fedora/tomcat','export JAVA_OPTS="-Xms1024m -Xmx1024m -XX:MaxPermSize=256m']
        with cd('/home/fedora'):
            files.append('.bash_profile', bash, use_sudo=True)

    with cd('/home/fedora'):
        fedora_url = 'http://downloads.sourceforge.net/project/fedora-commons/fedora/3.4.2/fcrepo-installer-3.4.2.jar'
        run("wget '{}'".format(fedora_url))
        
def _install_mysql():
    '''
    Installs mysql and creates databases with credentials
    '''
    
    #require.mysql.server(password='qwerty')
    require.rpm.packages(['mysql', 'mysql-server'])
    sudo('chkconfig mysqld on')
    fabtools.service.start('mysqld')
#     mysql_passwd = 'qwerty'
#     sudo('/usr/bin/mysqladmin -u root password %s' % (mysql_passwd))
    
    with settings(mysql_user='root',mysql_password='qwerty'):
        #if not fabtools.mysql.user_exists('root'):
        #    fabtools.mysql.create_user('root', password=mysql_passwd)

        # Drupal databases
        if not fabtools.mysql.database_exists('drupal6_default'):
            fabtools.mysql.create_database('drupal6_default')
        if not fabtools.mysql.database_exists('drupal6_exhibition'):
            fabtools.mysql.create_database('drupal6_exhibition')
        if not fabtools.mysql.database_exists('drupal6_fieldbooks'):
            fabtools.mysql.create_database('drupal6_fieldbooks')
        
        # Fedora databases
        if not fabtools.mysql.database_exists('fedora3'):
            fabtools.mysql.create_database('fedora3')
    
    drupaldbuser = 'drupaldbuser'
    drupaldbpass = 'Password123'    
    sql = 'echo "GRANT ALL ON {0}.* TO \'{1}\'@localhost IDENTIFIED BY \'{2}\';" | mysql -u root -p qwerty'
    sudo(sql.format('drupal6_default', drupaldbuser, drupaldbpass))
    sudo(sql.format('drupal6_exhibition', drupaldbuser, drupaldbpass))
    sudo(sql.format('drupal6_fieldbooks', drupaldbuser, drupaldbpass))

    fedoradbuser = 'fedora'
    fedoradbpass = 'Password123'
    sudo(sql.format('fedora3', fedoradbuser, fedoradbpass))







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
    
    
    
    
    
##########################    
# Fedora server management
@task
def fc(cmd):
    sudo('/etc/init.d/fcrepo-server %s' % cmd)
    
    
    
    
# Shell provisioning
#   # somehow need to incorporate this: http://cbednarski.com/articles/creating-vagrant-base-box-for-centos-62/
# #  config.vm.provision :shell, :inline => "sudo cp /vagrant/conf/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth0"
#   #config.vm.provision :unix_reboot
#   config.vm.provision :shell, :inline => "sudo yum -y update"
#   config.vm.provision :shell, :inline => "sudo yum -y upgrade"
# #  config.vm.provision :shell, :inline => "sudo rpm -Uvh http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.3-1.el5.rf.x86_64.rpm "
#   config.vm.provision :shell, :inline => "sudo rpm -Uvh http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm "
#   config.vm.provision :shell, :inline => "sudo yum -y --skip-broken groupinstall 'Development Tools'"
#   config.vm.provision :shell, :inline => "sudo yum -y install puppet wget mlocate"
# 
#   # Fedora
# 
#   config.vm.provision :shell, :inline => "sudo yum -y install mysql mysql-server"
#   config.vm.provision :shell, :inline => "sudo chkconfig mysqld on"
#   config.vm.provision :shell, :inline => "sudo service mysqld start"
# #/usr/bin/mysqladmin -u root password 'new-password'
# #/usr/bin/mysqladmin -u root -h localhost.localdomain password 'new-password'