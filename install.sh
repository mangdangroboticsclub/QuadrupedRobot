#!/usr/bin/env sh
# Install Mangdang Puppe-Mini

# build and deploy battery monitor deamon and IO configuration
sudo cp Mangdang/PWMController/i2c-pwm-pca9685a.dtbo /boot/firmware/overlays/
sudo cp Mangdang/IO_Configuration/syscfg.txt /boot/firmware/ -f
cd Mangdang/BatteryMonitor/
cmake .
make
sudo bash install.sh

# Install standford robot and UDPComms services
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/StanfordQuadruped/install.sh
sudo bash /home/ubuntu/Robotics/QuadrupedRobot/UDPComms/install.sh

