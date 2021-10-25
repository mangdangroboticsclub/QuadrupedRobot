import os
import sys

sys.path.append("/home/ubuntu/Robotics/QuadrupedRobot/")
sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("/home/ubuntu/Robotics/QuadrupedRobot") for name in dirs])
from Mangdang import PWMController
from pupper.Config import ServoParams, PWMParams
#from __future__ import division
import numpy as np

class HardwareInterface:
    def __init__(self):
        self.pwm_params = PWMParams()
        self.servo_params = ServoParams()

    def set_actuator_postions(self, joint_angles):
        send_servo_commands(self.pwm_params, self.servo_params, joint_angles)

    def set_actuator_position(self, joint_angle, axis, leg):
        send_servo_command(self.pwm_params, self.servo_params, joint_angle, axis, leg)


def pwm_to_duty_cycle(pulsewidth_micros, pwm_params):
    """Converts a pwm signal (measured in microseconds) to a corresponding duty cycle on the gpio pwm pin

    Parameters
    ----------
    pulsewidth_micros : float
        Width of the pwm signal in microseconds
    pwm_params : PWMParams
        PWMParams object

    Returns
    -------
    float
        PWM duty cycle corresponding to the pulse width
    """
    pulsewidth_micros = int(pulsewidth_micros / 1e6 * pwm_params.freq * pwm_params.range)
    if np.isnan(pulsewidth_micros):
        return 0
    return int(np.clip(pulsewidth_micros, 0, 4096))


def angle_to_pwm(angle, servo_params, axis_index, leg_index):
    """Converts a desired servo angle into the corresponding PWM command

    Parameters
    ----------
    angle : float
        Desired servo angle, relative to the vertical (z) axis
    servo_params : ServoParams
        ServoParams object
    axis_index : int
        Specifies which joint of leg to control. 0 is abduction servo, 1 is inner hip servo, 2 is outer hip servo.
    leg_index : int
        Specifies which leg to control. 0 is front-right, 1 is front-left, 2 is back-right, 3 is back-left.

    Returns
    -------
    float
        PWM width in microseconds
    """
    angle_deviation = (
                              angle - servo_params.neutral_angles[axis_index, leg_index]
                      ) * servo_params.servo_multipliers[axis_index, leg_index]
    pulse_width_micros = (
            servo_params.neutral_position_pwm
            + servo_params.micros_per_rad * angle_deviation
    )
    return pulse_width_micros


def angle_to_duty_cycle(angle, pwm_params, servo_params, axis_index, leg_index):
    duty_cycle_f = angle_to_pwm(angle, servo_params, axis_index, leg_index) * 1e3
    if np.isnan(duty_cycle_f):
        return 0
    return int(duty_cycle_f)


def initialize_pwm(pi, pwm_params):
    pi.set_pwm_freq(pwm_params.freq)


def send_servo_commands(pwm_params, servo_params, joint_angles):
    for leg_index in range(4):
        for axis_index in range(3):
            duty_cycle = angle_to_duty_cycle(
                joint_angles[axis_index, leg_index],
                pwm_params,
                servo_params,
                axis_index,
                leg_index,
            )
            # write duty_cycle to pwm linux kernel node
            file_node = "/sys/class/pwm/pwmchip0/pwm" + str(pwm_params.pins[axis_index, leg_index]) + "/duty_cycle"
            f = open(file_node, "w")
            f.write(str(duty_cycle))


def send_servo_command(pwm_params, servo_params, joint_angle, axis, leg):
    duty_cycle = angle_to_duty_cycle(joint_angle, pwm_params, servo_params, axis, leg)
    file_node = "/sys/class/pwm/pwmchip0/pwm" + str(pwm_params.pins[axis, leg]) + "/duty_cycle"
    f = open(file_node, "w")
    f.write(str(duty_cycle))


def deactivate_servos(pi, pwm_params):
    for leg_index in range(4):
        for axis_index in range(3):
            pi.set_pwm(pwm_params.pins[axis_index, leg_index], 0, 0)
