/*
 * SparkFun_BNO080_Library.cpp
 *
 *  Created on: Feb 6, 2019
 *      Author: josephmcgrath
 */

//Attempt communication with the device
//Return true if we got a 'Polo' back from Marco

#include "SparkFun_BNO080_Library.h"
#include <wiringPiI2C.h>
#include <stdio.h>
#include <errno.h>
#include <math.h>
#include <unistd.h>


//Define the size of the I2C buffer based on the platform the user has
//The catch-all default is 32
#define I2C_BUFFER_LENGTH 32

//-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

//Registers
const uint8_t CHANNEL_COMMAND = 0;
const uint8_t CHANNEL_EXECUTABLE = 1;
const uint8_t CHANNEL_CONTROL = 2;
const uint8_t CHANNEL_REPORTS = 3;
const uint8_t CHANNEL_WAKE_REPORTS = 4;
const uint8_t CHANNEL_GYRO = 5;

//All the ways we can configure or talk to the BNO080, figure 34, page 36 reference manual
//These are used for low level communication with the sensor, on channel 2
#define SHTP_REPORT_COMMAND_RESPONSE 0xF1
#define SHTP_REPORT_COMMAND_REQUEST 0xF2
#define SHTP_REPORT_FRS_READ_RESPONSE 0xF3
#define SHTP_REPORT_FRS_READ_REQUEST 0xF4
#define SHTP_REPORT_PRODUCT_ID_RESPONSE 0xF8
#define SHTP_REPORT_PRODUCT_ID_REQUEST 0xF9
#define SHTP_REPORT_BASE_TIMESTAMP 0xFB
#define SHTP_REPORT_SET_FEATURE_COMMAND 0xFD

//All the different sensors and features we can get reports from
//These are used when enabling a given sensor
#define SENSOR_REPORTID_ACCELEROMETER 0x01
#define SENSOR_REPORTID_GYROSCOPE 0x02
#define SENSOR_REPORTID_MAGNETIC_FIELD 0x03
#define SENSOR_REPORTID_LINEAR_ACCELERATION 0x04
#define SENSOR_REPORTID_ROTATION_VECTOR 0x05
#define SENSOR_REPORTID_GRAVITY 0x06
#define SENSOR_REPORTID_GAME_ROTATION_VECTOR 0x08
#define SENSOR_REPORTID_GEOMAGNETIC_ROTATION_VECTOR 0x09
#define SENSOR_REPORTID_TAP_DETECTOR 0x10
#define SENSOR_REPORTID_STEP_COUNTER 0x11
#define SENSOR_REPORTID_STABILITY_CLASSIFIER 0x13
#define SENSOR_REPORTID_PERSONAL_ACTIVITY_CLASSIFIER 0x1E

//Record IDs from figure 29, page 29 reference manual
//These are used to read the metadata for each sensor type
#define FRS_RECORDID_ACCELEROMETER 0xE302
#define FRS_RECORDID_GYROSCOPE_CALIBRATED 0xE306
#define FRS_RECORDID_MAGNETIC_FIELD_CALIBRATED 0xE309
#define FRS_RECORDID_ROTATION_VECTOR 0xE30B

//Command IDs from section 6.4, page 42
//These are used to calibrate, initialize, set orientation, tare etc the sensor
#define COMMAND_ERRORS 1
#define COMMAND_COUNTER 2
#define COMMAND_TARE 3
#define COMMAND_INITIALIZE 4
#define COMMAND_DCD 6
#define COMMAND_ME_CALIBRATE 7
#define COMMAND_DCD_PERIOD_SAVE 9
#define COMMAND_OSCILLATOR 10
#define COMMAND_CLEAR_DCD 11

#define CALIBRATE_ACCEL 0
#define CALIBRATE_GYRO 1
#define CALIBRATE_MAG 2
#define CALIBRATE_PLANAR_ACCEL 3
#define CALIBRATE_ACCEL_GYRO_MAG 4
#define CALIBRATE_STOP 5

#define MAX_PACKET_SIZE 128 //Packets can be up to 32k but we don't have that much RAM.
#define MAX_METADATA_SIZE 9 //This is in words. There can be many but we mostly only care about the first 9 (Qs, range, etc)

