import board
import busio
import numpy as np
import time
import RPi.GPIO as GPIO
from Mangdang.IMU.i2c import BNO08X_I2C
from . import BNO_REPORT_ROTATION_VECTOR

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
    def __init__(self):
        self.imu_resetIO = 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.imu_resetIO, GPIO.OUT)
        GPIO.output(self.imu_resetIO, 1)

        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        time.sleep(0.2)
        self.imu = BNO08X_I2C(i2c)
        self.last_quat = [1, 0, 0, 0]
        self.reset_IMU = False

    def begin(self):
        self.imu.enable_feature(BNO_REPORT_ROTATION_VECTOR)

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
        try:
            if self.reset_IMU:
                GPIO.output(self.imu_resetIO, 1)
                time.sleep(0.1)
                i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
                self.imu = BNO08X_I2C(i2c)
                time.sleep(0.1)
                self.imu.enable_feature(BNO_REPORT_ROTATION_VECTOR)
                self.reset_IMU = False
                return self.last_quat
            else:
                quat_i, quat_j, quat_k, quat_real = self.imu.quaternion
                quat_orientation = [quat_real, quat_i, quat_j, quat_k]
                new_quat = np.array(quat_orientation, dtype=np.float64)
                normal_quat = filter_deabnormal(new_quat, self.last_quat)
                lp_quat = filter_lowpass(normal_quat, self.last_quat)
                self.last_quat = lp_quat
                return self.last_quat
        except:
            GPIO.output(self.imu_resetIO, 0)
            self.reset_IMU = True
            time.sleep(0.05)
            return self.last_quat
