Vagrant deployment for Sidora
=============================

Deployment scripts for automated scratch build of Sidora.

Requirements
------------
* Download and install VirtualBox (https://www.virtualbox.org/)
* Download and install Vagrant (http://www.vagrantup.com/)
* Download and install Fabric (http://fabfile.org/)
* Download and install Fabtools

Note - the easiest way to install Fabric is through pip (or easy_install):

```
 pip install fabric
```

Fabtools currently requires development version:
```
 pip install git+git://github.com/ronnix/fabtools.git
```

Installation
------------
Setup the local VM environment:
```
 git clone https://github.com/Smithsonian/vagrant-sidora.git
 cd vagrant-sidora
 git submodule init
 git submodule update
 vagrant up
```

Then provision using fabric:
```
 fab vagrant install
```


Starting up services
--------------------

Apache
```
 fab vagrant start:httpd
```

Fedora

Point your browser at http://localhost:8080/fedora after starting up the fedora server.  You can do this via fabric (see below), for convenience, or you can do it manually like so:
```
 vagrant ssh -c "sudo /etc/init.d/fcrepo-server start"
```

Status
------
Currently this launcher only handles deployment of Fedora Commons 3.4.2.  It will gradually include the rest of the Islandora and Sidora stack.

References
----------
* The Fedora Commons deployment is based on instant-fedora-commons (https://github.com/kaisternad/instant-fedora-commons)
