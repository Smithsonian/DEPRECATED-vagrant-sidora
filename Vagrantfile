# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # config.vm.box_url = "http://domain.com/path/to/above.box"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network :forwarded_port, guest: 80, host: 8080  
  config.vm.network :forwarded_port, guest: 8080, host: 8080,
    auto_correct: true
  config.vm.network :forwarded_port, guest: 8443, host: 8443,
    auto_correct: true
  #config.vm.network :auto_correct

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  #config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Enable provisioning with chef solo, specifying a cookbooks path, roles
  # path, and data_bags path (all relative to this Vagrantfile), and adding
  # some recipes and/or roles.
  #
  # config.vm.provision :chef_solo do |chef|
  #   chef.cookbooks_path = "../my-recipes/cookbooks"
  #   chef.roles_path = "../my-recipes/roles"
  #   chef.data_bags_path = "../my-recipes/data_bags"
  #   chef.add_recipe "mysql"
  #   chef.add_role "web"
  #
  #   # You may also specify custom JSON attributes:
  #   chef.json = { :mysql_password => "foo" }
  # end

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "cookbooks"
    chef.add_recipe "apt"
    chef.add_recipe "mysql::server"
    chef.add_recipe "java"
    chef.add_recipe "fedora"
    chef.json = { 
      :mysql => {:server_root_password => "foo", :bind_address => "localhost"},
      :java => {:install_flavor => "openjdk", :jdk_version => '7'},
      :fcrepo => {
        :installpaths => {
          :fedora => "/usr/share/fcrepo",
          :tomcat => "/usr/share/fcrepo/tomcat"
        },
        :database => {
          :host => "localhost",
          :name => "fedora3",
          :username => "fedoraAdmin",
          :password => "fedoraAdmin"
        },
        :hostname => "localhost",
        :context => "fedora",
        :port => "8080",
        :osuser => "fcrepo",
        :osgroup => "fcrepo",
        :adminpassword => "fedoraAdmin",
        :users => {
          :databaseUser => {
            :username => "fedora",
            :password => "fedora"
          }
        }
      }
    }
  end
end
