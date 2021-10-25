import os
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while 1:
    if not GPIO.input(21):
        print("eanbling joystick")
        os.system("sudo systemctl start ds4drv")
        os.system("sudo systemctl start joystick")
        #os.system("screen sudo python3 /home/pi/RoverCommand/joystick.py")

    else:
        os.system("sudo systemctl stop ds4drv")
        os.system("sudo systemctl stop joystick")
        print("not eanbling joystick")

    time.sleep(5)
