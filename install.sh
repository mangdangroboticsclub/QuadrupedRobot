#!/usr/bin/env sh
# Install Mangdang Puppe-Mini

# build and deploy battery monitor deamon and IO configuration
sudo cp Mangdang/IO_Configuration/syscfg.txt /boot/firmware/ -f
cd Mangdang/BatteryMonitor/
cmake .
make
sudo bash install.sh

# Install standford robot and UDPComms services
sudo bash ~/Robotics/QuadrupedRobot/StanfordQuadruped/install.sh
sudo bash ~/Robotics/QuadrupedRobot/UDPComms/install.sh

