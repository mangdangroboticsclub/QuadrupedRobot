/*
 * Maxim MAX17201/MAX17205 fuel gauge driver
 *
 * Author: Mahir Ozturk <mahir.ozturk@maximintegrated.com>
 * Copyright (C) 2019 Maxim Integrated
 *
 * This program is free software; you can redistribute  it and/or modify it
 * under  the terms of  the GNU General  Public License as published by the
 * Free Software Foundation;  either version 2 of the  License, or (at your
 * option) any later version.
 *
 * This driver is based on max17042/40_battery.c
 */

#include <linux/delay.h>
#include <linux/err.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/mod_devicetable.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/power_supply.h>
#include <linux/platform_device.h>
#include <linux/pm.h>
#include <linux/regmap.h>
#include <linux/slab.h>

#define DRV_NAME "max1720x"

/* CONFIG register bits */
#define MAX1720X_CONFIG_ALRT_EN		(1 << 2)

/* STATUS register bits */
#define MAX1720X_STATUS_BST		(1 << 3)
#define MAX1720X_STATUS_POR		(1 << 1)

/* STATUS interrupt status bits */
#define MAX1720X_STATUS_ALRT_CLR_MASK	(0x88BB)
#define MAX1720X_STATUS_SOC_MAX_ALRT	(1 << 14)
#define MAX1720X_STATUS_TEMP_MAX_ALRT	(1 << 13)
#define MAX1720X_STATUS_VOLT_MAX_ALRT	(1 << 12)
#define MAX1720X_STATUS_SOC_MIN_ALRT	(1 << 10)
#define MAX1720X_STATUS_TEMP_MIN_ALRT	(1 << 9)
#define MAX1720X_STATUS_VOLT_MIN_ALRT	(1 << 8)
#define MAX1720X_STATUS_CURR_MAX_ALRT	(1 << 6)
#define MAX1720X_STATUS_CURR_MIN_ALRT	(1 << 2)

/* ProtStatus register bits */
#define MAX1730X_PROTSTATUS_CHGWDT	(1 << 15)
#define MAX1730X_PROTSTATUS_TOOHOTC	(1 << 14)
#define MAX1730X_PROTSTATUS_FULL	(1 << 13)
#define MAX1730X_PROTSTATUS_TOOCOLDC	(1 << 12)
#define MAX1730X_PROTSTATUS_OVP		(1 << 11)
#define MAX1730X_PROTSTATUS_OCCP	(1 << 10)
#define MAX1730X_PROTSTATUS_QOVFLW	(1 << 9)
#define MAX1730X_PROTSTATUS_RESCFAULT	(1 << 7)
#define MAX1730X_PROTSTATUS_PERMFAIL	(1 << 6)
#define MAX1730X_PROTSTATUS_DIEHOT	(1 << 5)
#define MAX1730X_PROTSTATUS_TOOHOTD	(1 << 4)
#define MAX1730X_PROTSTATUS_UVP		(1 << 3)
#define MAX1730X_PROTSTATUS_ODCP	(1 << 2)
#define MAX1730X_PROTSTATUS_RESDFAULT	(1 << 1)
#define MAX1730X_PROTSTATUS_SHDN	(1 << 0)

#define MAX1720X_VMAX_TOLERANCE		50 /* 50 mV */

#define MODELGAUGE_DATA_I2C_ADDR	0x36
#define NONVOLATILE_DATA_I2C_ADDR	0x0B

struct max1720x_platform_data {
	/*
	 * rsense in miliOhms.
	 * default 10 (if rsense = 0) as it is the recommended value by
	 * the datasheet although it can be changed by board designers.
	 */
	unsigned int rsense;
	int volt_min;	/* in mV */
	int volt_max;	/* in mV */
	int temp_min;	/* in DegreC */
	int temp_max;	/* in DegreeC */
	int soc_max;	/* in percent */
	int soc_min;	/* in percent */
	int curr_max;	/* in mA */
	int curr_min;	/* in mA */
};

struct max1720x_priv {
	struct i2c_client		*client;
	struct device			*dev;
	struct regmap			*regmap;
	struct power_supply		*battery;
	struct max1720x_platform_data	*pdata;
	struct work_struct		init_worker;
	struct attribute_group		*attr_grp;
	const u8			*regs;
	u8			nvmem_high_addr;
	int				cycles_reg_lsb_percent;
	int (*get_charging_status)(void);
	int (*get_battery_health)(struct max1720x_priv *priv, int *health);
};

enum chip_id {
	ID_MAX1720X,
	ID_MAX1730X,
};

enum register_ids {
	STATUS_REG = 0,
	VALRTTH_REG,
	TALRTTH_REG,
	SALRTTH_REG,
	ATRATE_REG,
	REPCAP_REG,
	REPSOC_REG,
	TEMP_REG,
	VCELL_REG,
	CURRENT_REG,
	AVGCURRENT_REG,
	TTE_REG	,
	CYCLES_REG,
	DESIGNCAP_REG,
	AVGVCELL_REG,
	MAXMINVOLT_REG,
	CONFIG_REG,
	TTF_REG	,
	VERSION_REG,
	FULLCAPREP_REG,
	VEMPTY_REG,
	QH_REG	,
	IALRTTH_REG,
	PROTSTATUS_REG,
	ATTTE_REG,
	VFOCV_REG,
};

