# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""

    Subclass of `IMU.BNO08X` to use I2C

"""
from struct import pack_into
import adafruit_bus_device.i2c_device as i2c_device
from . import BNO08X, DATA_BUFFER_SIZE, const, Packet, PacketError

_BNO08X_DEFAULT_ADDRESS = const(0x4A)


class BNO08X_I2C(BNO08X):
    """Library for the BNO08x IMUs from Hillcrest Laboratories

        :param ~busio.I2C i2c_bus: The I2C bus the BNO08x is connected to.

    """

    def __init__(
        self, i2c_bus, reset=None, address=_BNO08X_DEFAULT_ADDRESS, debug=False
    ):
        self.bus_device_obj = i2c_device.I2CDevice(i2c_bus, address)
        super().__init__(reset, debug)

    def _send_packet(self, channel, data):
        data_length = len(data)
        write_length = data_length + 4

        pack_into("<H", self._data_buffer, 0, write_length)
        self._data_buffer[2] = channel
        self._data_buffer[3] = self._sequence_number[channel]
        for idx, send_byte in enumerate(data):
            self._data_buffer[4 + idx] = send_byte
        packet = Packet(self._data_buffer)
        self._dbg("Sending packet:")
        self._dbg(packet)
        with self.bus_device_obj as i2c:
            i2c.write(self._data_buffer, end=write_length)

        self._sequence_number[channel] = (self._sequence_number[channel] + 1) % 256
        return self._sequence_number[channel]

    # returns true if available data was read
    # the sensor will always tell us how much there is, so no need to track it ourselves

    def _read_header(self):
        """Reads the first 4 bytes available as a header"""
        with self.bus_device_obj as i2c:
            i2c.readinto(self._data_buffer, end=4)  # this is expecting a header
        packet_header = Packet.header_from_buffer(self._data_buffer)
        self._dbg(packet_header)
        return packet_header

    def _read_packet(self):
        with self.bus_device_obj as i2c:
            i2c.readinto(self._data_buffer, end=4)  # this is expecting a header?
        self._dbg("")
        # print("SHTP READ packet header: ", [hex(x) for x in self._data_buffer[0:4]])

        header = Packet.header_from_buffer(self._data_buffer)
        packet_byte_count = header.packet_byte_count
        channel_number = header.channel_number
        sequence_number = header.sequence_number

        self._sequence_number[channel_number] = sequence_number
        if packet_byte_count == 0:
            self._dbg("SKIPPING NO PACKETS AVAILABLE IN i2c._read_packet")
        packet_byte_count -= 4
        self._dbg(
            "channel",
            channel_number,
            "has",
            packet_byte_count,
            "bytes available to read",
        )

        self._read(packet_byte_count)

        new_packet = Packet(self._data_buffer)
        if self._debug:
            print(new_packet)

        self._update_sequence_number(new_packet)

        return new_packet

    # returns true if all requested data was read
    def _read(self, requested_read_length):
        self._dbg("trying to read", requested_read_length, "bytes")
        # +4 for the header
        total_read_length = requested_read_length + 4
        if total_read_length > DATA_BUFFER_SIZE:
            self._data_buffer = bytearray(total_read_length)
            self._dbg(
                "!!!!!!!!!!!! ALLOCATION: increased _data_buffer to bytearray(%d) !!!!!!!!!!!!! "
                % total_read_length
            )
        with self.bus_device_obj as i2c:
            i2c.readinto(self._data_buffer, end=total_read_length)

    @property
    def _data_ready(self):
        header = self._read_header()

        if header.channel_number > 5:
            self._dbg("channel number out of range:", header.channel_number)
        if header.packet_byte_count == 0x7FFF:
            print("Byte count is 0x7FFF/0xFFFF; Error?")
            if header.sequence_number == 0xFF:
                print("Sequence number is 0xFF; Error?")
            ready = False
        else:
            ready = header.data_length > 0

        # self._dbg("\tdata ready", ready)
        return ready
