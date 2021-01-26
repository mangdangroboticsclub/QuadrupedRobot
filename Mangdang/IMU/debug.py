# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""A collection of dictionaries for better debug messages"""
# TODO: Remove for size before release
channels = {
    0x0: "SHTP_COMMAND",
    0x1: "EXE",
    0x2: "CONTROL",
    0x3: "INPUT_SENSOR_REPORTS",
    0x4: "WAKE_INPUT_SENSOR_REPORTS",
    0x5: "GYRO_ROTATION_VECTOR",
}

# Command Response

reports = {
    0xFB: "BASE_TIMESTAMP",
    0xF2: "COMMAND_REQUEST",
    0xF1: "COMMAND_RESPONSE",
    0xF4: "FRS_READ_REQUEST",
    0xF3: "FRS_READ_RESPONSE",
    0xF6: "FRS_WRITE_DATA",
    0xF7: "FRS_WRITE_REQUEST",
    0xF5: "FRS_WRITE_RESPONSE",
    0xFE: "GET_FEATURE_REQUEST",
    0xFC: "GET_FEATURE_RESPONSE",
    0xFD: "SET_FEATURE_COMMAND",
    0xFA: "TIMESTAMP_REBASE",
    0x01: "ACCELEROMETER",
    0x29: "ARVR_STABILIZED_GAME_ROTATION_VECTOR",
    0x28: "ARVR_STABILIZED_ROTATION_VECTOR",
    0x22: "CIRCLE_DETECTOR",
    0x1A: "FLIP_DETECTOR",
    0x08: "GAME_ROTATION_VECTOR",
    0x09: "GEOMAGNETIC_ROTATION_VECTOR",
    0x06: "GRAVITY",
    0x02: "GYROSCOPE",
    0x04: "LINEAR_ACCELERATION",
    0x03: "MAGNETIC_FIELD",
    0x1E: "PERSONAL_ACTIVITY_CLASSIFIER",
    0x1B: "PICKUP_DETECTOR",
    0x21: "POCKET_DETECTOR",
    0xF9: "PRODUCT_ID_REQUEST",
    0xF8: "PRODUCT_ID_RESPONSE",
    0x14: "RAW_ACCELEROMETER",
    0x15: "RAW_GYROSCOPE",
    0x16: "RAW_MAGNETOMETER",
    0x05: "ROTATION_VECTOR",
    0x17: "SAR",
    0x19: "SHAKE_DETECTOR",
    0x12: "SIGNIFICANT_MOTION",
    0x1F: "SLEEP_DETECTOR",
    0x13: "STABILITY_CLASSIFIER",
    0x1C: "STABILITY_DETECTOR",
    0x11: "STEP_COUNTER",
    0x18: "STEP_DETECTOR",
    0x10: "TAP_DETECTOR",
    0x20: "TILT_DETECTOR",
    0x07: "UNCALIBRATED_GYROSCOPE",
    0x0F: "UNCALIBRATED_MAGNETIC_FIELD",
}
# # Gravity (m/s2)
# _BNO_REPORT_GRAVITY = const(0x06) 10 bytes
# # Raw uncalibrated accelerometer data (ADC units). Used for testing
# _BNO_REPORT_RAW_ACCELEROMETER = const(0x14) 16
# # Uncalibrated gyroscope (rad/s).
# _BNO_REPORT_UNCALIBRATED_GYROSCOPE = const(0x07) 16
# # Raw uncalibrated gyroscope (ADC units).
# _BNO_REPORT_RAW_GYROSCOPE = const(0x15) 16
# # Magnetic field uncalibrated (in µTesla). The magnetic field measurement
# without hard-iron offset applied,
# # the hard-iron estimate is provided as a separate parameter.
# _BNO_REPORT_UNCALIBRATED_MAGNETIC_FIELD = const(0x0F)
# # Raw magnetic field measurement (in ADC units). Direct data from the magnetometer.
# Used for testing.
# _BNO_REPORT_RAW_MAGNETOMETER = const(0x16) 16
# # Geomagnetic Rotation Vector
# _BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR = const(0x09)
# # Game Rotation Vector
# _BNO_REPORT_GAME_ROTATION_VECTOR = const(0x08)
# # AR/VR Stabilized Game Rotation vector
# _BNO_REPORT_ARVR_STABILIZED_GAME_ROTATION_VECTOR = const(0x29)
# # AR/VR Stabilized Rotation Vector
# _BNO_REPORT_ARVR_STABILIZED_ROTATION_VECTOR = const(0x28)

# Gyro rotation Vector
# Gyro rotation Vector Prediction

# _BNO_REPORT_TAP_DETECTOR = const(0x10)
# _BNO_REPORT_STEP_COUNTER = const(0x11)
# _BNO_REPORT_SIGNIFICANT_MOTION = const(0x12)

# _BNO_REPORT_SAR = const(0x17)
# _BNO_REPORT_STEP_DETECTOR = const(0x18)
# _BNO_REPORT_SHAKE_DETECTOR = const(0x19)
# _BNO_REPORT_FLIP_DETECTOR = const(0x1A)
# _BNO_REPORT_PICKUP_DETECTOR = const(0x1B)
# _BNO_REPORT_STABILITY_DETECTOR = const(0x1C)
# _BNO_REPORT_SLEEP_DETECTOR = const(0x1F)
# _BNO_REPORT_TILT_DETECTOR = const(0x20)
# _BNO_REPORT_POCKET_DETECTOR = const(0x21)
# _BNO_REPORT_CIRCLE_DETECTOR = const(0x22)


# Reset reasons from ID Report reponse:
# 0 – Not Applicable
# 1 – Power On Reset
# 2 – Internal System Reset
# 3 – Watchdog Timeout
# 4 – External Reset
# 5 – Other