//Global Variables
uint8_t shtpHeader[4]; //Each packet has a header of 4 bytes
uint8_t shtpData[MAX_PACKET_SIZE];
uint8_t sequenceNumber[6] = { 0, 0, 0, 0, 0, 0 }; //There are 6 com channels. Each channel and direction has its own seqnum
uint8_t commandSequenceNumber = 0; //Commands have a seqNum as well. These are inside command packet, the header uses its own seqNum per channel

//These are the raw sensor values pulled from the user requested Input Report
uint16_t rawAccelX, rawAccelY, rawAccelZ, accelAccuracy;
uint16_t rawLinAccelX, rawLinAccelY, rawLinAccelZ, accelLinAccuracy;
uint16_t rawGyroX, rawGyroY, rawGyroZ, gyroAccuracy;
uint16_t rawMagX, rawMagY, rawMagZ, magAccuracy;
uint16_t rawQuatI, rawQuatJ, rawQuatK, rawQuatReal, rawQuatRadianAccuracy,
        quatAccuracy;
uint16_t stepCount;
uint32_t timeStamp;
uint8_t stabilityClassifier;
uint8_t activityClassifier;
uint8_t *_activityConfidences; //Array that store the confidences of the 9 possible activities
uint8_t calibrationStatus; //Byte R0 of ME Calibration Response

//These Q values are defined in the datasheet but can also be obtained by querying the meta data records
//See the read metadata example for more info
int16_t rotationVector_Q1 = 14;
int16_t accelerometer_Q1 = 8;
int16_t linear_accelerometer_Q1 = 8;
int16_t gyro_Q1 = 9;
int16_t magnetometer_Q1 = 4;

struct i2c_data {
	unsigned int writeCount;
	char *writeBuf;
	unsigned int readCount;
	char *readBuf;
};

int i2c_write_read(int fd, struct i2c_data i2cdata)
{
	int ret, wrt_flag, rd_flag;

	wrt_flag = rd_flag = 0;

	if(i2cdata.writeCount > 0) {
		ret = write(fd, i2cdata.writeBuf, i2cdata.writeCount);
		if(ret < 0) {
			printf("Error: i2c_write failed! ret: %d, errno: %d\n", ret, errno);
			return 0;
		}
		wrt_flag = (i2cdata.writeCount == ret) ? 1 : 0;
	} else
		wrt_flag = 1;

	usleep(5000);
	if(i2cdata.readCount > 0) {
		ret = read(fd, i2cdata.readBuf, i2cdata.readCount);
		if(ret < 0) {
			printf("Error: i2c_read failed! ret: %d, errno: %d\n", ret, errno);
			return 0;
		}
		rd_flag = (i2cdata.readCount == ret) ? 1 : 0;
	} else
		rd_flag = 1;


	ret = (wrt_flag & rd_flag);
	return ret;
}

bool IMU_begin(int handle)
{

    //We expect caller to begin their I2C port, with the speed of their choice external to the library (max 400 kHz for BNO080)

    //Begin by resetting the IMU
    IMU_softReset(handle);

    //Check communication with device
    shtpData[0] = SHTP_REPORT_PRODUCT_ID_REQUEST; //Request the product ID and reset info
    shtpData[1] = 0; //Reserved

    //Transmit packet on channel 2, 2 bytes

    if (!IMU_sendPacket(handle, CHANNEL_CONTROL, 2))
    {
        return false;
    }


    //Now we wait for response
    if (IMU_receivePacket(handle) == true)
    {
        if (shtpData[0] == SHTP_REPORT_PRODUCT_ID_RESPONSE)
        {
            return true;
        }
    }

    return false; //Something went wrong
}


