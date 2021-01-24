sources:=$(wildcard *.c)
objects:=$(sources:.c=.o)

CC=gcc

CFLAG += -lm -lwiringPi

libbno080.so:SparkFun_BNO080_Library.c
	gcc -shared -Wl,-soname,libbno080 -o libbno080.so -fPIC SparkFun_BNO080_Library.c

.PHONY: clean
clean:
	rm -f all $(objects) $(dependence) libbno080.so
