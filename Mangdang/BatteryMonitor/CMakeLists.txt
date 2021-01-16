cmake_minimum_required(VERSION 2.8.7)
project(nv_tools C CXX)

SET(CMAKE_C_COMPILER "gcc")
SET(CMAKE_CXX_COMPILER "g++")

SET(FG_SRC i2cbusses.c smbus.c batterymonitor.c)

SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/out)

ADD_EXECUTABLE(batterymonitor ${FG_SRC})

