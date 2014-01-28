import textwrap
from fabric.api import *
from fabric.contrib import files
from fabric.api import settings
import fabtools
from fabtools.vagrant import vagrant
from fabtools import require
import fabtools.mysql

@task
def test():
    pass

@task
def install():
    _rpm_setup()
    _devtools_install()
    _utilities_install()
    _java_install()
    _fedora_prep()
    _mysql_install()
    _php_install()
    _apache_install()
    _drupal_install()

def _rpm_setup():
    # prepare rpm installations
    fabtools.rpm.update()
    require.rpm.package('redhat-lsb-core-4.0-7.el6.centos.x86_64')

def _devtools_install():    
    # development tools
    require.rpm.repository('rpmforge')    
    fabtools.rpm.groupinstall('Development Tools', options='--skip-broken')

def _utilities_install():    
    # install utilities
    utilities = ['puppet', 'wget', 'mlocate']
    require.rpm.packages(utilities)

def _java_install():    
    # Java
    #run('wget http://download.oracle.com/otn-pub/java/jdk/7u2-b13/jdk-7u2-linux-x64.rpm')
    #sudo('sudo yum install jdk-7u2-linux-x64.rpm')
    require.oracle_jdk.installed(version='7u25-b15')
#    require.oracle_jdk.installed(version='7u2')
    sudo('alternatives --install /usr/bin/java java /usr/java/latest/jre/bin/java 20000')
    sudo('alternatives --install /usr/bin/javaws javaws /usr/java/latest/jre/bin/javaws 20000')
#    sudo('alternatives --install /usr/lib/mozilla/plugins/libjavaplugin.so libjavaplugin.so /usr/java/latest/jre/lib/i386/libnpjp2.so 20000')
#    sudo('alternatives --install /usr/lib64/mozilla/plugins/libjavaplugin.so libjavaplugin.so.x86_64 /usr/java/latest/jre/lib/amd64/libnpjp2.so 20000')

def _fedora_prep():     
     # prepare Fedora
    if not fabtools.user.exists('fedora'):
        fabtools.user.create('fedora')
        bash = ['export FEDORA_HOME=/usr/local/fedora',
                'export CATALINA_HOME=/usr/local/fedora/tomcat',
#                 'export JAVA_OPTS="-Xms1024m -Xmx1024m -XX:MaxPermSize=256m"']
                'export JAVA_OPTS="-Xms100m -Xmx100m -XX:MaxPermSize=256m"'] # saner values for now
        with cd('/home/fedora'):
            files.append('.bashrc', bash, use_sudo=True)

#     with cd('/home/fedora'):
    fedora_url = 'http://downloads.sourceforge.net/project/fedora-commons/fedora/3.4.2/fcrepo-installer-3.4.2.jar'
    sudo("wget -P /home/fedora '{}'".format(fedora_url))
    sudo('mkdir /usr/local/fedora')
    sudo('chown fedora:fedora /usr/local/fedora')
    sudo('mv /home/fedora/fcrepo-installer-3.4.2.jar /usr/local/fedora/')
    
def _mysql_install():
    '''
    Installs mysql and creates databases with credentials
    '''
    
    #require.mysql.server(password='qwerty')
    require.rpm.packages(['mysql', 'mysql-server'])
    sudo('chkconfig mysqld on')
    fabtools.service.start('mysqld')
    mysql_passwd = 'qwerty'
    sudo('/usr/bin/mysqladmin -u root password %s' % (mysql_passwd))
    
    with settings(mysql_user='root',mysql_password='qwerty'):
