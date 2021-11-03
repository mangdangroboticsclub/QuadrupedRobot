# the command script to init system for mini pupper 
set -x
sudo cp rc.local /etc/
sudo cp rc.local.service /lib/systemd/system/
sudo systemctl enable rc-local
sudo systemctl start rc-local.service
