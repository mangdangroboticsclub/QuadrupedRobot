import wiringpi
import ctypes
import numpy as np
import time

def filter_deabnormal(data_new,data_last):
    ''' deabnormal filter, remove the abnormal value.

		Parameter:
		data_new : the new IMU data
		data_last: the last IMU data

		Return:
		data_normal: the IMU data that have remove abnormal value
	'''
    data_normal = data_new
    for index in range(4):
        if abs(data_new[index] - data_last[index])>1:
            data_normal[index] = data_last[index]
    return data_normal

def filter_lowpass(data_new,data_last):
    ''' low pass filter.

		Parameter:
		data_new : the new IMU data
		data_last: the last IMU data

		Return:
		data_lowpass: the low frequencey IMU data
	'''
    data_lowpass = data_new

    for index in range(4):
        data_lowpass[index] = data_last[index]*0.8 + data_new[index]*0.2
    return data_lowpass

class IMU:
    def __init__(self, addr=0x4A):
        self.bno080 = ctypes.CDLL('/home/pi/QuadrupedRobot/Mangdang/IMU/library/libbno080.so')

        self.bno080.IMU_getQuatI.restype = ctypes.c_float
        self.bno080.IMU_getQuatJ.restype = ctypes.c_float
        self.bno080.IMU_getQuatK.restype = ctypes.c_float
        self.bno080.IMU_getQuatReal.restype = ctypes.c_float

        self.i2c = wiringpi.wiringPiI2CSetupInterface("/dev/i2c-3", addr)
        self.last_quat = np.array([1, 0, 0, 0])
        self.start_time = time.time()

    def begin(self):
        self.bno080.IMU_begin(self.i2c)
        self.bno080.IMU_enableRotationVector(self.i2c, 10)

    def read_orientation(self):
        """Reads quaternion measurements from the Teensy . Returns the read quaternion.

                Parameters
                ----------
                bno080 : BNO080 object
                    Handle to the pyserial Serial object

                Returns
                -------
                np array (4,)
                    If there was quaternion data to read on the I2C port returns the quaternion as a numpy array, otherwise returns the last read quaternion.
                """
        self.start_time = time.time()
        while True:
            if self.bno080.IMU_dataAvailable(self.i2c):
                quat = [self.bno080.IMU_getQuatReal(), self.bno080.IMU_getQuatI(), self.bno080.IMU_getQuatJ(), self.bno080.IMU_getQuatK()]
                if quat != [0, 0, 0, 0]:
                    new_quat = np.array(quat, dtype=np.float64)
                    normal_quat = filter_deabnormal(new_quat,self.last_quat)
                    lp_quat = filter_lowpass(normal_quat,self.last_quat)
                    self.last_quat = lp_quat
                    self.start_time = time.time()
                    return self.last_quat
                if (time.time() - self.start_time) > 0.005:
                    return self.last_quat
            else:
                if(time.time()-self.start_time) > 0.005:
                    return self.last_quat
                print("quaternion data is not available")