#     with settings(mysql_user='root',mysql_password=None):
        if not fabtools.mysql.user_exists('drupaldbuser'):
            fabtools.mysql.create_user('drupaldbuser', password='Password123')
        if not fabtools.mysql.user_exists('fedora'):
            fabtools.mysql.create_user('fedora', password='Password123')

        # Drupal databases
        if not fabtools.mysql.database_exists('drupal6_default'):
            fabtools.mysql.create_database('drupal6_default',owner='drupaldbuser')
        if not fabtools.mysql.database_exists('drupal6_exhibition'):
            fabtools.mysql.create_database('drupal6_exhibition',owner='drupaldbuser')
        if not fabtools.mysql.database_exists('drupal6_fieldbooks'):
            fabtools.mysql.create_database('drupal6_fieldbooks',owner='drupaldbuser')
        
        # Fedora databases
        if not fabtools.mysql.database_exists('fedora'):
            fabtools.mysql.create_database('fedora',owner='fedora')

        fabtools.mysql.query("GRANT ALL ON drupal6_default.* TO 'drupaldbuser'@'localhost' IDENTIFIED BY 'Password123';")
        fabtools.mysql.query("GRANT ALL ON drupal6_exhibition.* TO 'drupaldbuser'@'localhost' IDENTIFIED BY 'Password123';")
        fabtools.mysql.query("GRANT ALL ON drupal6_fieldbooks.* TO 'drupaldbuser'@'localhost' IDENTIFIED BY 'Password123';")
        fabtools.mysql.query("GRANT ALL ON fedora.* TO 'fedora'@'localhost' IDENTIFIED BY 'Password123';")
        
def _php_install():
    php = ['php','php-cli','php-common','php-gd','php-ldap','php-mbstring','php-mysql','php-pdo','php-soap','php-xml']
    require.rpm.packages(php)
    
    # Expand Key PHP Limits
    files.sed('/etc/php.ini', 'upload_max_filesize = \w+', 'upload_max_filesize = 64M', use_sudo=True)
    files.sed('/etc/php.ini', 'post_max_size = \w+', 'post_max_size = 100M', use_sudo=True)
    files.sed('/etc/php.ini', 'memory_limit = \w+', 'memory_limit = 128M', use_sudo=True)

def _apache_install():
    '''
    Installs apache and modifies configuration for Drupal
    '''

    # Install apache
    require.rpm.packages(['httpd'])
    
    # Create drupal DocumentRoot
#     if not fabtools.files.is_dir('/var/www/drupal'):
#         sudo('mkdir /var/www/drupal')
    
    # Modify httpd.conf
    httpd_conf = "/etc/httpd/conf/httpd.conf"
    files.sed(httpd_conf, 'DocumentRoot "/var/www/html"', 'DocumentRoot "/var/www/drupal"', use_sudo=True)
    if not files.contains(httpd_conf, '<Directory "/var/www/drupal">'):
        files.append(httpd_conf,'<Directory "/var/www/drupal">', use_sudo=True)
        files.append(httpd_conf,'   Options FollowSymLinks', use_sudo=True)
        files.append(httpd_conf,'   AllowOverride All', use_sudo=True)
        files.append(httpd_conf,'   Order allow,deny', use_sudo=True)
        files.append(httpd_conf,'   Allow from all', use_sudo=True)
        files.append(httpd_conf,'</Directory>', use_sudo=True)

    # Start apache
    sudo('chkconfig httpd on')
#     fabtools.service.start('httpd')

def _drupal_install():
    '''
    Installs Drupal
    '''

    # Install drush
    require.rpm.packages(['drupal6-drush'])
    
    # Download and unpack Drupal
#     run('wget http://ftp.drupal.org/files/projects/drupal-6.26.tar.gz')
#     run('tar -zxvf drupal-6.26.tar.gz')
#     sudo('mv drupal-6.26 /var/www')
    with cd('/var/www'):
        sudo('drush dl drupal-6.26')
        sudo('ln -s drupal-6.26 drupal')
