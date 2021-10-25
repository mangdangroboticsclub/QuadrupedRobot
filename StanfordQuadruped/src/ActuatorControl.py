import os
import sys
import time

class ActuatorControl:
    
    def __init__(self,pwm_number):

        self.pwm_number = pwm_number

    def updateDutyCycle(self,angle):

        duty_cycle = int((1.11*angle+50)*10000)

        return duty_cycle

    def updateActuatorAngle(self,angle):

        if self.pwm_number == 1:
            actuator_name = 'pwm1'
        elif self.pwm_number == 2:
            actuator_name = 'pwm2'
        elif self.pwm_number == 3:
            actuator_name = 'pwm3'

        duty_cycle = self.updateDutyCycle(angle)
        file_node = '/sys/class/pwm/pwmchip0/' + actuator_name+ '/duty_cycle'
        f = open(file_node, "w")
        f.write(str(duty_cycle))

#test = ActuatorControl(3)
#time.sleep(10)
#for index in range(30):
#    test.updateActuatorAngle(index*3)
#    time.sleep(0.1)
#    test.updateActuatorAngle(0)
