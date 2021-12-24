#!/usr/bin/env sh
# Install FuelGauge driver and battery monitor daemon
#

set -x

sudo cp i2c4.dtbo /boot/firmware/overlays/
sudo cp max1720x_battery.ko /lib/modules/`uname -r`/kernel/drivers/power/supply/
sudo depmod -a

sudo cp battery_monitor /usr/bin/
sudo cp battery_monitor.service /lib/systemd/system/
sudo systemctl enable  battery_monitor.service


