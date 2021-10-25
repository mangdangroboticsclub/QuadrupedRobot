from UDPComms import Publisher
from PS4Joystick import Joystick

import time
from enum import Enum

drive_pub = Publisher(8830)
arm_pub = Publisher(8410)

j=Joystick()

MODES = Enum('MODES', 'SAFE DRIVE ARM')
mode = MODES.SAFE

while True:
    values = j.get_input()

    if( values['button_ps'] ):
        if values['dpad_up']:
            mode = MODES.DRIVE
            j.led_color(red=255)
        elif values['dpad_right']:
            mode = MODES.ARM
            j.led_color(blue=255)
        elif values['dpad_down']:
            mode = MODES.SAFE
            j.led_color(green=255)

        # overwrite when swiching modes to prevent phantom motions
        values['dpad_down'] = 0
        values['dpad_up'] = 0
        values['dpad_right'] = 0
        values['dpad_left'] = 0

    if mode == MODES.DRIVE:
        forward_left  = - values['left_analog_y']
        forward_right = - values['right_analog_y']
        twist = values['right_analog_x']

        on_right = values['button_r1']
        on_left = values['button_l1']
        l_trigger = values['l2_analog']

        if on_left or on_right:
            if on_right:
                forward = forward_right
            else:
                forward = forward_left

            slow = 150
            fast = 500

            max_speed = (fast+slow)/2 + l_trigger*(fast-slow)/2

            out = {'f':(max_speed*forward),'t':-150*twist}
            drive_pub.send(out)
            print(out)
        else:
            drive_pub.send({'f':0,'t':0})

    elif mode == MODES.ARM:
        r_forward  = - values['right_analog_y']
        r_side = values['right_analog_x']

        l_forward  = - values['left_analog_y']
        l_side = values['left_analog_x']

        r_shoulder  = values['button_r1']
        l_shoulder  = values['button_l1']

        r_trigger  = values['r2_analog']
        l_trigger = values['l2_analog']

        square  = values['button_square']
        cross  = values['button_cross']
        circle  = values['button_circle']
        triangle  = values['button_triangle']

        PS  = values['button_ps'] 

        # hat directions could be reversed from previous version
        hat = [ values["dpad_up"] - values["dpad_down"],
               values["dpad_right"] - values["dpad_left"] ]

        reset = (PS == 1) and (triangle == 1)
        reset_dock = (PS==1) and (square ==1)
        
        target_vel = {"x": l_side,
                  "y": l_forward,
                  "z": (r_trigger - l_trigger)/2,
                  "yaw": r_side,
                  "pitch": r_forward,
                  "roll": (r_shoulder - l_shoulder),
                  "grip": cross - square,
                  "hat": hat,
                  "reset": reset,
                  "resetdock":reset_dock,
                  "trueXYZ": circle,
                  "dock": triangle}

        print(target_vel)
        arm_pub.send(target_vel)
    elif mode == MODES.SAFE:
        # random stuff to demo color features
        triangle = values['button_triangle']
        square = values['button_square']

        j.rumble(small = 255*triangle, big = 255*square)

        r2 = values['r2_analog']
        r2 = j.map( r2, -1, 1, 0 ,255)
        j.led_color( green = 255, blue = r2)

    else:
        pass

    time.sleep(0.1)
