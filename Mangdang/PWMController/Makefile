#
# The makefile for pwm controller driver build
#

obj-m += pwm-pca9685.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

install:
	sudo cp pwm-pca9685.ko  /lib/modules/`uname -r`/kernel/drivers/misc/
	sudo depmod -a
