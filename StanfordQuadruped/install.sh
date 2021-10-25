#!/usr/bin/env sh

sudo bash  /home/ubuntu/Robotics/QuadrupedRobot/PupperCommand/install.sh
sudo bash  /home/ubuntu/Robotics/QuadrupedRobot/PS4Joystick/install.sh

cd /home/ubuntu/Robotics/QuadrupedRobot/StanfordQuadruped
sudo ln -s $(realpath .)/robot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot
sudo systemctl start robot