static int max1720x_get_battery_health(struct max1720x_priv *priv, int *health);
static int max1730x_get_battery_health(struct max1720x_priv *priv, int *health);

static int (*get_battery_health_handlers[])
		(struct max1720x_priv *priv, int *health) = {
	[ID_MAX1720X] = max1720x_get_battery_health,
	[ID_MAX1730X] = max1730x_get_battery_health,
};

/* Register addresses  */
static const u8 max1720x_regs[] = {
	[STATUS_REG]		= 0x00,
	[VALRTTH_REG]		= 0x01,
	[TALRTTH_REG]		= 0x02,
	[SALRTTH_REG]		= 0x03,
	[ATRATE_REG]		= 0x04,
	[REPCAP_REG]		= 0x05,
	[REPSOC_REG]		= 0x06,
	[TEMP_REG]		= 0x08,
	[VCELL_REG]		= 0x09,
	[CURRENT_REG]		= 0x0A,
	[AVGCURRENT_REG]	= 0x0B,
	[TTE_REG] 		= 0x11,
	[CYCLES_REG] 		= 0x17,
	[DESIGNCAP_REG] 	= 0x18,
	[AVGVCELL_REG] 		= 0x19,
	[MAXMINVOLT_REG]	= 0x1B,
	[CONFIG_REG]		= 0x1D,
	[TTF_REG]		= 0x20,
	[VERSION_REG]		= 0x21,
	[FULLCAPREP_REG]	= 0x35,
	[VEMPTY_REG]		= 0x3A,
	[QH_REG]		= 0x4D,
	[IALRTTH_REG]		= 0xB4,
	[ATTTE_REG]		= 0xDD,
	[VFOCV_REG]		= 0xFB,
};

static const u8 max1730x_regs[] = {
	[STATUS_REG]		= 0x00,
	[VALRTTH_REG]		= 0x01,
	[TALRTTH_REG]		= 0x02,
	[SALRTTH_REG]		= 0x03,
	[ATRATE_REG]		= 0x04,
	[REPCAP_REG]		= 0x05,
	[REPSOC_REG]		= 0x06,
	[TEMP_REG]		= 0x1B,
	[VCELL_REG]		= 0x1A,
	[CURRENT_REG]		= 0x1C,
	[AVGCURRENT_REG]	= 0x1D,
	[TTE_REG] 		= 0x11,
	[CYCLES_REG] 		= 0x17,
	[DESIGNCAP_REG] 	= 0x18,
	[AVGVCELL_REG] 		= 0x19,
	[MAXMINVOLT_REG]	= 0x08,
	[CONFIG_REG]		= 0x1D,
	[TTF_REG]		= 0x20,
	[VERSION_REG]		= 0x21,
	[FULLCAPREP_REG]	= 0x10,
	[VEMPTY_REG]		= 0x3A,
	[QH_REG]		= 0x4D,
	[IALRTTH_REG]		= 0xAC,
	[PROTSTATUS_REG]	= 0xD9,
	[ATTTE_REG]		= 0xDD,
	[VFOCV_REG]		= 0xFB,
};

static const u8* chip_regs[] = {
	[ID_MAX1720X] = max1720x_regs,
	[ID_MAX1730X] = max1730x_regs,
};

static const u8 nvmem_high_addrs[] = {
	[ID_MAX1720X] = 0xDF,
	[ID_MAX1730X] = 0xEF,
};

static const int cycles_reg_lsb_percents[] = {
	[ID_MAX1720X] = 25,
	[ID_MAX1730X] = 16,
};

static enum power_supply_property max1720x_battery_props[] = {
	POWER_SUPPLY_PROP_PRESENT,
	POWER_SUPPLY_PROP_CYCLE_COUNT,
	POWER_SUPPLY_PROP_VOLTAGE_MAX,
	POWER_SUPPLY_PROP_VOLTAGE_MIN_DESIGN,
	POWER_SUPPLY_PROP_VOLTAGE_NOW,
	POWER_SUPPLY_PROP_VOLTAGE_AVG,
	POWER_SUPPLY_PROP_VOLTAGE_OCV,
	POWER_SUPPLY_PROP_CAPACITY,
	POWER_SUPPLY_PROP_CAPACITY_ALERT_MIN,
	POWER_SUPPLY_PROP_CAPACITY_ALERT_MAX,
	POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN,
	POWER_SUPPLY_PROP_CHARGE_FULL,
	POWER_SUPPLY_PROP_CHARGE_NOW,
	POWER_SUPPLY_PROP_CHARGE_COUNTER,
	POWER_SUPPLY_PROP_TEMP,
	POWER_SUPPLY_PROP_TEMP_ALERT_MIN,
	POWER_SUPPLY_PROP_TEMP_ALERT_MAX,
	POWER_SUPPLY_PROP_HEALTH,
	POWER_SUPPLY_PROP_CURRENT_NOW,
	POWER_SUPPLY_PROP_CURRENT_AVG,
	POWER_SUPPLY_PROP_STATUS,
	POWER_SUPPLY_PROP_TIME_TO_EMPTY_AVG,
	POWER_SUPPLY_PROP_TIME_TO_FULL_AVG,
};

