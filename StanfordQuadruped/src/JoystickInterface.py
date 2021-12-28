import UDPComms
import numpy as np
import time
from src.State import BehaviorState, State
from src.Command import Command
from src.Utilities import deadband, clipped_first_order_filter


class JoystickInterface:
    def __init__(
        self, config, udp_port=8830, udp_publisher_port = 8840,
    ):
        self.config = config
        self.previous_gait_toggle = 0
        self.previous_state = BehaviorState.REST
        self.previous_hop_toggle = 0
        self.previous_activate_toggle = 0
        self.previous_dance_activate_toggle = 0

        self.previous_dance_switch_toggle = 0
        self.previous_gait_switch_toggle = 0

        self.message_rate = 50
        self.udp_handle = UDPComms.Subscriber(udp_port, timeout=0.3)
        self.udp_publisher = UDPComms.Publisher(udp_publisher_port,65532)


    def get_command(self, state, do_print=False):
        try:
            msg = self.udp_handle.get()
            command = Command()

            ####### Handle discrete commands ########
            # Check if requesting a state transition to trotting, or from trotting to resting
            gait_toggle = msg["R1"]
            command.trot_event = (gait_toggle == 1 and self.previous_gait_toggle == 0)

            # Check if requesting a state transition to hopping, from trotting or resting
            hop_toggle = msg["x"]
            command.hop_event = (hop_toggle == 1 and self.previous_hop_toggle == 0)
            
            dance_activate_toggle = msg["circle"]
            command.dance_activate_event = (dance_activate_toggle == 1 and self.previous_dance_activate_toggle == 0)
            
            shutdown_toggle = msg["triangle"]
            command.shutdown_signal = shutdown_toggle

            activate_toggle = msg["L1"]
            command.activate_event = (activate_toggle == 1 and self.previous_activate_toggle == 0)

            dance_toggle = msg["L2"]
            command.dance_switch_event = (dance_toggle == 1 and self.previous_dance_switch_toggle != 1)

            gait_switch_toggle = msg["R2"]
            command.gait_switch_event = (gait_switch_toggle == 1 and self.previous_gait_switch_toggle != 1)

            # Update previous values for toggles and state
            self.previous_gait_toggle = gait_toggle
            self.previous_hop_toggle = hop_toggle
            self.previous_activate_toggle = activate_toggle
            self.previous_dance_activate_toggle = dance_activate_toggle

            self.previous_dance_switch_toggle = dance_toggle
            self.previous_gait_switch_toggle = gait_switch_toggle

            ####### Handle continuous commands ########
            x_vel = msg["ly"] * self.config.max_x_velocity
            y_vel = msg["lx"] * -self.config.max_y_velocity
            command.horizontal_velocity = np.array([x_vel, y_vel])
            command.yaw_rate = msg["rx"] * -self.config.max_yaw_rate

            message_rate = msg["message_rate"]
            message_dt = 1.0 / message_rate

            pitch = msg["ry"] * self.config.max_pitch
            deadbanded_pitch = deadband(
                pitch, self.config.pitch_deadband
            )
            pitch_rate = clipped_first_order_filter(
                state.pitch,
                deadbanded_pitch,
                self.config.max_pitch_rate,
                self.config.pitch_time_constant,
            )
            command.pitch = state.pitch + message_dt * pitch_rate

            height_movement = msg["dpady"]
            command.height = state.height - message_dt * self.config.z_speed * height_movement

            roll_movement = - msg["dpadx"]
            command.roll = state.roll + message_dt * self.config.roll_speed * roll_movement

            return command

        except UDPComms.timeout:
            if do_print:
                print("UDP Timed out")
            return Command()


    def set_color(self, color):
        joystick_msg = {"ps4_color": color}
        self.udp_publisher.send(joystick_msg)