#         sudo('chown -R vagrant:vagrant drupal')

    with cd('/var/www/drupal/'):
        drush_site_install = ['drush site-install',
                        '-y default',
                        '--account-mail=admin@localhost',
                        '--account-name=admin',
                        '--account-pass=Password123',
                        '--site-name=Sidora',
                        '--site-mail=admin@localhost',
#                        '--locale=si',
                        '--db-url=mysql://drupaldbuser:Password123@localhost/drupal6_default']
        drush_cmd = ' '.join(drush_site_install)
        sudo(drush_cmd)                  

    # Set up Multi-sites
    with cd('/var/www/drupal/'):
        drush_site_install = ['drush site-install',
                        '-y default',
                        '--account-mail=admin@localhost',
                        '--account-name=admin',
                        '--account-pass=Password123',
                        '--site-name=Sidora Exhibition',
                        '--sites-subdir=si-islandora.si.edu.exhibition',
                        '--site-mail=admin@localhost',
#                        '--locale=si',
                        '--db-url=mysql://drupaldbuser:Password123@localhost/drupal6_exhibition']
        drush_cmd = ' '.join(drush_site_install)
        sudo(drush_cmd)                  
        
    with cd('/var/www/drupal/'):
        drush_site_install = ['drush site-install',
                        '-y default',
                        '--account-mail=admin@localhost',
                        '--account-name=admin',
                        '--account-pass=Password123',
                        '--site-name=Sidora Exhibition',
                        '--sites-subdir=si-islandora.si.edu.fieldbooks',
                        '--site-mail=admin@localhost',
#                        '--locale=si',
                        '--db-url=mysql://drupaldbuser:Password123@localhost/drupal6_fieldbooks']
        drush_cmd = ' '.join(drush_site_install)
        sudo(drush_cmd)                  

    with cd('/var/www/drupal/sites/default'):
        sudo('chmod a-w .')
        sudo('chmod a-w settings.php')

    with cd('/var/www/drupal/sites/all/'):
        sudo('mkdir modules')

    with cd('/var/www/drupal/sites/all/modules'):
#         sudo('git clone git://github.com/Smithsonian/sidora.git')
        sudo('cp -r /vagrant/sidora ./sidora')

    with cd('/var/www/drupal/sites/all/modules'):
        drush_modules = []
        drush_cmd = 'drush -y dl ' + ' '.join(drush_modules)
        drush_cmd = 'drush -y en ' + ' '.join(drush_modules)
    
    # Set up Multi-sites
#     with cd('/var/www/drupal'):
#         sudo('ln -s . fieldbooks')
#         sudo('ln -s . exhibition')
#     with cd('/var/www/drupal/sites'):
#         sudo('cp -r default si-islandora.si.edu.fieldbooks')
#         sudo('cp -r default si-islandora.si.edu.exhibition')
#     with cd('/var/www/drupal/sites/default'):
#         sudo('cp default.settings.php settings.php')
#         sudo('chmod a+w .')
#         sudo('chmod a+w settings.php')
#     with cd('/var/www/drupal/sites/si-islandora.si.edu.fieldbooks'):
#         sudo('cp default.settings.php settings.php')
#         sudo('chmod a+w .')
#         sudo('chmod a+w settings.php')
#     with cd('/var/www/drupal/sites/si-islandora.si.edu.exhibition'):
#         sudo('cp default.settings.php settings.php')
#         sudo('chmod a+w .')
#         sudo('chmod a+w settings.php')


def _fedora_install():
    '''
    Installs Fedora
    '''
    
    with cd('/usr/local/fedora'):
        sudo('java -jar fcrepo-installer-3.4.2.jar /var/www/drupal/sites/all/modules/sidora/data/fedora/install.properties', user='fedora')
        
    # Start Tomcat
    sudo('/usr/local/fedora/tomcat/bin/startup.sh', user='fedora')
    
    # Check catalina.out for errors
#    tail -f /usr/local/fedora/tomcat/logs/catalina.out

    # Test Fedora in browser
    # run('curl http://localhost:8080/fedora')

    # Stop Tomcat
    sudo('/usr/local/fedora/tomcat/bin/shutdown.sh')
    
    # Remove the following Fedora default XACML policy files:
    with cd('/usr/local/fedora/data/fedora-xacml-policies/repository-policies/default'):
        sudo('rm deny-policy-management-if-not-administrator.xml')
        sudo('rm deny-apim-if-not-localhost.xml')

    # Add the Sidora policy files
    with cd('/var/www/drupal/sites/all/sidora/data/xacml'):
        sudo('cp *  /usr/local/fedora/data/fedora-xacml-policies/repository-policies/default')

    # Start Tomcat to apply the policy changes
    sudo('/usr/local/fedora/tomcat/bin/startup.sh')
        
