#yes | sudo apt-get install adafruit-circuitpython-busdevice
yes | sudo apt-get install cmake
yes | sudo apt-get install i2c-tools python-smbus
yes | pip install wiringpi
yes | pip3 install adafruit-blinka
yes | pip3 install adafruit-CircuitPython-BusDevice

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

cd $ROOT_DIR
sudo cp Mangdang/IO_Configuration/config.txt /boot/ -f
