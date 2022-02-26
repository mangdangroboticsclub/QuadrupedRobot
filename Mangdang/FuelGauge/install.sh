#!/usr/bin/env sh
# Install FuelGauge driver and battery monitor daemon
#

set -x

sudo cp i2c4.dtbo /boot/firmware/overlays/
make clean
make
make install

sudo cp battery_monitor /usr/bin/
sudo cp battery_monitor.service /lib/systemd/system/
sudo systemctl enable  battery_monitor.service


