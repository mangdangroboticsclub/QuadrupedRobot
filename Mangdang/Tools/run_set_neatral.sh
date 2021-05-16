#!/usr/bin/env sh

# step 1 stop robot service
systemctl stop robot

# step 2 set neatral position

echo 1500000 > /sys/class/pwm/pwmchip0/pwm0/duty_cycle
echo "pwm 0 setting pwm off parameter --> 90 degree "

echo 1500000 > /sys/class/pwm/pwmchip0/pwm1/duty_cycle
echo "pwm 1 setting pwm off parameter --> 90 degree"

echo 500000 > /sys/class/pwm/pwmchip0/pwm2/duty_cycle
echo "pwm 2 setting pwm off parameter --> 0 degree"

echo 2500000 > /sys/class/pwm/pwmchip0/pwm3/duty_cycle
echo "pwm 3 setting pwm off parameter --> 180 degree"

sleep 1

echo "Done ! "
