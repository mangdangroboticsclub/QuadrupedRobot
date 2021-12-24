# The command script to init system for mini pupper 
set -x
sudo chmod 440 sudoers
sudo cp sudoers  /etc/
sudo cp rc.local /etc/
sudo cp rc.local.service /lib/systemd/system/
sudo systemctl enable rc-local
sudo systemctl start rc-local.service