static inline int max1720x_raw_voltage_to_uvolts(struct max1720x_priv *priv,
						 int lsb)
{
	return lsb * 10000 / 65536; /* 78.125uV per bit */
}

static inline int max1720x_raw_current_to_uamps(struct max1720x_priv *priv,
						int curr)
{
	return curr * 15625 / ((int)priv->pdata->rsense * 10);
}

static inline int max1720x_raw_capacity_to_uamph(struct max1720x_priv *priv,
						 int cap)
{
	return cap * 5000 / (int)priv->pdata->rsense;
}

static ssize_t max1720x_log_show(struct device *dev,
				 struct device_attribute *attr, char *buf)
{
	struct max1720x_priv *priv = dev_get_drvdata(dev);
	int rc = 0, reg = 0;
	u32 val = 0;

	for (reg = 0; reg < 0xE0; reg++) {
		regmap_read(priv->regmap, reg, &val);
		rc += (int)snprintf(buf+rc, PAGE_SIZE-rc, "0x%04X,", val);

		if (reg == 0x4F)
			reg += 0x60;

		if (reg == 0xBF)
			reg += 0x10;
	}

	rc += (int)snprintf(buf+rc, PAGE_SIZE-rc, "\n");

	return rc;
}

static ssize_t max1720x_nvmem_show(struct device *dev,
				   struct device_attribute *attr, char *buf)
{
	struct max1720x_priv *priv = dev_get_drvdata(dev);
	int rc = 0, reg = 0;
	u32 val = 0;
	int ret;
	int i;

	/*
	 * Device has a separate slave address for accessing non-volatile memory
	 * region, so we are temporarily changing i2c client address.
	 */
	priv->client->addr = NONVOLATILE_DATA_I2C_ADDR;

	for (reg = 0x80; reg < priv->nvmem_high_addr; reg += 16) {
		rc += snprintf(buf+rc, PAGE_SIZE-rc, "Page %02Xh: ",
			       (reg + 0x100) >> 4);
		for (i = 0; i < 16; i++) {
			ret = regmap_read(priv->regmap, reg + i, &val);
			if (ret) {
				dev_err(dev, "NV memory reading failed (%d)\n",
					ret);
				return 0;
			}
			rc += snprintf(buf+rc, PAGE_SIZE-rc, "0x%04X ", val);
		}
		rc += snprintf(buf+rc, PAGE_SIZE-rc, "\n");

	}

	priv->client->addr = MODELGAUGE_DATA_I2C_ADDR;

	return rc;
}

static ssize_t max1720x_atrate_show(struct device *dev,
				   struct device_attribute *attr, char *buf)
{
	struct max1720x_priv *priv = dev_get_drvdata(dev);
	u32 val = 0;
	int ret;

	ret = regmap_read(priv->regmap, priv->regs[ATRATE_REG], &val);
	if (ret) {
		return 0;
	}

	return sprintf(buf, "%d", (short)val);
}

static ssize_t max1720x_atrate_store(struct device *dev,
				     struct device_attribute *attr,
				     const char *buf, size_t count)
{
	struct max1720x_priv *priv = dev_get_drvdata(dev);
	s32 val = 0;
	int ret;

	if (kstrtos32(buf, 0, &val))
		return -EINVAL;

	ret = regmap_write(priv->regmap, priv->regs[ATRATE_REG], val);
	if (ret < 0)
		return ret;

	return count;
}

static ssize_t max1720x_attte_show(struct device *dev,
				   struct device_attribute *attr, char *buf)
{
	struct max1720x_priv *priv = dev_get_drvdata(dev);
	u32 val = 0;
	int ret;

	ret = regmap_read(priv->regmap, priv->regs[ATTTE_REG], &val);
	if (ret) {
		return 0;
	}

	return sprintf(buf, "%d", (short)val);
}

static DEVICE_ATTR(log, S_IRUGO, max1720x_log_show, NULL);
static DEVICE_ATTR(nvmem, S_IRUGO, max1720x_nvmem_show, NULL);
static DEVICE_ATTR(atrate, S_IRUGO | S_IWUSR, max1720x_atrate_show,
		   max1720x_atrate_store);
static DEVICE_ATTR(attte, S_IRUGO, max1720x_attte_show, NULL);

static struct attribute *max1720x_attr[] = {
	&dev_attr_log.attr,
	&dev_attr_nvmem.attr,
	&dev_attr_atrate.attr,
	&dev_attr_attte.attr,
	NULL
};

static struct attribute_group max1720x_attr_group = {
	.attrs = max1720x_attr,
};

static int max1720x_get_temperature(struct max1720x_priv *priv, int *temp)
{
	int ret;
	u32 data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[TEMP_REG], &data);
	if (ret < 0)
		return ret;

	*temp = sign_extend32(data, 15);
	/* The value is converted into centigrade scale */
	/* Units of LSB = 1 / 256 degree Celsius */
	*temp = (*temp * 10) >> 8;
	return 0;
}

