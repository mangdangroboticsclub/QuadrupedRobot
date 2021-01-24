/*
 * SparkFun_BNO080_Library.h
 *
 *  Created on: Feb 6, 2019
 *      Author: josephmcgrath
 */

#ifndef SPARKFUN_BNO080_LIBRARY_H_
#define SPARKFUN_BNO080_LIBRARY_H_

#include <stdbool.h>

//The default I2C address for the BNO080 on the SparkX breakout is 0x4B. 0x4A is also possible.
#define BNO080_DEFAULT_ADDRESS 0x4B

typedef signed char             int8_t;
typedef short int               int16_t;
typedef int                     int32_t;
//typedef long int                int64_t;

typedef unsigned char           uint8_t;
typedef unsigned short int      uint16_t;
typedef unsigned int            uint32_t;
//typedef unsigned long int       uint64_t;

// IMU Functions
bool IMU_begin(int handle);
void IMU_softReset(int handle); //Try to reset the IMU via software

float qToFloat(int16_t fixedPointValue, uint8_t qPoint); //Given a Q value, converts fixed point floating to regular floating point number

bool IMU_receivePacket(int handle);
bool IMU_getData(int handle, uint16_t bytesRemaining); //Given a number of bytes, send the requests in I2C_BUFFER_LENGTH chunks
bool IMU_sendPacket(int handle, uint8_t channelNumber,
                    uint8_t dataLength);

void IMU_enableRotationVector(int handle, uint16_t timeBetweenReports);
void IMU_enableGyro(int handle, uint16_t timeBetweenReports);
void IMU_enableAccelerometer(int handle, uint16_t timeBetweenReports);

bool IMU_dataAvailable(int handle);
void parseInputReport(void); //Parse sensor readings out of report
void parseCommandReport(void); //Parse command responses out of report

float IMU_getQuatI();
float IMU_getQuatJ();
float IMU_getQuatK();
float IMU_getQuatReal();
float IMU_getQuatRadianAccuracy();
uint8_t IMU_getQuatAccuracy();

float IMU_getAccelX();
float IMU_getAccelY();
float IMU_getAccelZ();
uint8_t IMU_getAccelAccuracy();

float IMU_getGyroX();
float IMU_getGyroY();
float IMU_getGyroZ();
uint8_t IMU_getGyroAccuracy();

void setFeatureCommand(int handle, uint8_t reportID,
                       uint16_t timeBetweenReports);
void setFeatureCommand_config(int handle, uint8_t reportID,
                              uint16_t timeBetweenReports,
                              uint32_t specificConfig);



#endif /* SPARKFUN_BNO080_LIBRARY_H_ */
