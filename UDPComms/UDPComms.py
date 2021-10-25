
import socket
import struct
from collections import namedtuple
from time import monotonic
import msgpack
import time

timeout = socket.timeout

MAX_SIZE = 65507

class Publisher:
    def __init__(self, port_tx,port):
        """ Create a Publisher Object

        Arguments:
            port         -- the port to publish the messages on
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.des_address = ("127.0.0.1",port_tx)
        self.sock.bind(("127.0.0.1", port))
        self.sock.settimeout(0.2)

    def send(self, obj):
        """ Publish a message. The obj can be any nesting of standard python types """
        msg = msgpack.dumps(obj, use_bin_type=False)
        assert len(msg) < MAX_SIZE, "Encoded message too big!"
        self.sock.sendto(msg,self.des_address)

    def __del__(self):
        self.sock.close()


class Subscriber:
    def __init__(self, port_rx, timeout=0.2):
        """ Create a Subscriber Object

        Arguments:
            port         -- the port to listen to messages on
            timeout      -- how long to wait before a message is considered out of date
        """
        self.max_size = MAX_SIZE
        self.timeout = timeout

        self.last_data = None
        self.last_time = float('-inf')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.settimeout(timeout)
        self.sock.bind(("127.0.0.1", port_rx))

    def recv(self):
        """ Receive a single message from the socket buffer. It blocks for up to timeout seconds.
        If no message is received before timeout it raises a UDPComms.timeout exception"""

        try:
            self.last_data, address = self.sock.recvfrom(3)
        except BlockingIOError:
            raise socket.timeout("no messages in buffer and called with timeout = 0")
        print(self.last_data)
        self.last_time = monotonic()
        return msgpack.loads(self.last_data, raw=False)
    def get(self):
        """ Returns the latest message it can without blocking. If the latest massage is 
            older then timeout seconds it raises a UDPComms.timeout exception"""
        try:
            self.sock.settimeout(0)
            while True:
                self.last_data, address = self.sock.recvfrom(self.max_size)
                self.last_time = monotonic()
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        current_time = monotonic()
        if (current_time - self.last_time) < self.timeout:
            return msgpack.loads(self.last_data, raw=False)
        else:
            raise socket.timeout("timeout=" + str(self.timeout) + \
                                 ", last message time=" + str(self.last_time) + \
                                 ", current time=" + str(current_time))

    def get_list(self):
        """ Returns list of messages, in the order they were received"""
        msg_bufer = []
        try:
            self.sock.settimeout(0)
            while True:
                self.last_data, address = self.sock.recvfrom(self.max_size)
                self.last_time = monotonic()
                msg = msgpack.loads(self.last_data, raw=False)
                msg_bufer.append(msg)
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        return msg_bufer

    def __del__(self):
        self.sock.close()

class Subscriber:
    def __init__(self, port, timeout=0.2):
        """ Create a Subscriber Object

        Arguments:
            port         -- the port to listen to messages on
            timeout      -- how long to wait before a message is considered out of date
        """
        self.max_size = MAX_SIZE

        self.port = port
        self.timeout = timeout

        self.last_data = None
        self.last_time = float('-inf')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.sock.settimeout(timeout)
        self.sock.bind(("", port))

    def recv(self):
        """ Receive a single message from the socket buffer. It blocks for up to timeout seconds.
        If no message is received before timeout it raises a UDPComms.timeout exception"""

        try:
            self.last_data, address = self.sock.recvfrom(self.max_size)
        except BlockingIOError:
            raise socket.timeout("no messages in buffer and called with timeout = 0")

        self.last_time = monotonic()
        return msgpack.loads(self.last_data, raw=False)

    def get(self):
        """ Returns the latest message it can without blocking. If the latest massage is 
            older then timeout seconds it raises a UDPComms.timeout exception"""
        try:
            self.sock.settimeout(0)
            while True:
                self.last_data, address = self.sock.recvfrom(self.max_size)
                self.last_time = monotonic()
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        current_time = monotonic()
        if (current_time - self.last_time) < self.timeout:
            return msgpack.loads(self.last_data, raw=False)
        else:
            raise socket.timeout("timeout=" + str(self.timeout) + \
                                 ", last message time=" + str(self.last_time) + \
                                 ", current time=" + str(current_time))

    def get_list(self):
        """ Returns list of messages, in the order they were received"""
        msg_bufer = []
        try:
            self.sock.settimeout(0)
            while True:
                self.last_data, address = self.sock.recvfrom(self.max_size)
                self.last_time = monotonic()
                msg = msgpack.loads(self.last_data, raw=False)
                msg_bufer.append(msg)
        except socket.error:
            pass
        finally:
            self.sock.settimeout(self.timeout)

        return msg_bufer

    def __del__(self):
        self.sock.close()


if __name__ == "__main__":
    msg = 'very important data'

    a = Publisher(1000)
    a.send( {"text": "magic", "number":5.5, "bool":False} )

