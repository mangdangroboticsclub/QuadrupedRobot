#!/usr/bin/env sh
# Install EEPROM driver
#

set -x
sudo cp i2c3.dtbo /boot/firmware/overlays/
make
make install
