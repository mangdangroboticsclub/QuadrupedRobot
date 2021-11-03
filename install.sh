#!/usr/bin/env sh
# Install Mangdang Puppe-Mini

# overlay dtbo, IO configuration and services
sudo cp Mangdang/PWMController/i2c-pwm-pca9685a.dtbo /boot/firmware/overlays/
sudo cp Mangdang/EEPROM/i2c3.dtbo /boot/firmware/overlays/
sudo cp Mangdang/IO_Configuration/syscfg.txt /boot/firmware/ -f
cd /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/FuelGauge
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/FuelGauge/install.sh
cd /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/System
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/System/install.sh

# Install standford robot and UDPComms services
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/StanfordQuadruped/install.sh
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/UDPComms/install.sh