static int max1720x_set_temp_lower_limit(struct max1720x_priv *priv,
						int temp)
{
	int ret;
	u32 data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[TALRTTH_REG], &data);
	if (ret < 0)
		return ret;

	/* Input in deci-centigrade, convert to centigrade */
	temp /= 10;

	data &= 0xFF00;
	data |= (temp & 0xFF);

	ret = regmap_write(map, priv->regs[TALRTTH_REG], data);
	if (ret < 0)
		return ret;

	return 0;
}

static int max1720x_get_temperature_alert_min(struct max1720x_priv *priv,
						int *temp)
{
	int ret;
	u32 data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[TALRTTH_REG], &data);
	if (ret < 0)
		return ret;

	/* Convert 1DegreeC LSB to 0.1DegreeC LSB */
	*temp = sign_extend32(data & 0xff, 7) * 10;

	return 0;
}

static int max1720x_set_temp_upper_limit(struct max1720x_priv *priv,
						int temp)
{
	int ret;
	u32 data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[TALRTTH_REG], &data);
	if (ret < 0)
		return ret;

	/* Input in deci-centigrade, convert to centigrade */
	temp /= 10;

	data &= 0xFF;
	data |= ((temp << 8) & 0xFF00);

	ret = regmap_write(map, priv->regs[TALRTTH_REG], data);
	if (ret < 0)
		return ret;

	return 0;
}

static int max1720x_get_temperature_alert_max(struct max1720x_priv *priv,
						int *temp)
{
	int ret;
	u32 data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[TALRTTH_REG], &data);
	if (ret < 0)
		return ret;

	/* Convert 1DegreeC LSB to 0.1DegreeC LSB */
	*temp = sign_extend32(data >> 8, 7) * 10;

	return 0;
}

static int max1720x_get_battery_health(struct max1720x_priv *priv, int *health)
{
	int temp, vavg, vbatt, ret;
	u32 val;

	ret = regmap_read(priv->regmap, priv->regs[AVGVCELL_REG], &val);
	if (ret < 0)
		goto health_error;

	/* bits [0-3] unused */
	vavg = max1720x_raw_voltage_to_uvolts(priv, val);
	/* Convert to millivolts */
	vavg /= 1000;

	ret = regmap_read(priv->regmap, priv->regs[VCELL_REG], &val);
	if (ret < 0)
		goto health_error;

	/* bits [0-3] unused */
	vbatt = max1720x_raw_voltage_to_uvolts(priv, val);
	/* Convert to millivolts */
	vbatt /= 1000;

	if (vavg < priv->pdata->volt_min) {
		*health = POWER_SUPPLY_HEALTH_DEAD;
		goto out;
	}

	if (vbatt > priv->pdata->volt_max + MAX1720X_VMAX_TOLERANCE) {
		*health = POWER_SUPPLY_HEALTH_OVERVOLTAGE;
		goto out;
	}

	ret = max1720x_get_temperature(priv, &temp);
	if (ret < 0)
		goto health_error;

	if (temp <= priv->pdata->temp_min) {
		*health = POWER_SUPPLY_HEALTH_COLD;
		goto out;
	}

	if (temp >= priv->pdata->temp_max) {
		*health = POWER_SUPPLY_HEALTH_OVERHEAT;
		goto out;
	}

	*health = POWER_SUPPLY_HEALTH_GOOD;

out:
	return 0;

health_error:
	return ret;
}

static int max1730x_get_battery_health(struct max1720x_priv *priv, int *health)
{
	int ret;
	u32 val;

	ret = regmap_read(priv->regmap, priv->regs[PROTSTATUS_REG], &val);
	if (ret < 0)
		return ret;

	if ((val & MAX1730X_PROTSTATUS_RESCFAULT) ||
	    (val & MAX1730X_PROTSTATUS_RESDFAULT)) {
		*health = POWER_SUPPLY_HEALTH_UNKNOWN;
	} else if ((val & MAX1730X_PROTSTATUS_TOOHOTC) ||
		   (val & MAX1730X_PROTSTATUS_TOOHOTD) ||
		   (val & MAX1730X_PROTSTATUS_DIEHOT)) {
		*health = POWER_SUPPLY_HEALTH_OVERHEAT;
	} else if ((val & MAX1730X_PROTSTATUS_UVP) ||
		   (val & MAX1730X_PROTSTATUS_PERMFAIL) ||
		   (val & MAX1730X_PROTSTATUS_SHDN)) {
		*health = POWER_SUPPLY_HEALTH_DEAD;
	} else if (val & MAX1730X_PROTSTATUS_TOOCOLDC) {
		*health = POWER_SUPPLY_HEALTH_COLD;
	} else if (val & MAX1730X_PROTSTATUS_OVP) {
		*health = POWER_SUPPLY_HEALTH_OVERVOLTAGE;
	} else if ((val & MAX1730X_PROTSTATUS_QOVFLW) ||
		   (val & MAX1730X_PROTSTATUS_OCCP) ||
		   (val & MAX1730X_PROTSTATUS_ODCP)) {
		*health = POWER_SUPPLY_HEALTH_UNSPEC_FAILURE;
	} else if (val & MAX1730X_PROTSTATUS_CHGWDT) {
		*health = POWER_SUPPLY_HEALTH_WATCHDOG_TIMER_EXPIRE;
	} else {
		*health = POWER_SUPPLY_HEALTH_GOOD;
	}

	return 0;
}

