
import sys
import time
import subprocess
import math

from threading import Thread
from collections import OrderedDict, deque

from ds4drv.actions import ActionRegistry
from ds4drv.backends import BluetoothBackend, HidrawBackend
from ds4drv.config import load_options
from ds4drv.daemon import Daemon
from ds4drv.eventloop import EventLoop
from ds4drv.exceptions import BackendError
from ds4drv.action import ReportAction

from ds4drv.__main__ import create_controller_thread


class ActionShim(ReportAction):
    """ intercepts the joystick report"""

    def __init__(self, *args, **kwargs):
        super(ActionShim, self).__init__(*args, **kwargs)
        self.timer = self.create_timer(0.02, self.intercept)
        self.values = None
        self.timestamps = deque(range(10), maxlen=10)

    def enable(self):
        self.timer.start()

    def disable(self):
        self.timer.stop()
        self.values = None

    def load_options(self, options):
        pass

    def deadzones(self,values):
        deadzone = 0.14
        if math.sqrt( values['left_analog_x'] ** 2  + values['left_analog_y'] ** 2) < deadzone:
            values['left_analog_y'] = 0.0
            values['left_analog_x'] = 0.0
        if math.sqrt( values['right_analog_x'] ** 2 + values['right_analog_y'] ** 2) < deadzone:
            values['right_analog_y'] = 0.0
            values['right_analog_x'] = 0.0

        return values

    def intercept(self, report):
        new_out = OrderedDict()
        for key in report.__slots__:
            value = getattr(report, key)
            new_out[key] = value

        for key in ["left_analog_x", "left_analog_y", 
                    "right_analog_x", "right_analog_y", 
                    "l2_analog", "r2_analog"]:
            new_out[key] =  2*( new_out[key]/255 )  - 1

        new_out = self.deadzones(new_out)

        self.timestamps.append(new_out['timestamp'])
        if len(set(self.timestamps)) <= 1:
            self.values = None
        else:
            self.values = new_out

        return True

class Joystick:
    def __init__(self):
        self.thread = None

        options = load_options()

        if options.hidraw:
            raise ValueError("HID mode not supported")
            backend = HidrawBackend(Daemon.logger)
        else:
            subprocess.run(["hciconfig", "hciX", "up"])
            backend = BluetoothBackend(Daemon.logger)

        backend.setup()

        self.thread = create_controller_thread(1, options.controllers[0])

        self.thread.controller.setup_device(next(backend.devices))

        self.shim = ActionShim(self.thread.controller)
        self.thread.controller.actions.append(self.shim)
        self.shim.enable()

        self._color = (None, None, None)
        self._rumble = (None, None)
        self._flash = (None, None)

        # ensure we get a value before returning
        while self.shim.values is None:
            pass

    def close(self):
        if self.thread is None:
            return
        self.thread.controller.exit("Cleaning up...")
        self.thread.controller.loop.stop()

    def __del__(self):
        self.close()

    @staticmethod
    def map(val, in_min, in_max, out_min, out_max):
        """ helper static method that helps with rescaling """
        in_span = in_max - in_min
        out_span = out_max - out_min

        value_scaled = float(val - in_min) / float(in_span)
        value_mapped = (value_scaled * out_span) + out_min

        if value_mapped < out_min:
            value_mapped = out_min

        if value_mapped > out_max:
            value_mapped = out_max

        return value_mapped

    def get_input(self):
        """ returns ordered dict with state of all inputs """
        if self.thread.controller.error:
            raise IOError("Encountered error with controller")
        if self.shim.values is None:
            raise TimeoutError("Joystick hasn't updated values in last 200ms")

        return self.shim.values

    def led_color(self, red=0, green=0, blue=0):
        """ set RGB color in range 0-255"""
        color = (int(red),int(green),int(blue))
        if( self._color == color ):
            return
        self._color = color
        self.thread.controller.device.set_led( *self._color )

    def rumble(self, small=0, big=0):
        """ rumble in range 0-255 """
        rumble = (int(small),int(big))
        if( self._rumble == rumble ):
            return
        self._rumble = rumble
        self.thread.controller.device.rumble( *self._rumble )

    def led_flash(self, on=0, off=0):
        """ flash led: on and off times in range 0 - 255 """
        flash = (int(on),int(off))
        if( self._flash == flash ):
            return
        self._flash = flash

        if( self._flash == (0,0) ):
            self.thread.controller.device.stop_led_flash()
        else:
            self.thread.controller.device.start_led_flash( *self._flash )


if __name__ == "__main__":
    j = Joystick()
    while 1:
        for key, value in j.get_input().items():
            print(key,value)
        print()

        time.sleep(0.1)
