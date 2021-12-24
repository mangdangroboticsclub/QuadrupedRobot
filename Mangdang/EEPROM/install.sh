#!/usr/bin/env sh
# Install EEPROM driver
#

set -x
sudo cp i2c3.dtbo /boot/firmware/overlays/
sudo cp at24.ko /lib/modules/`uname -r`/kernel/drivers/nvmem/
sudo depmod -a
