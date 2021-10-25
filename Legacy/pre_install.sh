#!/usr/bin/env sh

###Install all software dependence for Mini Pupper

#Update time and source
sudo date -s "$(curl -s --head http://www.baidu.com | grep ^Date: | sed 's/Date: //g')"
sudo apt-get update

#dependencies
sudo apt-get install -y libsdl-ttf2.0-0
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libhdf5-dev
sudo apt-get install -y python3-pip
sudo apt-get install -y cmake
sudo apt-get install -y i2c-tools
sudo apt-get install -y python


#Libraries of Python3
yes | sudo pip3 install Cython
yes | sudo pip3 install numpy
yes | sudo pip3 install msgpack
yes | sudo pip3 install pexpect
yes | sudo pip3 install transforms3d
yes | sudo pip3 install matplotlib
yes | sudo pip3 install ds4drv    # driver for PS4
yes | sudo pip3 install pyserial  # serial port control for python
yes | sudo pip3 install RPi.GPIO
yes | sudo pip3 install adafruit-blinka==5.13.1
yes | sudo pip3 install adafruit-CircuitPython-BusDevice==5.0.4
yes | sudo pip3 install spidev

#The WA for Pillow lib in raspberry ubuntu 20.04
sudo rm /usr/lib/python3/dist-packages/PIL/ImageOps.py -f
sudo cp ImageOps.py  /usr/lib/python3/dist-packages/PIL/ImageOps.py -f