//Updates the latest variables if possible
//Returns false if new readings are not available
bool IMU_dataAvailable(int handle)
{
    //If we have an interrupt pin connection available, check if data is available.
    //If int pin is NULL, then we'll rely on receivePacket() to timeout
    //See issue 13: https://github.com/sparkfun/SparkFun_BNO080_Arduino_Library/issues/13
    /* ignore interrupt for now
     if(_int != NULL)
     {
     if(digitalRead(_int) == HIGH) return(false);
     }
     */

    if (IMU_receivePacket(handle) == true)
    {
        //printf("shtpHeader[2] = %d, shtpData[0] = 0x%x\n", shtpHeader[2], shtpData[0]);
        //Check to see if this packet is a sensor reporting its data to us
        if (shtpHeader[2] == CHANNEL_REPORTS && shtpData[0] == SHTP_REPORT_BASE_TIMESTAMP)
        {
            parseInputReport(); //This will update the rawAccelX, etc variables depending on which feature report is found
            return (true);
        }
        else if (shtpHeader[2] == CHANNEL_CONTROL)
        {
            parseCommandReport(); //This will update responses to commands, calibrationStatus, etc.
            return (true);
        }
	else if (shtpHeader[2] != 0)
	{
            return (true);
	}

    } else {
	printf("Error: Receive Packet is not Available! shtpHeader[2] = %d, shtpData[0] = 0x%x\n", shtpHeader[2], shtpData[0]);
        IMU_softReset(handle);
        IMU_enableRotationVector(handle, 10); // send data updates every 50 ms
	sleep(1);
    }
    return (false);
}

//This function pulls the data from the command response report

//Unit responds with packet that contains the following:
//shtpHeader[0:3]: First, a 4 byte header
//shtpData[0]: The Report ID
//shtpData[1]: Sequence number (See 6.5.18.2)
//shtpData[2]: Command
//shtpData[3]: Command Sequence Number
//shtpData[4]: Response Sequence Number
//shtpData[4 + 0]: R0
//shtpData[4 + 1]: R1
//shtpData[4 + 2]: R2
//shtpData[4 + 3]: R3
//shtpData[4 + 4]: R4
//shtpData[4 + 5]: R5
//shtpData[4 + 6]: R6
//shtpData[4 + 7]: R7
//shtpData[4 + 8]: R8
void parseCommandReport(void)
{
    if (shtpData[0] == SHTP_REPORT_COMMAND_RESPONSE)
    {
        //The BNO080 responds with this report to command requests. It's up to us to remember which command we issued.
        uint8_t command = shtpData[2];//This is the Command byte of the response

        if(command == COMMAND_ME_CALIBRATE)
        {
            calibrationStatus = shtpData[5 + 0]; //R0 - Status (0 = success, non-zero = fail)
        }
    }
    else
    {
        //This sensor report ID is unhandled.
        //See reference manual to add additional feature reports as needed
    }

    //TODO additional feature reports may be strung together. Parse them all.
}

//This function pulls the data from the input report
//The input reports vary in length so this function stores the various 16-bit values as globals

