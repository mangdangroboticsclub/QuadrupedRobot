#
# The makefile for eeprom driver build
#

obj-m += at24.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

install:
	sudo cp at24.ko  /lib/modules/`uname -r`/kernel/drivers/misc/
	sudo depmod -a
