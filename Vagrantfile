Vagrant.configure("2") do |config|
  config.vm.box = "almalinux/9"

  config.vm.define "destination" do |dest|
    dest.vm.hostname = "destination"
    dest.vm.network "private_network", ip: "192.168.10.10"
    dest.vm.provision "shell", path: "scripts/provision_destination.sh"
  end

  config.vm.define "bastion" do |bast|
    bast.vm.hostname = "bastion"
    bast.vm.network "private_network", ip: "192.168.20.10"
    bast.vm.provision "shell", path: "scripts/provision_bastion.sh"
  end

  config.vm.define "admin-server" do |admin|
    admin.vm.hostname = "admin-server"
    admin.vm.network "private_network", ip: "192.168.30.10"
    admin.vm.provision "shell", path: "scripts/provision_admin.sh"
  end
end