//Unit responds with packet that contains the following:
//shtpHeader[0:3]: First, a 4 byte header
//shtpData[0:4]: Then a 5 byte timestamp of microsecond clicks since reading was taken (shtpData[0] == SHTP_REPORT_BASE_TIMESTAMP)
//shtpData[5 + 0]: Then a feature report ID (0x01 for Accel, 0x05 for Rotation Vector)
//shtpData[5 + 1]: Sequence number (See 6.5.18.2)
//shtpData[5 + 2]: Status
//shtpData[3]: Delay
//shtpData[4:5]: i/accel x/gyro x/etc
//shtpData[6:7]: j/accel y/gyro y/etc
//shtpData[8:9]: k/accel z/gyro z/etc
//shtpData[10:11]: real/gyro temp/etc
//shtpData[12:13]: Accuracy estimate
void parseInputReport(void)
{
    //Calculate the number of data bytes in this packet
    int16_t dataLength = ((uint16_t) shtpHeader[1] << 8 | shtpHeader[0]);
    dataLength &= ~(1 << 15); //Clear the MSbit. This bit indicates if this package is a continuation of the last.
    //Ignore it for now. TODO catch this as an error and exit

    dataLength -= 4; //Remove the header bytes from the data count

    timeStamp = ((uint32_t) shtpData[4] << (8 * 3)) | (shtpData[3] << (8 * 2)) | (shtpData[2] << (8 * 1)) | (shtpData[1] << (8 * 0));

    uint8_t status = shtpData[5 + 2] & 0x03; //Get status bits
    uint16_t data1 = (uint16_t) shtpData[5 + 5] << 8 | shtpData[5 + 4];
    uint16_t data2 = (uint16_t) shtpData[5 + 7] << 8 | shtpData[5 + 6];
    uint16_t data3 = (uint16_t) shtpData[5 + 9] << 8 | shtpData[5 + 8];
    uint16_t data4 = 0;
    uint16_t data5 = 0;

    if (dataLength - 5 > 9)
    {
        data4 = (uint16_t) shtpData[5 + 11] << 8 | shtpData[5 + 10];
    }
    if (dataLength - 5 > 11)
    {
        data5 = (uint16_t) shtpData[5 + 13] << 8 | shtpData[5 + 12];
    }

    //Store these generic values to their proper global variable
    if (shtpData[5] == SENSOR_REPORTID_ACCELEROMETER)
    {
        accelAccuracy = status;
        rawAccelX = data1;
        rawAccelY = data2;
        rawAccelZ = data3;
    }
    else if (shtpData[5] == SENSOR_REPORTID_LINEAR_ACCELERATION)
    {
        accelLinAccuracy = status;
        rawLinAccelX = data1;
        rawLinAccelY = data2;
        rawLinAccelZ = data3;
    }
    else if (shtpData[5] == SENSOR_REPORTID_GYROSCOPE)
    {
        gyroAccuracy = status;
        rawGyroX = data1;
        rawGyroY = data2;
        rawGyroZ = data3;
    }
    else if (shtpData[5] == SENSOR_REPORTID_MAGNETIC_FIELD)
    {
        magAccuracy = status;
        rawMagX = data1;
        rawMagY = data2;
        rawMagZ = data3;
    }
    else if (shtpData[5] == SENSOR_REPORTID_ROTATION_VECTOR || shtpData[5] == SENSOR_REPORTID_GAME_ROTATION_VECTOR)
    {
        quatAccuracy = status;
        rawQuatI = data1;
        rawQuatJ = data2;
        rawQuatK = data3;
        rawQuatReal = data4;
        rawQuatRadianAccuracy = data5; //Only available on rotation vector, not game rot vector
    }
    else if (shtpData[5] == SENSOR_REPORTID_STEP_COUNTER)
    {
        stepCount = data3; //Bytes 8/9
    }
    else if (shtpData[5] == SENSOR_REPORTID_STABILITY_CLASSIFIER)
    {
        stabilityClassifier = shtpData[5 + 4]; //Byte 4 only
    }
    else if (shtpData[5] == SENSOR_REPORTID_PERSONAL_ACTIVITY_CLASSIFIER)
    {
        activityClassifier = shtpData[5 + 5]; //Most likely state

        //Load activity classification confidences into the array
        int x;
        for (x = 0; x < 9; x++) //Hardcoded to max of 9. TODO - bring in array size
            _activityConfidences[x] = shtpData[5 + 6 + x]; //5 bytes of timestamp, byte 6 is first confidence byte
    }
    else if (shtpData[5] == SHTP_REPORT_COMMAND_RESPONSE)
    {
        //The BNO080 responds with this report to command requests. It's up to us to remember which command we issued.
        uint8_t command = shtpData[5 + 2]; //This is the Command byte of the response

        if (command == COMMAND_ME_CALIBRATE)
        {
            calibrationStatus = shtpData[5 + 5]; //R0 - Status (0 = success, non-zero = fail)
        }
    }
    else
    {
        //This sensor report ID is unhandled.
        //See reference manual to add additional feature reports as needed
    }

    //TODO additional feature reports may be strung together. Parse them all.
}

//Return the rotation vector quaternion I
float IMU_getQuatI()
{
  float quat = qToFloat(rawQuatI, rotationVector_Q1);
  return (quat);
}

//Return the rotation vector quaternion J
float IMU_getQuatJ()
{
  float quat = qToFloat(rawQuatJ, rotationVector_Q1);
  return (quat);
}

