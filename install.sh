#!/usr/bin/env sh
# Install Mangdang Pupper-Mini

# Overlay dtbo, IO configuration and services
sudo cp Mangdang/PWMController/i2c-pwm-pca9685a.dtbo /boot/firmware/overlays/
sudo cp Mangdang/EEPROM/i2c3.dtbo /boot/firmware/overlays/
sudo cp Mangdang/IO_Configuration/syscfg.txt /boot/firmware/ -f
sudo cp Mangdang/IO_Configuration/config.txt /boot/firmware/ -f
sudo cp Mangdang/stuff/*.mp3 /home/ubuntu/Music/ -f

# Install mangdang power-on service
cd /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/FuelGauge
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/FuelGauge/install.sh
cd /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/System
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/System/install.sh

# Install Mangdang EEPROM
cd /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/EEPROM
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/Mangdang/EEPROM/install.sh

# Install standford robot and UDPComms services
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/StanfordQuadruped/install.sh
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/UDPComms/install.sh

