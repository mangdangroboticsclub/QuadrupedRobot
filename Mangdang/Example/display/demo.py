import os
import sys
from PIL import Image

sys.path.append("/home/ubuntu/Robotics/QuadrupedRobot")
sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("/home/ubuntu/Robotics/QuadrupedRobot") for name in dirs])
from Mangdang.LCD.ST7789 import ST7789

def main():
    """ The demo for picture show
    """

    # init st7789 device 
    disp = ST7789()
    disp.begin()
    disp.clear()

    # show exaple picture
    image=Image.open("./dog.png")
    image.resize((320,240))
    disp.display(image)

main()

