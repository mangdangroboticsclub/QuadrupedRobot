#!/usr/bin/env sh

sudo bash  ~/Robotics/QuadrupedRobot/PupperCommand/install.sh
sudo bash ~/Robotics/QuadrupedRobot/PS4Joystick/install.sh

cd ~/Robotics/QuadrupedRobot/StanfordQuadruped
sudo ln -s $(realpath .)/robot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot
sudo systemctl start robot
