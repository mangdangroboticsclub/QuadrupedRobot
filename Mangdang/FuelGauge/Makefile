#
# The makefile for max17205 driver build
#

obj-m += max1720x_battery.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

install:
	sudo cp max1720x_battery.ko /lib/modules/`uname -r`/kernel/drivers/power/supply/
	sudo depmod -a
