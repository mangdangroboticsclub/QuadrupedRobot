# PS4Joystick

Code allowing the use of a DualShock (PS4 Joystick) over Bluetooth on Linux. Over USB comming soon. `mac_joystick.py` shows how to emulate something similar on macOS, but without the fancy features.

Note: We have updated from the previous version so make sure you disable ds4drv from running automatically at startup as they will conflict.

This method still requires [ds4drv](https://github.com/chrippa/ds4drv) however it doesn't run it as a separate service and then separately pull joystick data using Pygame. Instead it imports ds4drv directly which gives us much more control over the joystick behaviour. Specifically:

- It will only pair to one joystick allowing us to run multiple robots at a time
- Allows for launching joystick code via systemd at boot using `sudo systemctl enable joystick`
- Can change joystick colors and using rumble directly from Python (can also access the touchpad and IMU!)
- Is a much nicer interface than using Pygame, as the axes are actually named as opposed to arbitrarly numbered! The axis directions are consistant with Pygame. 
- Doesn't need $DISPLAY hacks to run on headless devices

### Usage

Take a look at `rover_example.py` as it demonstrates most features. 
To implement this functionality to a new repository (say [PupperCommand](https://github.com/stanfordroboticsclub/PupperCommand)) you can just call `from PS4Joystick import Joystick` anywhere once you've installed the module. Replicate `joystick.service` in that repository.


### Install

``` sudo bash install.sh ```


### macOS

Sadly ds4drv doesn't work on Macs. But you can get some of the functionality by installing Pygame with `sudo pip3 install Pygame`. Take a look in `mac_joystick.py` for an example. Note this only works over USB (plug the controller in using a micro usb cable) and the mapping is different than using Pygame with ds4drv