/*
    smbus.h - SMBus level access helper functions

    Copyright (C) 1995-1997  Simon G. Vogl
    Copyright (C) 1998-1999  Frodo Looijaard <frodol@dds.nl>
    Copyright (C) 2012-2017  Jean Delvare <jdelvare@suse.de>

    This library is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation; either version 2.1 of the License, or
    (at your option) any later version.
*/

#ifndef LIB_I2C_SMBUS_H
#define LIB_I2C_SMBUS_H

#define I2C_API_VERSION		0x100

#include <linux/types.h>
#include <linux/i2c.h>

extern __s32 i2c_smbus_access(int file, char read_write, __u8 command,
			      int size, union i2c_smbus_data *data);

extern __s32 i2c_smbus_write_quick(int file, __u8 value);
extern __s32 i2c_smbus_read_byte(int file);
extern __s32 i2c_smbus_write_byte(int file, __u8 value);
extern __s32 i2c_smbus_read_byte_data(int file, __u8 command);
extern __s32 i2c_smbus_write_byte_data(int file, __u8 command, __u8 value);
extern __s32 i2c_smbus_read_word_data(int file, __u8 command);
extern __s32 i2c_smbus_write_word_data(int file, __u8 command, __u16 value);
extern __s32 i2c_smbus_process_call(int file, __u8 command, __u16 value);

/* Returns the number of read bytes */
extern __s32 i2c_smbus_read_block_data(int file, __u8 command, __u8 *values);
extern __s32 i2c_smbus_write_block_data(int file, __u8 command, __u8 length,
					const __u8 *values);

/* Returns the number of read bytes */
/* Until kernel 2.6.22, the length is hardcoded to 32 bytes. If you
   ask for less than 32 bytes, your code will only work with kernels
   2.6.23 and later. */
extern __s32 i2c_smbus_read_i2c_block_data(int file, __u8 command, __u8 length,
					   __u8 *values);
extern __s32 i2c_smbus_write_i2c_block_data(int file, __u8 command, __u8 length,
					    const __u8 *values);

/* Returns the number of read bytes */
extern __s32 i2c_smbus_block_process_call(int file, __u8 command, __u8 length,
					  __u8 *values);

#endif /* LIB_I2C_SMBUS_H */
