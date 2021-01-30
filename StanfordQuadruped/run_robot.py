import os
import sys
import threading
import time

import numpy as np

sys.path.append("..")
sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])
from Mangdang.IMU.IMU import IMU
from src.Controller import Controller
from src.JoystickInterface import JoystickInterface
from src.State import State
from pupper.HardwareInterface import HardwareInterface
from pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics

quat_orientation = np.array([1, 0, 0, 0])  # IMU orientation data (Quaternions)


def IMU_read(use_IMU, imu):
    """IMU data read program
    """
    global quat_orientation
    if use_IMU:
        while True:
            quat_orientation = imu.read_orientation()
            time.sleep(0.01)
    else:
        quat_orientation = np.array([1, 0, 0, 0])


def main():
    """Main program
    """
    use_IMU = False

    # Create config
    config = Configuration()
    hardware_interface = HardwareInterface()

    # Create imu handle

    if use_IMU:
        imu = IMU()
        time.sleep(0.1)
        imu.begin()
        time.sleep(0.1)

    # Startup the IMU data reading thread
    try:
        _imuThread = threading.Thread(target=IMU_read, args=(use_IMU, imu,))
        _imuThread.start()
    except:
        print("Error: IMU thread could not startup!!!")

    # Create controller and user input handles
    controller = Controller(
        config,
        four_legs_inverse_kinematics,
    )
    state = State()
    print("Creating joystick listener...")
    joystick_interface = JoystickInterface(config)
    print("Done.")

    last_loop = time.time()

    print("Summary of gait parameters:")
    print("overlap time: ", config.overlap_time)
    print("swing time: ", config.swing_time)
    print("z clearance: ", config.z_clearance)
    print("x shift: ", config.x_shift)

    # Wait until the activate button has been pressed
    while True:
        print("Waiting for L1 to activate robot.")
        while True:
            command = joystick_interface.get_command(state)
            joystick_interface.set_color(config.ps4_deactivated_color)
            if command.activate_event == 1:
                break
            time.sleep(0.1)
        print("Robot activated.")
        joystick_interface.set_color(config.ps4_color)

        while True:
            now = time.time()
            if now - last_loop < config.dt:
                continue
            last_loop = time.time()

            # Parse the udp joystick commands and then update the robot controller's parameters
            command = joystick_interface.get_command(state)
            if command.activate_event == 1:
                print("Deactivating Robot")
                break

            # Read imu data. Orientation will be None if no data was available
            state.quat_orientation = quat_orientation
            # Step the controller forward by dt
            controller.run(state, command)

            # Update the pwm widths going to the servos
            hardware_interface.set_actuator_postions(state.joint_angles)
main()