def _gsearch_install():

    # Download GSearch
    with cd('/home/fedora'):
        sudo('wget http://sourceforge.net/projects/fedora-commons/files/services/3.1/genericsearch-2.2.zip/download', user='fedora')
        sudo('unzip genericsearch-2.2.zip', user='fedora')

        # Copy to Tomcat
        sudo('cp genericsearch-2.2/fedoragsearch.war /usr/local/fedora/tomcat/webapps/', user='fedora')
        # verify creation of /usr/local/fedora/tomcat/webapps/fedoragsearch ?
    
    # Edit configuration
    with cd('/var/www/drupal/sites/all/modules/sidora/data/fedoragsearch/WEB-INF/classes'):
        sudo('cp -r config /usr/local/fedora/tomcat/webapps/fedoragsearch/WEB-INF/classes/', user='fedora')
    
    fedoragsearch_path = '/usr/local/fedora/tomcat/webapps/fedoragsearch/WEB-INF/classes/config/'
    fedoragsearch_properties = fedoragsearch_path + 'fedoragsearch.properties'
    fedoragsearch_soapBase = 'http://localhost:8080/fedoragsearch/services'
    fedoragsearch_soapUser = 'fedora'
    fedoragsearch_soapPass = 'Password123'
    fedoragsearch_indexNames = 'gsearch_solr gsearch_fieldbooks'
    
    files.sed(fedoragsearch_properties, 'fedoragsearch.soapBase.+\n', fedoragsearch_soapBase, use_sudo=True)
    files.sed(fedoragsearch_properties, 'fedoragsearch.soapUser.+\n', fedoragsearch_soapUser, use_sudo=True)
    files.sed(fedoragsearch_properties, 'fedoragsearch.soapPass.+\n', fedoragsearch_soapPass, use_sudo=True)
    files.sed(fedoragsearch_properties, 'fedoragsearch.indexNames.+\n', fedoragsearch_indexNames, use_sudo=True)
    
    str1 = '<xsl:param name="HOST" select="\'si-fedoradev.si.edu\'"/>'
    str2 = '<xsl:param name="HOST" select="\'localhost\'"/>'    
    files.sed(fedoragsearch_path + 'index/gsearch_solr/demoFoxmlToSolr.xslt', str1, str2, use_sudo=True)

    # Restart tomcat
    stop('tomcat')
    start('tomcat')
    
def _solr_install():
    stop('tomcat')
    
    # Download and install Solr:
    with cd('/home/fedora'):
        require.rpm.packages('ant','xml-commons-apis')
        sudo('wget http://archive.apache.org/dist/lucene/solr/1.4.1/apache-solr-1.4.1.zip')
        sudo('unzip apache-solr-1.4.1.zip -d /opt/')
    with cd('/opt'):
        sudo('ln -s /opt/apache-solr-1.4.1 /opt/solr')
        sudo('chown -R fedora:fedora /opt/apache-solr-1.4.1')
        
    # Install the Solr Index Configurations
    with cd('/usr/local/fedora'):
        sudo('cp -r /var/www/drupal-6.26/sites/all/modules/sidora/data/solr/gsearch_solr .')
        sudo('cp -r /var/www/drupal-6.26/sites/all/modules/sidora/data/solr/gsearch_fieldbooks .')
       
    # Solr.xml    
    text = """
<Context docBase="/opt/solr/dist/apache-solr-1.4.1.war" debug="0" crossContext="true">
    <Environment name="solr/home" type="java.lang.String" value="/usr/local/fedora/gsearch_solr/solr" override="true" />
</Context>"""
    files.append('/usr/local/fedora/tomcat/conf/Catalina/localhost/solr.xml',text, use_sudo=True)
    
    # Start Tomcat
    start('tomcat')


