#yes | sudo apt-get install adafruit-circuitpython-busdevice
yes | sudo apt-get install cmake

ROOT_DIR=`pwd`

cd Mangdang/BatteryMonitor/
cmake .
make
sudo bash install.sh

cd $ROOT_DIR
cd StanfordQuadruped
sudo bash install.sh

cd $ROOT_DIR
cd UDPComms
sudo bash install.sh
