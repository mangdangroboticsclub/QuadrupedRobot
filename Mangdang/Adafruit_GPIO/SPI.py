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

import operator
import time

import Mangdang.Adafruit_GPIO as GPIO


MSBFIRST = 0
LSBFIRST = 1


class SpiDev(object):
    """Hardware-based SPI implementation using the spidev interface."""

    def __init__(self, port, device, max_speed_hz=500000):
        """Initialize an SPI device using the SPIdev interface.  Port and device
        identify the device, for example the device /dev/spidev1.0 would be port
        1 and device 0.
        """
        import spidev
        self._device = spidev.SpiDev()
        self._device.open(port, device)
        self._device.max_speed_hz=max_speed_hz
        # Default to mode 0, and make sure CS is active low.
        self._device.mode = 0
        #self._device.cshigh = False

    def set_clock_hz(self, hz):
        """Set the speed of the SPI clock in hertz.  Note that not all speeds
        are supported and a lower speed might be chosen by the hardware.
        """
        self._device.max_speed_hz=hz

    def set_mode(self, mode):
        """Set SPI mode which controls clock polarity and phase.  Should be a
        numeric value 0, 1, 2, or 3.  See wikipedia page for details on meaning:
        http://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus
        """
        if mode < 0 or mode > 3:
            raise ValueError('Mode must be a value 0, 1, 2, or 3.')
        self._device.mode = mode

    def set_bit_order(self, order):
        """Set order of bits to be read/written over serial lines.  Should be
        either MSBFIRST for most-significant first, or LSBFIRST for
        least-signifcant first.
        """
        if order == MSBFIRST:
            self._device.lsbfirst = False
        elif order == LSBFIRST:
            self._device.lsbfirst = True
        else:
            raise ValueError('Order must be MSBFIRST or LSBFIRST.')

    def close(self):
        """Close communication with the SPI device."""
        self._device.close()

    def write(self, data):
        """Half-duplex SPI write.  The specified array of bytes will be clocked
        out the MOSI line.
        """
        self._device.writebytes(data)

    def read(self, length):
        """Half-duplex SPI read.  The specified length of bytes will be clocked
        in the MISO line and returned as a bytearray object.
        """
        return bytearray(self._device.readbytes(length))

    def transfer(self, data):
        """Full-duplex SPI read and write.  The specified array of bytes will be
        clocked out the MOSI line, while simultaneously bytes will be read from
        the MISO line.  Read bytes will be returned as a bytearray object.
        """
        return bytearray(self._device.xfer2(data))

class SpiDevMraa(object):
    """Hardware SPI implementation with the mraa library on Minnowboard"""
    def __init__(self, port, device, max_speed_hz=500000):
        import mraa
        self._device = mraa.Spi(0)
        self._device.mode(0)
        
    def set_clock_hz(self, hz):
        """Set the speed of the SPI clock in hertz.  Note that not all speeds
        are supported and a lower speed might be chosen by the hardware.
        """
        self._device.frequency(hz)

    def set_mode(self,mode):
        """Set SPI mode which controls clock polarity and phase.  Should be a
        numeric value 0, 1, 2, or 3.  See wikipedia page for details on meaning:
        http://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus
        """
        if mode < 0 or mode > 3:
            raise ValueError('Mode must be a value 0, 1, 2, or 3.')
        self._device.mode(mode)

    def set_bit_order(self, order):
        """Set order of bits to be read/written over serial lines.  Should be
        either MSBFIRST for most-significant first, or LSBFIRST for
        least-signifcant first.
        """
        if order == MSBFIRST:
            self._device.lsbmode(False)
        elif order == LSBFIRST:
            self._device.lsbmode(True)
        else:
            raise ValueError('Order must be MSBFIRST or LSBFIRST.')
        
    def close(self):
        """Close communication with the SPI device."""
        self._device.Spi()

    def write(self, data):
        """Half-duplex SPI write.  The specified array of bytes will be clocked
        out the MOSI line.
        """
        self._device.write(bytearray(data))

