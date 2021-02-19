# ST7789
Library for ST7789-based IPS LCD with Raspberry Pi (SPI interface, 240x240 pixels, 7 pins without CS pin) - This is different from the [Pirimoni Display](https://www.adafruit.com/product/3787) with 12 pins. It is also missing the CS pin unlike the original. These 7 pin displays are mostly sold on Aliexpress and Banggood and are good value for money (£3-4), but a bit tricky to set up initially.

# Wiring Diagram
![alt text](https://github.com/pkkirilov/ST7789/blob/master/ST7789%20wiring.png "Wiring")
TFT Display Pin to RPi Pin (as in board Pin, not BCM):

| TFT PIN | RPi GPIO |
|:-------:|:--------:|
|   GND   |   PIN 6  |
|   VCC   |   PIN 1  |
|   SCL   |  PIN 23  |
|   SDA   |  PIN 19  |
|   RES   |  PIN 15  |
|    DC   |  PIN 11  |
|   BLK   |  PIN 13  |


# References
* [ST7789 Datasheet](https://drive.google.com/file/d/1OHdfYN2_EqtdWj6n5vNYCxvyYUSaHTt2/view)
* [that-ben's thread](https://raspberrypi.stackexchange.com/q/108168)
* [Solinnovay's lib](https://github.com/solinnovay/Python_ST7789)
