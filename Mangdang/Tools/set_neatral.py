import sys
import os

sys.path.append("/home/ubuntu/Robotics/QuadrupedRobot")
sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("/home/ubuntu/Robotics/QuadrupedRobot") for name in dirs])
from Mangdang import PWMController
from pupper.Config import PWMParams, Configuration, ServoParams


def main():
    """Main program
    """

    print ("starting...")

    # Servo neutral setting
    pwm = PWMController.PCA9685()
    pwm_params = PWMParams()
    servo_params = ServoParams()
    pwm.set_pwm_freq(pwm_params.freq)

    pulsewidth_neutral = int(servo_params.neutral_position_pwm / 1e6 * pwm_params.freq * pwm_params.range)
    print("pwm 0 setting pwm off parameter " , pulsewidth_neutral);
    pwm.set_pwm(0, 0, pulsewidth_neutral)
    print("pwm 1 setting pwm off parameter " , pulsewidth_neutral);
    pwm.set_pwm(1, 0, pulsewidth_neutral)
    print("pwm 2 setting pwm off parameter " , int(1000 / 1e6 * pwm_params.freq * pwm_params.range));
    pwm.set_pwm(2, 0, int(1000 / 1e6 * pwm_params.freq * pwm_params.range))
    print("pwm 3 setting pwm off parameter " , int(2000 / 1e6 * pwm_params.freq * pwm_params.range));
    pwm.set_pwm(3, 0, int(2000 / 1e6 * pwm_params.freq * pwm_params.range))
    print ("end ...")

main()