static int max1720x_get_min_capacity_alert_th(struct max1720x_priv *priv,
					      unsigned int *th)
{
	int ret;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[SALRTTH_REG], th);
	if (ret < 0)
		return ret;

	*th &= 0xFF;

	return 0;
}

static int max1720x_set_min_capacity_alert_th(struct max1720x_priv *priv,
					      unsigned int th)
{
	int ret;
	unsigned int data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[SALRTTH_REG], &data);
	if (ret < 0)
		return ret;

	data &= 0xFF00;
	data |= (th & 0xFF);

	ret = regmap_write(map, priv->regs[SALRTTH_REG], data);
	if (ret < 0)
		return ret;

	return 0;
}

static int max1720x_get_max_capacity_alert_th(struct max1720x_priv *priv,
					      unsigned int *th)
{
	int ret;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[SALRTTH_REG], th);
	if (ret < 0)
		return ret;

	*th >>= 8;

	return 0;
}

static int max1720x_set_max_capacity_alert_th(struct max1720x_priv *priv,
					      unsigned int th)
{
	int ret;
	unsigned int data;
	struct regmap *map = priv->regmap;

	ret = regmap_read(map, priv->regs[SALRTTH_REG], &data);
	if (ret < 0)
		return ret;

	data &= 0xFF;
	data |= ((th & 0xFF) << 8);

	ret = regmap_write(map, priv->regs[SALRTTH_REG], data);
	if (ret < 0)
		return ret;

	return 0;
}

static int max1720x_get_property(struct power_supply *psy,
				 enum power_supply_property psp,
				 union power_supply_propval *val)
{
	struct max1720x_priv *priv = power_supply_get_drvdata(psy);
	struct regmap *regmap = priv->regmap;
	struct max1720x_platform_data *pdata = priv->pdata;
	unsigned int reg;
	int ret;

