# the command script to install battery monitor daemon

set -x
sudo cp out/batterymonitor /bin/
sudo cp stuff/rc.local /etc/
sudo cp stuff/rc.local.service /lib/systemd/system/
sudo systemctl enable rc-local
sudo systemctl start rc-local.service