def _drupal_filter_install():
    stop('tomcat')
    
    # Install the authorization module
    with cd('/usr/local/fedora/tomcat/webapps/fedora/WEB-INF/lib'):
        sudo('cp /var/www/drupal-6.26/sites/all/modules/sidora/data/fedora/DrupalAuthModule.jar .')
    
    # Install and configure Fedora security    
    text = """
fedora-auth
{
        org.fcrepo.server.security.jaas.auth.module.XmlUsersFileModule required
        debug=true; 
        ca.upei.roblib.fedora.servletfilter.DrupalAuthModule required
        debug=true; 
};
"""
    files.append('/usr/local/fedora/server/config/jaas.conf',text, use_sudo=True)
    sudo('cp filter-drupal.xml /usr/local/fedora/server/config/filter-drupal.xml')
    
    # Update the passwords in filter-drupal.xml
    str1 
    str2
    files.sed('/usr/local/fedora/server/config/filter-drupal.xml', str1, str2, use_sudo=True)
    
    # Start Tomcat
    start('tomcat')
    
def _fits_install():
    '''
    FITS provides a framework that integrates a number of tools for characterizing files (bitsteams).
    '''
    
    with cd('/home/fedora'):
        sudo('wget https://fits.googlecode.com/files/fits-0.6.2.zip', user='fedora')
        sudo('unzip fits-0.6.2.zip -d /opt/')
        sudo('ln -s /opt/fits-0.6.2/fits.sh /usr/bin/fits')
        sudo('ln -s /opt/fits-0.6.2 fits') # wrong directory?        
        
def _microservices_install():
    
    # Add the EPEL repository
    #wget http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
    require.rpm.package('epel-release-5-4.noarch4')

    # Install Python
    py_pckgs = ['readline-devel','sqlite-devel','zlib-devel','openssl-devel','bzip2-devel','ncurses-devel']
    require.rpm.packages(py_pckgs)
    require.rpm.packages('python26')
    require.rpm.packages('python-devel')
    require.rpm.packages('python-setuptools')

    # Create a location for installing micro services
    with cd('/opt'):
        sudo('mkdir islandora_microservices')
        sudo('chown fedora:fedora islandora_microservices')
    with cd('/opt/islandora_microservices'):
        sudo('cp /vagrant/modules/islandora_microservices ./')
    with cd('/vagrant/modules/islandora_microservices/islandora_microservices'):
        sudo('cp islandora_listener.cfg.default islandora_listener.cfg')

# Edit islandora_listener.cfg. Change the password to whatever you have chosen.
# and enable the smithsonian_plugin.
# [Plugins]
# enabled: smithsonian_plugin

    # Obtain the Islandora Python Utilities
    with cd('/opt'):
        sudo('cp /vagrant/modules/IslandoraPYUtils ./')
    with cd('/opt/IslandoraPYUtils'):
        sudo('python2.6 setup.py install')

    

# @task
# def deploy():
#     # Require SIdora from github
#     #fabtools.require.git.working_copy("https://github.com/Smithsonian/sidora.git")
#     fabtools.require.git.working_copy("https://github.com/Smithsonian/sidora-deploy")
#     #run("git clone https://github.com/Smithsonian/sidora.git")

@task
def setup():
    # Require git
    fabtools.rpm.install('git')
    
    
@task
def start(service):
    if service == 'tomcat':
        sudo('/usr/local/fedora/tomcat/bin/startup.sh')
    else:
        fabtools.service.start(service)    
    
@task
def stop(service):
    if service == 'tomcat':
        sudo('/usr/local/fedora/tomcat/bin/shutdown.sh')
    else:
        fabtools.service.stop(service)    
    
##########################    
# Fedora server management
@task
def fc(cmd):
    sudo('/etc/init.d/fcrepo-server %s' % cmd)
    
    