	switch (psp) {
	case POWER_SUPPLY_PROP_PRESENT:
		ret = regmap_read(regmap, priv->regs[STATUS_REG], &reg);
		if (ret < 0)
			return ret;
		if (reg & MAX1720X_STATUS_BST)
			val->intval = 0;
		else
			val->intval = 1;
		break;
	case POWER_SUPPLY_PROP_CYCLE_COUNT:
		ret = regmap_read(regmap, priv->regs[CYCLES_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = reg * 100 / priv->cycles_reg_lsb_percent;
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_MAX:
		ret = regmap_read(regmap, priv->regs[MAXMINVOLT_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = reg >> 8;
		val->intval *= 20000; /* Units of LSB = 20mV */
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_MIN_DESIGN:
		ret = regmap_read(regmap, priv->regs[VEMPTY_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = reg >> 7;
		val->intval *= 10000; /* Units of LSB = 10mV */
		break;
	case POWER_SUPPLY_PROP_STATUS:
		if (pdata && priv->get_charging_status)
			val->intval = priv->get_charging_status();
		else
			val->intval = POWER_SUPPLY_STATUS_UNKNOWN;
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_NOW:
		ret = regmap_read(regmap, priv->regs[VCELL_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_voltage_to_uvolts(priv, reg);
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_AVG:
		ret = regmap_read(regmap, priv->regs[AVGVCELL_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_voltage_to_uvolts(priv, reg);
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_OCV:
		ret = regmap_read(regmap, priv->regs[VFOCV_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_voltage_to_uvolts(priv, reg);
		break;
	case POWER_SUPPLY_PROP_CAPACITY:
		ret = regmap_read(regmap, priv->regs[REPSOC_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = reg >> 8; /* RepSOC LSB: 1/256 % */
		break;
	case POWER_SUPPLY_PROP_CAPACITY_ALERT_MIN:
		ret = max1720x_get_min_capacity_alert_th(priv, &val->intval);
		if (ret < 0)
			return ret;

		break;
	case POWER_SUPPLY_PROP_CAPACITY_ALERT_MAX:
		ret = max1720x_get_max_capacity_alert_th(priv, &val->intval);
		if (ret < 0)
			return ret;

		break;
	case POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN:
		ret = regmap_read(regmap, priv->regs[DESIGNCAP_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_capacity_to_uamph(priv, reg);
		break;
	case POWER_SUPPLY_PROP_CHARGE_FULL:
		ret = regmap_read(regmap, priv->regs[FULLCAPREP_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_capacity_to_uamph(priv, reg);
		break;
	case POWER_SUPPLY_PROP_CHARGE_COUNTER:
		ret = regmap_read(regmap, priv->regs[QH_REG], &reg);
		if (ret < 0)
			return ret;

		/* This register is signed as oppose to other capacity type
		 * registers.
		 */
		val->intval = max1720x_raw_capacity_to_uamph(priv,
				sign_extend32(reg, 15));
		break;
	case POWER_SUPPLY_PROP_CHARGE_NOW:
		ret = regmap_read(regmap, priv->regs[REPCAP_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_capacity_to_uamph(priv, reg);
		break;
	case POWER_SUPPLY_PROP_TEMP:
		ret = max1720x_get_temperature(priv, &val->intval);
		if (ret < 0)
			return ret;
		break;
	case POWER_SUPPLY_PROP_TEMP_ALERT_MIN:
		ret = max1720x_get_temperature_alert_min(priv, &val->intval);
		if (ret < 0)
			return ret;
		break;
	case POWER_SUPPLY_PROP_TEMP_ALERT_MAX:
		ret = max1720x_get_temperature_alert_max(priv, &val->intval);
		if (ret < 0)
			return ret;
		break;
	case POWER_SUPPLY_PROP_HEALTH:
		if (priv->get_battery_health != 0) {
			ret = priv->get_battery_health(priv, &val->intval);
			if (ret < 0)
				return ret;
		} else {
			val->intval = POWER_SUPPLY_HEALTH_UNKNOWN;
		}
		break;
	case POWER_SUPPLY_PROP_CURRENT_NOW:
		ret = regmap_read(regmap, priv->regs[CURRENT_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_current_to_uamps(priv, sign_extend32(reg, 15));
		break;
	case POWER_SUPPLY_PROP_CURRENT_AVG:
		ret = regmap_read(regmap, priv->regs[AVGCURRENT_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = max1720x_raw_current_to_uamps(priv, sign_extend32(reg, 15));
		break;
	case POWER_SUPPLY_PROP_TIME_TO_EMPTY_AVG:
		ret = regmap_read(regmap, priv->regs[TTE_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = (reg * 45) >> 3; /* TTE LSB: 5.625 sec */
		break;
	case POWER_SUPPLY_PROP_TIME_TO_FULL_AVG:
		ret = regmap_read(regmap, priv->regs[TTF_REG], &reg);
		if (ret < 0)
			return ret;

		val->intval = (reg * 45) >> 3; /* TTF LSB: 5.625 sec */
		break;
	default:
		return -EINVAL;
	}
	return 0;
}

static int max1720x_set_property(struct power_supply *psy,
				 enum power_supply_property psp,
				 const union power_supply_propval *val)
{
	struct max1720x_priv *priv = power_supply_get_drvdata(psy);
	int ret = 0;

	switch (psp) {
	case POWER_SUPPLY_PROP_TEMP_ALERT_MIN:
		ret = max1720x_set_temp_lower_limit(priv, val->intval);
		if (ret < 0)
			dev_err(priv->dev, "temp alert min set fail:%d\n",
				ret);
		break;
	case POWER_SUPPLY_PROP_TEMP_ALERT_MAX:
		ret = max1720x_set_temp_upper_limit(priv, val->intval);
		if (ret < 0)
			dev_err(priv->dev, "temp alert max set fail:%d\n",
				ret);
		break;
	case POWER_SUPPLY_PROP_CAPACITY_ALERT_MIN:
		ret = max1720x_set_min_capacity_alert_th(priv, val->intval);
		if (ret < 0)
			dev_err(priv->dev, "capacity alert min set fail:%d\n",
				ret);
		break;
	case POWER_SUPPLY_PROP_CAPACITY_ALERT_MAX:
		ret = max1720x_set_max_capacity_alert_th(priv, val->intval);
		if (ret < 0)
			dev_err(priv->dev, "capacity alert max set fail:%d\n",
				ret);
		break;
	default:
		return -EINVAL;
	}

	return ret;
}

static int max1720x_property_is_writeable(struct power_supply *psy,
					  enum power_supply_property psp)
{
	int ret;

	switch (psp) {
	case POWER_SUPPLY_PROP_TEMP_ALERT_MIN:
	case POWER_SUPPLY_PROP_TEMP_ALERT_MAX:
	case POWER_SUPPLY_PROP_CAPACITY_ALERT_MIN:
	case POWER_SUPPLY_PROP_CAPACITY_ALERT_MAX:
		ret = 1;
		break;
	default:
		ret = 0;
	}

	return ret;
}

static irqreturn_t max1720x_irq_handler(int id, void *dev)
{
	struct max1720x_priv *priv = dev;
	u32 val;

	/* Check alert type */
	regmap_read(priv->regmap, priv->regs[STATUS_REG], &val);

	if (val & MAX1720X_STATUS_SOC_MAX_ALRT)
		dev_info(priv->dev, "Alert: SOC MAX!\n");
	if (val & MAX1720X_STATUS_SOC_MIN_ALRT)
		dev_info(priv->dev, "Alert: SOC MIN!\n");
	if (val & MAX1720X_STATUS_TEMP_MAX_ALRT)
		dev_info(priv->dev, "Alert: TEMP MAX!\n");
	if (val & MAX1720X_STATUS_TEMP_MIN_ALRT)
		dev_info(priv->dev, "Alert: TEMP MIN!\n");
	if (val & MAX1720X_STATUS_VOLT_MAX_ALRT)
		dev_info(priv->dev, "Alert: VOLT MAX!\n");
	if (val & MAX1720X_STATUS_VOLT_MIN_ALRT)
		dev_info(priv->dev, "Alert: VOLT MIN!\n");
	if (val & MAX1720X_STATUS_CURR_MAX_ALRT)
		dev_info(priv->dev, "Alert: CURR MAX!\n");
	if (val & MAX1720X_STATUS_CURR_MIN_ALRT)
		dev_info(priv->dev, "Alert: CURR MIN!\n");

	/* Clear alerts */
	regmap_write(priv->regmap, priv->regs[STATUS_REG],
				  val & MAX1720X_STATUS_ALRT_CLR_MASK);

	power_supply_changed(priv->battery);

	return IRQ_HANDLED;
}

static void max1720x_set_alert_thresholds(struct max1720x_priv *priv)
{
	struct max1720x_platform_data *pdata = priv->pdata;
	struct regmap *regmap = priv->regmap;
	u32 val;

	/* Set VAlrtTh */
	val = (pdata->volt_min / 20);
	val |= ((pdata->volt_max / 20) << 8);
	regmap_write(regmap, priv->regs[VALRTTH_REG], val);

	/* Set TAlrtTh */
	val = pdata->temp_min & 0xFF;
	val |= ((pdata->temp_max & 0xFF) << 8);
	regmap_write(regmap, priv->regs[TALRTTH_REG], val);

	/* Set SAlrtTh */
	val = pdata->soc_min;
	val |= (pdata->soc_max << 8);
	regmap_write(regmap, priv->regs[SALRTTH_REG], val);

	/* Set IAlrtTh */
	val = (pdata->curr_min * pdata->rsense / 400) & 0xFF;
	val |= (((pdata->curr_max * pdata->rsense / 400) & 0xFF) << 8);
	regmap_write(regmap, priv->regs[IALRTTH_REG], val);
}

static int max1720x_init(struct max1720x_priv *priv)
{
	struct regmap *regmap = priv->regmap;
	int ret;
	unsigned int reg;
	u32 fgrev;

	ret = regmap_read(regmap, priv->regs[VERSION_REG], &fgrev);
	if (ret < 0)
		return ret;

	dev_info(priv->dev, "IC Version: 0x%04x\n", fgrev);

	/* Optional step - alert threshold initialization */
	max1720x_set_alert_thresholds(priv);

	/* Clear Status.POR */
	ret = regmap_read(regmap, priv->regs[STATUS_REG], &reg);
	if (ret < 0)
		return ret;

	ret = regmap_write(regmap, priv->regs[STATUS_REG],
			   reg & ~MAX1720X_STATUS_POR);
	if (ret < 0)
		return ret;

	return 0;
}

static void max1720x_init_worker(struct work_struct *work)
{
	struct max1720x_priv *priv = container_of(work,
			struct max1720x_priv,
			init_worker);

	max1720x_init(priv);
}

static struct max1720x_platform_data *max1720x_parse_dt(struct device *dev)
{
	struct device_node *np = dev->of_node;
	struct max1720x_platform_data *pdata;
	int ret;

	pdata = devm_kzalloc(dev, sizeof(*pdata), GFP_KERNEL);
	if (!pdata)
		return NULL;

	ret = of_property_read_u32(np, "talrt-min", &pdata->temp_min);
	if (ret)
		pdata->temp_min = -128; /* DegreeC */ /* Disable alert */

	ret = of_property_read_u32(np, "talrt-max", &pdata->temp_max);
	if (ret)
		pdata->temp_max = 127; /* DegreeC */ /* Disable alert */

	ret = of_property_read_u32(np, "valrt-min", &pdata->volt_min);
	if (ret)
		pdata->volt_min = 0; /* mV */ /* Disable alert */

	ret = of_property_read_u32(np, "valrt-max", &pdata->volt_max);
	if (ret)
		pdata->volt_max = 5100; /* mV */ /* Disable alert */

	ret = of_property_read_u32(np, "ialrt-min", &pdata->curr_min);
	if (ret)
		pdata->curr_min = -5120; /* mA */ /* Disable alert */

	ret = of_property_read_u32(np, "ialrt-max", &pdata->curr_max);
	if (ret)
		pdata->curr_max = 5080; /* mA */ /* Disable alert */

	ret = of_property_read_u32(np, "salrt-min", &pdata->soc_min);
	if (ret)
		pdata->soc_min = 0; /* Percent */ /* Disable alert */

	ret = of_property_read_u32(np, "salrt-max", &pdata->soc_max);
	if (ret)
		pdata->soc_max = 255; /* Percent */ /* Disable alert */

	ret = of_property_read_u32(np, "rsense", &pdata->rsense);
	if (ret)
		pdata->rsense = 10;

	return pdata;
}

static const struct regmap_config max1720x_regmap = {
	.reg_bits		= 8,
	.val_bits		= 16,
	.val_format_endian	= REGMAP_ENDIAN_NATIVE,
};

static const struct power_supply_desc max1720x_fg_desc = {
	.name			= "max1720x_battery",
	.type			= POWER_SUPPLY_TYPE_BATTERY,
	.properties		= max1720x_battery_props,
	.num_properties		= ARRAY_SIZE(max1720x_battery_props),
	.get_property		= max1720x_get_property,
	.set_property		= max1720x_set_property,
	.property_is_writeable	= max1720x_property_is_writeable,
};

static int max1720x_probe(struct i2c_client *client,
			  const struct i2c_device_id *id)
{
	struct i2c_adapter *adapter = to_i2c_adapter(client->dev.parent);
	struct max1720x_priv *priv;
	struct power_supply_config psy_cfg = {};
	int ret;

	if (!i2c_check_functionality(adapter, I2C_FUNC_SMBUS_WORD_DATA))
		return -EIO;

	priv = devm_kzalloc(&client->dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->regs = chip_regs[id->driver_data];
	priv->nvmem_high_addr = nvmem_high_addrs[id->driver_data];
	priv->cycles_reg_lsb_percent = cycles_reg_lsb_percents[id->driver_data];
	priv->get_battery_health = get_battery_health_handlers[id->driver_data];

	if (client->dev.of_node)
		priv->pdata = max1720x_parse_dt(&client->dev);
	else
		priv->pdata = client->dev.platform_data;

	priv->dev = &client->dev;

	i2c_set_clientdata(client, priv);

	priv->client = client;
	priv->regmap = devm_regmap_init_i2c(client, &max1720x_regmap);
	if (IS_ERR(priv->regmap))
		return PTR_ERR(priv->regmap);

	INIT_WORK(&priv->init_worker, max1720x_init_worker);
	schedule_work(&priv->init_worker);

	psy_cfg.drv_data = priv;
	priv->battery = power_supply_register(&client->dev,
					      &max1720x_fg_desc, &psy_cfg);
	if (IS_ERR(priv->battery)) {
		ret = PTR_ERR(priv->battery);
		dev_err(&client->dev, "failed to register battery: %d\n", ret);
		goto err_supply;
	}

	if (client->irq) {
		ret = devm_request_threaded_irq(priv->dev, client->irq,
						NULL,
						max1720x_irq_handler,
						IRQF_TRIGGER_FALLING |
						IRQF_ONESHOT,
						priv->battery->desc->name,
						priv);
		if (ret) {
			dev_err(priv->dev, "Failed to request irq %d\n",
				client->irq);
			goto err_irq;
		} else {
			regmap_update_bits(priv->regmap, priv->regs[CONFIG_REG],
					   MAX1720X_CONFIG_ALRT_EN,
					   MAX1720X_CONFIG_ALRT_EN);
		}
	}

	/* Create max1720x sysfs attributes */
	priv->attr_grp = &max1720x_attr_group;
	ret = sysfs_create_group(&priv->dev->kobj, priv->attr_grp);
	if (ret) {
		dev_err(priv->dev, "Failed to create attribute group [%d]\n",
			ret);
		priv->attr_grp = NULL;
		goto err_attr;
	}

	return 0;

err_irq:
	power_supply_unregister(priv->battery);
err_supply:
	cancel_work_sync(&priv->init_worker);
err_attr:
	sysfs_remove_group(&priv->dev->kobj, priv->attr_grp);
	return ret;
}

static int max1720x_remove(struct i2c_client *client)
{
	struct max1720x_priv *priv = i2c_get_clientdata(client);

	cancel_work_sync(&priv->init_worker);
	sysfs_remove_group(&priv->dev->kobj, priv->attr_grp);
	power_supply_unregister(priv->battery);

	return 0;
}

#ifdef CONFIG_PM_SLEEP
static int max1720x_suspend(struct device *dev)
{
	struct i2c_client *client = to_i2c_client(dev);

	if (client->irq) {
		disable_irq(client->irq);
		enable_irq_wake(client->irq);
	}

	return 0;
}

static int max1720x_resume(struct device *dev)
{
	struct i2c_client *client = to_i2c_client(dev);

	if (client->irq) {
		disable_irq_wake(client->irq);
		enable_irq(client->irq);
	}

	return 0;
}

static SIMPLE_DEV_PM_OPS(max1720x_pm_ops, max1720x_suspend, max1720x_resume);
#define MAX1720X_PM_OPS (&max1720x_pm_ops)
#else
#define MAX1720X_PM_OPS NULL
#endif /* CONFIG_PM_SLEEP */

#ifdef CONFIG_OF
static const struct of_device_id max1720x_match[] = {
	{ .compatible = "maxim,max17201", },
	{ .compatible = "maxim,max17205", },
	{ .compatible = "maxim,max17301", },
	{ .compatible = "maxim,max17302", },
	{ .compatible = "maxim,max17303", },
	{ },
};
MODULE_DEVICE_TABLE(of, max1720x_match);
#endif

static const struct i2c_device_id max1720x_id[] = {
	{ "max17201", ID_MAX1720X },
	{ "max17205", ID_MAX1720X },
	{ "max17301", ID_MAX1730X },
	{ "max17302", ID_MAX1730X },
	{ "max17303", ID_MAX1730X },
	{ },
};
MODULE_DEVICE_TABLE(i2c, max1720x_id);

static struct i2c_driver max1720x_i2c_driver = {
	.driver = {
		.name		= DRV_NAME,
		.of_match_table	= of_match_ptr(max1720x_match),
		.pm		= MAX1720X_PM_OPS,
	},
	.probe		= max1720x_probe,
	.remove		= max1720x_remove,
	.id_table	= max1720x_id,
};
module_i2c_driver(max1720x_i2c_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Mahir Ozturk <mahir.ozturk@maximintegrated.com>");
MODULE_DESCRIPTION("Maxim MAX17201/5 and MAX17301/2/3 Fuel Gauge driver");