class BitBang(object):
    """Software-based implementation of the SPI protocol over GPIO pins."""

    def __init__(self, gpio, sclk, mosi=None, miso=None, ss=None):
        """Initialize bit bang (or software) based SPI.  Must provide a BaseGPIO
        class, the SPI clock, and optionally MOSI, MISO, and SS (slave select)
        pin numbers. If MOSI is set to None then writes will be disabled and fail
        with an error, likewise for MISO reads will be disabled.  If SS is set to
        None then SS will not be asserted high/low by the library when
        transfering data.
        """
        self._gpio = gpio
        self._sclk = sclk
        self._mosi = mosi
        self._miso = miso
        self._ss = ss
        # Set pins as outputs/inputs.
        gpio.setup(sclk, GPIO.OUT)
        if mosi is not None:
            gpio.setup(mosi, GPIO.OUT)
        if miso is not None:
            gpio.setup(miso, GPIO.IN)
        if ss is not None:
            gpio.setup(ss, GPIO.OUT)
            # Assert SS high to start with device communication off.
            gpio.set_high(ss)
        # Assume mode 0.
        self.set_mode(0)
        # Assume most significant bit first order.
        self.set_bit_order(MSBFIRST)

    def set_clock_hz(self, hz):
        """Set the speed of the SPI clock.  This is unsupported with the bit
        bang SPI class and will be ignored.
        """
        pass

    def set_mode(self, mode):
        """Set SPI mode which controls clock polarity and phase.  Should be a
        numeric value 0, 1, 2, or 3.  See wikipedia page for details on meaning:
        http://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus
        """
        if mode < 0 or mode > 3:
            raise ValueError('Mode must be a value 0, 1, 2, or 3.')
        if mode & 0x02:
            # Clock is normally high in mode 2 and 3.
            self._clock_base = GPIO.HIGH
        else:
            # Clock is normally low in mode 0 and 1.
            self._clock_base = GPIO.LOW
        if mode & 0x01:
            # Read on trailing edge in mode 1 and 3.
            self._read_leading = False
        else:
            # Read on leading edge in mode 0 and 2.
            self._read_leading = True
        # Put clock into its base state.
        self._gpio.output(self._sclk, self._clock_base)

    def set_bit_order(self, order):
        """Set order of bits to be read/written over serial lines.  Should be
        either MSBFIRST for most-significant first, or LSBFIRST for
        least-signifcant first.
        """
        # Set self._mask to the bitmask which points at the appropriate bit to
        # read or write, and appropriate left/right shift operator function for
        # reading/writing.
        if order == MSBFIRST:
            self._mask = 0x80
            self._write_shift = operator.lshift
            self._read_shift = operator.rshift
        elif order == LSBFIRST:
            self._mask = 0x01
            self._write_shift = operator.rshift
            self._read_shift = operator.lshift
        else:
            raise ValueError('Order must be MSBFIRST or LSBFIRST.')

    def close(self):
        """Close the SPI connection.  Unused in the bit bang implementation."""
        pass

    def write(self, data, assert_ss=True, deassert_ss=True):
        """Half-duplex SPI write.  If assert_ss is True, the SS line will be
        asserted low, the specified bytes will be clocked out the MOSI line, and
        if deassert_ss is True the SS line be put back high.
        """
        # Fail MOSI is not specified.
        if self._mosi is None:
            raise RuntimeError('Write attempted with no MOSI pin specified.')
        if assert_ss and self._ss is not None:
            self._gpio.set_low(self._ss)
        for byte in data:
            for i in range(8):
                # Write bit to MOSI.
                if self._write_shift(byte, i) & self._mask:
                    self._gpio.set_high(self._mosi)
                else:
                    self._gpio.set_low(self._mosi)
                # Flip clock off base.
                self._gpio.output(self._sclk, not self._clock_base)
                # Return clock to base.
                self._gpio.output(self._sclk, self._clock_base)
        if deassert_ss and self._ss is not None:
            self._gpio.set_high(self._ss)

    def read(self, length, assert_ss=True, deassert_ss=True):
        """Half-duplex SPI read.  If assert_ss is true, the SS line will be
        asserted low, the specified length of bytes will be clocked in the MISO
        line, and if deassert_ss is true the SS line will be put back high.
        Bytes which are read will be returned as a bytearray object.
        """
        if self._miso is None:
            raise RuntimeError('Read attempted with no MISO pin specified.')
        if assert_ss and self._ss is not None:
            self._gpio.set_low(self._ss)
        result = bytearray(length)
        for i in range(length):
            for j in range(8):
                # Flip clock off base.
                self._gpio.output(self._sclk, not self._clock_base)
                # Handle read on leading edge of clock.
                if self._read_leading:
                    if self._gpio.is_high(self._miso):
                        # Set bit to 1 at appropriate location.
                        result[i] |= self._read_shift(self._mask, j)
                    else:
                        # Set bit to 0 at appropriate location.
                        result[i] &= ~self._read_shift(self._mask, j)
                # Return clock to base.
                self._gpio.output(self._sclk, self._clock_base)
                # Handle read on trailing edge of clock.
                if not self._read_leading:
                    if self._gpio.is_high(self._miso):
                        # Set bit to 1 at appropriate location.
                        result[i] |= self._read_shift(self._mask, j)
                    else:
                        # Set bit to 0 at appropriate location.
                        result[i] &= ~self._read_shift(self._mask, j)
        if deassert_ss and self._ss is not None:
            self._gpio.set_high(self._ss)
        return result

    def transfer(self, data, assert_ss=True, deassert_ss=True):
        """Full-duplex SPI read and write.  If assert_ss is true, the SS line
        will be asserted low, the specified bytes will be clocked out the MOSI
        line while bytes will also be read from the MISO line, and if
        deassert_ss is true the SS line will be put back high.  Bytes which are
        read will be returned as a bytearray object.
        """
        if self._mosi is None:
            raise RuntimeError('Write attempted with no MOSI pin specified.')
        if self._miso is None:
            raise RuntimeError('Read attempted with no MISO pin specified.')
        if assert_ss and self._ss is not None:
            self._gpio.set_low(self._ss)
        result = bytearray(len(data))
        for i in range(len(data)):
            for j in range(8):
                # Write bit to MOSI.
                if self._write_shift(data[i], j) & self._mask:
                    self._gpio.set_high(self._mosi)
                else:
                    self._gpio.set_low(self._mosi)
                # Flip clock off base.
                self._gpio.output(self._sclk, not self._clock_base)
                # Handle read on leading edge of clock.
                if self._read_leading:
                    if self._gpio.is_high(self._miso):
                        # Set bit to 1 at appropriate location.
                        result[i] |= self._read_shift(self._mask, j)
                    else:
                        # Set bit to 0 at appropriate location.
                        result[i] &= ~self._read_shift(self._mask, j)
                # Return clock to base.
                self._gpio.output(self._sclk, self._clock_base)
                # Handle read on trailing edge of clock.
                if not self._read_leading:
                    if self._gpio.is_high(self._miso):
                        # Set bit to 1 at appropriate location.
                        result[i] |= self._read_shift(self._mask, j)
                    else:
                        # Set bit to 0 at appropriate location.
                        result[i] &= ~self._read_shift(self._mask, j)
        if deassert_ss and self._ss is not None:
            self._gpio.set_high(self._ss)
        return result
