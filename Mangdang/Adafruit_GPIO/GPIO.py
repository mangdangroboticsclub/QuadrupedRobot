# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import Adafruit_GPIO.Platform as Platform


OUT     = 0
IN      = 1
HIGH    = True
LOW     = False

RISING      = 1
FALLING     = 2
BOTH        = 3

PUD_OFF  = 0
PUD_DOWN = 1
PUD_UP   = 2

class BaseGPIO(object):
    """Base class for implementing simple digital IO for a platform.
    Implementors are expected to subclass from this and provide an implementation
    of the setup, output, and input functions."""

    def setup(self, pin, mode, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUT or IN."""
        raise NotImplementedError

    def output(self, pin, value):
        """Set the specified pin the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high)."""
        raise NotImplementedError

    def input(self, pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low."""
        raise NotImplementedError

    def set_high(self, pin):
        """Set the specified pin HIGH."""
        self.output(pin, HIGH)

    def set_low(self, pin):
        """Set the specified pin LOW."""
        self.output(pin, LOW)

    def is_high(self, pin):
        """Return true if the specified pin is pulled high."""
        return self.input(pin) == HIGH

    def is_low(self, pin):
        """Return true if the specified pin is pulled low."""
        return self.input(pin) == LOW


# Basic implementation of multiple pin methods just loops through pins and
# processes each one individually. This is not optimal, but derived classes can
# provide a more optimal implementation that deals with groups of pins
# simultaneously.
# See MCP230xx or PCF8574 classes for examples of optimized implementations.

    def output_pins(self, pins):
        """Set multiple pins high or low at once.  Pins should be a dict of pin
        name to pin value (HIGH/True for 1, LOW/False for 0).  All provided pins
        will be set to the given values.
        """
        # General implementation just loops through pins and writes them out
        # manually.  This is not optimized, but subclasses can choose to implement
        # a more optimal batch output implementation.  See the MCP230xx class for
        # example of optimized implementation.
        for pin, value in iter(pins.items()):
            self.output(pin, value)

    def setup_pins(self, pins):
        """Setup multiple pins as inputs or outputs at once.  Pins should be a
        dict of pin name to pin type (IN or OUT).
        """
        # General implementation that can be optimized by derived classes.
        for pin, value in iter(pins.items()):
            self.setup(pin, value)

    def input_pins(self, pins):
        """Read multiple pins specified in the given list and return list of pin values
        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if pulled low.
        """
        # General implementation that can be optimized by derived classes.
        return [self.input(pin) for pin in pins]


    def add_event_detect(self, pin, edge):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.
        """
        raise NotImplementedError
   
    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        raise NotImplementedError
  
    def add_event_callback(self, pin, callback):
        """Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.
        """
        raise NotImplementedError

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.  You need to 
        enable edge detection using add_event_detect() first.   Pin should be 
        type IN.
        """
        raise NotImplementedError

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH."""
        raise NotImplementedError

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none 
        is specified.
        """
        raise NotImplementedError


# helper functions useful to derived classes

    def _validate_pin(self, pin):
        # Raise an exception if pin is outside the range of allowed values.
        if pin < 0 or pin >= self.NUM_GPIO:
            raise ValueError('Invalid GPIO value, must be between 0 and {0}.'.format(self.NUM_GPIO))

    def _bit2(self, src, bit, val):
        bit = 1 << bit
        return (src | bit) if val else (src & ~bit)


