#!/usr/bin/env sh
# Install pca9685 driver
#

set -x
sudo cp i2c-pwm-pca9685a.dtbo /boot/firmware/overlays/
make
make install