//Return the rotation vector quaternion K
float IMU_getQuatK()
{
  float quat = qToFloat(rawQuatK, rotationVector_Q1);
  return (quat);
}

//Return the rotation vector quaternion Real
float IMU_getQuatReal()
{
  float quat = qToFloat(rawQuatReal, rotationVector_Q1);
  return (quat);
}

//Return the rotation vector accuracy
float IMU_getQuatRadianAccuracy()
{
  float quat = qToFloat(rawQuatRadianAccuracy, rotationVector_Q1);
  return (quat);
}

//Return the accuracy
uint8_t IMU_getQuatAccuracy()
{
  return (quatAccuracy);
}

//Return the acceleration component
float IMU_getAccelX()
{
  float accel = qToFloat(rawAccelX, accelerometer_Q1);
  return (accel);
}

//Return the acceleration component
float IMU_getAccelY()
{
  float accel = qToFloat(rawAccelY, accelerometer_Q1);
  return (accel);
}

//Return the acceleration component
float IMU_getAccelZ()
{
  float accel = qToFloat(rawAccelZ, accelerometer_Q1);
  return (accel);
}

//Return the acceleration component
uint8_t IMU_getAccelAccuracy()
{
  return (accelAccuracy);
}

//Return the gyro component
float IMU_getGyroX()
{
  float gyro = qToFloat(rawGyroX, gyro_Q1);
  return (gyro);
}

//Return the gyro component
float IMU_getGyroY()
{
  float gyro = qToFloat(rawGyroY, gyro_Q1);
  return (gyro);
}

//Return the gyro component
float IMU_getGyroZ()
{
  float gyro = qToFloat(rawGyroZ, gyro_Q1);
  return (gyro);
}

//Return the gyro component
uint8_t IMU_getGyroAccuracy()
{
  return (gyroAccuracy);
}

//Send command to reset IC
//Read all advertisement packets from sensor
//The sensor has been seen to reset twice if we attempt too much too quickly.
//This seems to work reliably.
void IMU_softReset(int handle)
{
    shtpData[0] = 1; //Reset

    //Attempt to start communication with sensor
    IMU_sendPacket(handle, CHANNEL_EXECUTABLE, 1); //Transmit packet on channel 1, 1 byte

    //Read all incoming data and flush it
    sleep(1);
    while (IMU_receivePacket(handle) == true)
        ;
    sleep(.0050);
    while (IMU_receivePacket(handle) == true)
        ;

}


//Given a register value and a Q point, convert to float
//See https://en.wikipedia.org/wiki/Q_(number_format)
float qToFloat(int16_t fixedPointValue, uint8_t qPoint)
{
  float qFloat = fixedPointValue;
  qFloat *= pow(2, qPoint * -1);
  return (qFloat);
}


//Sends the packet to enable the rotation vector
void IMU_enableRotationVector(int handle, uint16_t timeBetweenReports)
{
    setFeatureCommand(handle, SENSOR_REPORTID_ROTATION_VECTOR, timeBetweenReports);
}

//Sends the packet to enable the gyro
void IMU_enableGyro(int handle, uint16_t timeBetweenReports)
{
    setFeatureCommand(handle, SENSOR_REPORTID_GYROSCOPE, timeBetweenReports);
}

//Sends the packet to enable the accelerometer
void IMU_enableAccelerometer(int handle, uint16_t timeBetweenReports)
{
    setFeatureCommand(handle, SENSOR_REPORTID_ACCELEROMETER, timeBetweenReports);
}

//Given a sensor's report ID, this tells the BNO080 to begin reporting the values
void setFeatureCommand(int handle, uint8_t reportID, uint16_t timeBetweenReports)
{
    setFeatureCommand_config(handle, reportID, timeBetweenReports, 0); //No specific config
}

