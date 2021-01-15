# PupperCommand
## Installation
```shell
git clone https://github.com/stanfordroboticsclub/PupperCommand.git
cd PupperCommand
sudo bash install.sh
```
Then clone https://github.com/stanfordroboticsclub/PS4Joystick/ and follow the installation instructions in the README.

## Starting the joystick publisher
1. The ```install.sh``` script makes the Raspberry Pi automatically look to pair and connect to PS4 joysticks on boot.
2. So once the Raspberry Pi turns on, put the PS4 controller into pairing mode by holding the share and PS button at the same time. The light should start blinking in bursts of two. 
3. By around 10 seconds, the joystick should have paired with the Raspberry Pi and the front light on the joystick will change to whatever color you specify in the ```joystick.py``` script.

## Debugging 
To see if the controller is publishing to the Rover topic use: 
```shell
rover peek 8830
```

You can also check the status of the system daemon (systemd) running the ```joystick.py``` script by doing
```shell
sudo systemctl status joystick
```
If it shows that the service failed, you can try
```shell
sudo systemctl stop joystick
sudo systemctl start joystick
```

## Notes
If a packet is lost over the joystick connection, the PS4Joystick code will raise an exception and cause the program to exit. Systemd will then restart the ```joystick.py``` script, which means you will have to re-pair the joystick (hold share + ps4 button until double blinking). 