class RPiGPIOAdapter(BaseGPIO):
    """GPIO implementation for the Raspberry Pi using the RPi.GPIO library."""

    def __init__(self, rpi_gpio, mode=None):
        self.rpi_gpio = rpi_gpio
        # Suppress warnings about GPIO in use.
        rpi_gpio.setwarnings(False)
        # Setup board pin mode.
        if mode == rpi_gpio.BOARD or mode == rpi_gpio.BCM:
            rpi_gpio.setmode(mode)
        elif mode is not None:
            raise ValueError('Unexpected value for mode.  Must be BOARD or BCM.')
        else:
            # Default to BCM numbering if not told otherwise.
            rpi_gpio.setmode(rpi_gpio.BCM)
        # Define mapping of Adafruit GPIO library constants to RPi.GPIO constants.
        self._dir_mapping = { OUT:      rpi_gpio.OUT,
                              IN:       rpi_gpio.IN }
        self._pud_mapping = { PUD_OFF:  rpi_gpio.PUD_OFF,
                              PUD_DOWN: rpi_gpio.PUD_DOWN,
                              PUD_UP:   rpi_gpio.PUD_UP }
        self._edge_mapping = { RISING:  rpi_gpio.RISING,
                               FALLING: rpi_gpio.FALLING,
                               BOTH:    rpi_gpio.BOTH }

    def setup(self, pin, mode, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUTPUT or INPUT.
        """
        self.rpi_gpio.setup(pin, self._dir_mapping[mode],
                            pull_up_down=self._pud_mapping[pull_up_down])

    def output(self, pin, value):
        """Set the specified pin the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high).
        """
        self.rpi_gpio.output(pin, value)

    def input(self, pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self.rpi_gpio.input(pin)

    def input_pins(self, pins):
        """Read multiple pins specified in the given list and return list of pin values
        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if pulled low.
        """
        # maybe rpi has a mass read...  it would be more efficient to use it if it exists
        return [self.rpi_gpio.input(pin) for pin in pins]

    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.  Callback is a
        function for the event.  Bouncetime is switch bounce timeout in ms for
        callback
        """
        kwargs = {}
        if callback:
            kwargs['callback']=callback
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.rpi_gpio.add_event_detect(pin, self._edge_mapping[edge], **kwargs)

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        self.rpi_gpio.remove_event_detect(pin)

    def add_event_callback(self, pin, callback):
        """Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.
        """
        self.rpi_gpio.add_event_callback(pin, callback)

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.  You need to 
        enable edge detection using add_event_detect() first.   Pin should be
        type IN.
        """
        return self.rpi_gpio.event_detected(pin)

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING,
        FALLING or BOTH.
        """
        self.rpi_gpio.wait_for_edge(pin, self._edge_mapping[edge])

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none 
        is specified.
        """
        if pin is None:
            self.rpi_gpio.cleanup()
        else:
            self.rpi_gpio.cleanup(pin)

class AdafruitBBIOAdapter(BaseGPIO):
    """GPIO implementation for the Beaglebone Black using the Adafruit_BBIO
    library.
    """

    def __init__(self, bbio_gpio):
        self.bbio_gpio = bbio_gpio
        # Define mapping of Adafruit GPIO library constants to RPi.GPIO constants.
        self._dir_mapping = { OUT:      bbio_gpio.OUT,
                              IN:       bbio_gpio.IN }
        self._pud_mapping = { PUD_OFF:  bbio_gpio.PUD_OFF,
                              PUD_DOWN: bbio_gpio.PUD_DOWN,
                              PUD_UP:   bbio_gpio.PUD_UP }
        self._edge_mapping = { RISING:  bbio_gpio.RISING,
                               FALLING: bbio_gpio.FALLING,
                               BOTH:    bbio_gpio.BOTH }

    def setup(self, pin, mode, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUTPUT or INPUT.
        """
        self.bbio_gpio.setup(pin, self._dir_mapping[mode],
                             pull_up_down=self._pud_mapping[pull_up_down])

    def output(self, pin, value):
        """Set the specified pin the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high).
        """
        self.bbio_gpio.output(pin, value)

    def input(self, pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self.bbio_gpio.input(pin)

    def input_pins(self, pins):
        """Read multiple pins specified in the given list and return list of pin values
        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if pulled low.
        """
        # maybe bbb has a mass read...  it would be more efficient to use it if it exists
        return [self.bbio_gpio.input(pin) for pin in pins]

    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.  Callback is a
        function for the event.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        kwargs = {}
        if callback:
            kwargs['callback']=callback
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.bbio_gpio.add_event_detect(pin, self._edge_mapping[edge], **kwargs)

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        self.bbio_gpio.remove_event_detect(pin)

    def add_event_callback(self, pin, callback, bouncetime=-1):
        """Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        kwargs = {}
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.bbio_gpio.add_event_callback(pin, callback, **kwargs)

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.  You need to 
        enable edge detection using add_event_detect() first.   Pin should be 
        type IN.
        """
        return self.bbio_gpio.event_detected(pin)

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH.
        """
        self.bbio_gpio.wait_for_edge(pin, self._edge_mapping[edge])

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none 
        is specified.
        """
        if pin is None:
            self.bbio_gpio.cleanup()
        else:
            self.bbio_gpio.cleanup(pin)

class AdafruitMinnowAdapter(BaseGPIO):
    """GPIO implementation for the Minnowboard + MAX using the mraa library"""
    
    def __init__(self,mraa_gpio):
        self.mraa_gpio = mraa_gpio
        # Define mapping of Adafruit GPIO library constants to mraa constants
        self._dir_mapping = { OUT:      self.mraa_gpio.DIR_OUT,
                              IN:       self.mraa_gpio.DIR_IN }
        self._pud_mapping = { PUD_OFF:  self.mraa_gpio.MODE_STRONG,
                              PUD_UP:   self.mraa_gpio.MODE_HIZ,
                              PUD_DOWN: self.mraa_gpio.MODE_PULLDOWN }
        self._edge_mapping = { RISING:   self.mraa_gpio.EDGE_RISING,
                              FALLING:  self.mraa_gpio.EDGE_FALLING,
                              BOTH:     self.mraa_gpio.EDGE_BOTH }

    def setup(self,pin,mode):
        """Set the input or output mode for a specified pin.  Mode should be
        either DIR_IN or DIR_OUT.
        """
        self.mraa_gpio.Gpio.dir(self.mraa_gpio.Gpio(pin),self._dir_mapping[mode])   

    def output(self,pin,value):
        """Set the specified pin the provided high/low value.  Value should be
        either 1 (ON or HIGH), or 0 (OFF or LOW) or a boolean.
        """
        self.mraa_gpio.Gpio.write(self.mraa_gpio.Gpio(pin), value)
    
    def input(self,pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self.mraa_gpio.Gpio.read(self.mraa_gpio.Gpio(pin))    
    
    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.  Callback is a
        function for the event.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        kwargs = {}
        if callback:
            kwargs['callback']=callback
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.mraa_gpio.Gpio.isr(self.mraa_gpio.Gpio(pin), self._edge_mapping[edge], **kwargs)

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        self.mraa_gpio.Gpio.isrExit(self.mraa_gpio.Gpio(pin))

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH.
        """
        self.bbio_gpio.wait_for_edge(self.mraa_gpio.Gpio(pin), self._edge_mapping[edge])

def get_platform_gpio(**keywords):
    """Attempt to return a GPIO instance for the platform which the code is being
    executed on.  Currently supports only the Raspberry Pi using the RPi.GPIO
    library and Beaglebone Black using the Adafruit_BBIO library.  Will throw an
    exception if a GPIO instance can't be created for the current platform.  The
    returned GPIO object is an instance of BaseGPIO.
    """
    plat = Platform.platform_detect()
    if plat == Platform.RASPBERRY_PI:
        import RPi.GPIO
        return RPiGPIOAdapter(RPi.GPIO, **keywords)
    elif plat == Platform.BEAGLEBONE_BLACK:
        import Adafruit_BBIO.GPIO
        return AdafruitBBIOAdapter(Adafruit_BBIO.GPIO, **keywords)
    elif plat == Platform.MINNOWBOARD:
        import mraa
        return AdafruitMinnowAdapter(mraa, **keywords)
    elif plat == Platform.JETSON_NANO:
        import Jetson.GPIO
        return RPiGPIOAdapter(Jetson.GPIO, **keywords)
    elif plat == Platform.UNKNOWN:
        raise RuntimeError('Could not determine platform.')