//Given a sensor's report ID, this tells the BNO080 to begin reporting the values
//Also sets the specific config word. Useful for personal activity classifier
void setFeatureCommand_config(int handle, uint8_t reportID, uint16_t timeBetweenReports, uint32_t specificConfig)
{
	int ret;
    long microsBetweenReports = (long)timeBetweenReports * 1000L;

    shtpData[0] = SHTP_REPORT_SET_FEATURE_COMMAND; //Set feature command. Reference page 55
    shtpData[1] = reportID; //Feature Report ID. 0x01 = Accelerometer, 0x05 = Rotation vector
    shtpData[2] = 0; //Feature flags
    shtpData[3] = 0; //Change sensitivity (LSB)
    shtpData[4] = 0; //Change sensitivity (MSB)
    shtpData[5] = (microsBetweenReports >> 0) & 0xFF; //Report interval (LSB) in microseconds. 0x7A120 = 500ms
    shtpData[6] = (microsBetweenReports >> 8) & 0xFF; //Report interval
    shtpData[7] = (microsBetweenReports >> 16) & 0xFF; //Report interval
    shtpData[8] = (microsBetweenReports >> 24) & 0xFF; //Report interval (MSB)
    shtpData[9] = 0; //Batch Interval (LSB)
    shtpData[10] = 0; //Batch Interval
    shtpData[11] = 0; //Batch Interval
    shtpData[12] = 0; //Batch Interval (MSB)
    shtpData[13] = (specificConfig >> 0) & 0xFF; //Sensor-specific config (LSB)
    shtpData[14] = (specificConfig >> 8) & 0xFF; //Sensor-specific config
    shtpData[15] = (specificConfig >> 16) & 0xFF; //Sensor-specific config
    shtpData[16] = (specificConfig >> 24) & 0xFF; //Sensor-specific config (MSB)

    //Transmit packet on channel 2, 17 bytes
    ret = IMU_sendPacket(handle, CHANNEL_CONTROL, 17);
	if(ret < 0)
		printf("Faile to set Feature command: %d\n", reportID);
	else
		printf("Success to set Feature command: %d\n", reportID);
}

//Check to see if there is any new data available
//Read the contents of the incoming packet into the shtpData array
bool IMU_receivePacket(int handle)
{
	int ret;
    //Do I2C

    uint8_t txBuffer[I2C_BUFFER_LENGTH]; // not required for this
    uint8_t rxBuffer[I2C_BUFFER_LENGTH]; // to store header

    // initialize new i2c transaction
    struct i2c_data i2cTransaction;

    i2cTransaction.writeBuf = txBuffer;
    i2cTransaction.writeCount = 0;
    i2cTransaction.readBuf = rxBuffer;
    i2cTransaction.readCount = 4; // ask for four bytes to find out how much data we need to read

    /*
    // timeout here
    uint8_t counter;
    for (counter = 0; counter < 100; counter++)
    {
        if (i2c_write_read(handle, &i2cTransaction))
        {
            break;
        }
        sleep(.001);
    }
    if (counter == 100) // if timeout occurred
    {
        return false;
    }
    */
    //if (!i2c_write_read(handle, &i2cTransaction)) return false; (THIS BREAKS IT FOR SOME REASON)
    ret = i2c_write_read(handle, i2cTransaction);
	if(!ret) {
		printf("Failed to read Packet header via i2c!\n");
		return false;
	}

    //Get the first four bytes, aka the packet header
    uint8_t packetLSB = rxBuffer[0];
    uint8_t packetMSB = rxBuffer[1];
    uint8_t channelNumber = rxBuffer[2];
    uint8_t sequenceNumber_in = rxBuffer[3];


    //Store the header info.
    shtpHeader[0] = packetLSB;
    shtpHeader[1] = packetMSB;
    shtpHeader[2] = channelNumber;
    shtpHeader[3] = sequenceNumber_in;

    //Calculate the number of data bytes in this packet
    //printf("packetMSB = %d, packetLSB = %d, channelNumber = %d, sequenceNumber_in = %d\n", packetMSB, packetLSB, channelNumber, sequenceNumber_in);
    int16_t dataLength = ((uint16_t) packetMSB << 8 | packetLSB);
    dataLength &= ~(1 << 15); //Clear the MSbit.
    //This bit indicates if this package is a continuation of the last. Ignore it for now.

    if (dataLength == 0)
    {
        //Packet is empty
        printf("Packet is empty!\n");
        return (false);        //All done
    }
    dataLength -= 4; //Remove the header bytes from the data count

    IMU_getData(handle, dataLength);

    return (true); //We're done!
}

//Sends multiple requests to sensor until all data bytes are received from sensor
//The shtpData buffer has max capacity of MAX_PACKET_SIZE. Any bytes over this amount will be lost.
//I2C read limit is 32 bytes. Header is 4 bytes, so max data we can read per interation is 28 bytes
bool IMU_getData(int handle, uint16_t bytesRemaining)
{
    uint16_t dataSpot = 0; //Start at the beginning of shtpData array
    uint16_t numberOfBytesToRead;
	int ret;

    //Setup a series of chunked 32 byte reads
    while (bytesRemaining > 0)
    {
        numberOfBytesToRead = bytesRemaining;
        if (numberOfBytesToRead > (I2C_BUFFER_LENGTH - 4))
            numberOfBytesToRead = (I2C_BUFFER_LENGTH - 4);

        //Do I2C

        uint8_t txBuffer[I2C_BUFFER_LENGTH];
        uint8_t rxBuffer[I2C_BUFFER_LENGTH];

        // initialize new i2c transaction
        struct i2c_data i2cTransaction;

        i2cTransaction.writeBuf = txBuffer;
        i2cTransaction.writeCount = 0;
        i2cTransaction.readBuf = rxBuffer;
        i2cTransaction.readCount = (numberOfBytesToRead + 4);

        /*
        // timeout here
        uint8_t counter;
        for (counter = 0; counter < 100; counter++)
        {
            if (i2c_write_read(handle, &i2cTransaction))
            {
                break;
            }
            sleep(.001);
        }
        if (counter == 100) // if timeout occurred
        {
            return false;
        }
        */
        //if (!i2c_write_read(handle, &i2cTransaction)) return false;
        ret = i2c_write_read(handle, i2cTransaction);
		if(!ret) {
			printf("Failed to read shtpdata, continue\n");
			continue;
		}


        // need to discard the header
        uint8_t i;
        for (i = 4; i < (numberOfBytesToRead + 4); i++)
        {
            if (dataSpot < MAX_PACKET_SIZE)
            {
                shtpData[dataSpot++] = rxBuffer[i];
            }
            else
            {
                // skip this data because the data is full
            }
        }

        bytesRemaining -= numberOfBytesToRead;
    }
    return (true); //Done!
}


//Given the data packet, send the header then the data
//Returns false if sensor does not ACK
bool IMU_sendPacket(int handle, uint8_t channelNumber, uint8_t dataLength)
{
    uint8_t packetLength = dataLength + 4; //Add four bytes for the header

    //Do I2C

    uint8_t txBuffer[I2C_BUFFER_LENGTH]; // need to store transmission
    uint8_t rxBuffer[I2C_BUFFER_LENGTH]; // don't really need

    // Place data in txBuffer
    // all transmissions automatically start with the 7 bit slave address
    // 4 byte packet header
    txBuffer[0] = packetLength & 0xFF; // Packet length LSB
    txBuffer[1] = packetLength >> 8; // Packet length MSB (right shift to get rid of lower byte)
    txBuffer[2] = channelNumber; // Channel number
    txBuffer[3] = sequenceNumber[channelNumber]++; // Send the sequence number, increments with each packet sent, different counter for each channel
    // different counter for each direction as well
    // data
    uint8_t i;
    for (i = 0; i < dataLength; i++)
    {
        txBuffer[i + 4] = shtpData[i];
    }
    //if(packetLength > I2C_BUFFER_LENGTH) return(false); //You are trying to send too much. Break into smaller packets.

    // initialize new i2c transaction
    struct i2c_data i2cTransaction;

    i2cTransaction.writeBuf = txBuffer;
    i2cTransaction.writeCount = packetLength;
    i2cTransaction.readBuf = rxBuffer;
    i2cTransaction.readCount = 0;

    if (i2c_write_read(handle, i2cTransaction)) // returns true if in BLOCKING and successful transfer, or if in CALLBACK
    {
        return true;
    }

    return false;
}

