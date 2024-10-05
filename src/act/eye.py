#!/usr/bin/python
import time
from rpi_ws281x import PixelStrip, Color
import board
import neopixel_spi as neopixel

from pubsub import pub
from time import sleep

# LED strip configuration:
NUM_PIXELS = 2        # Number of LED pixels.
PIXEL_ORDER = neopixel.GRB

class Eye:
    def __init__(self, **kwargs):
        spi = board.SPI()
        self.pixels = neopixel.NeoPixel_SPI(
                       spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
                        , bit0=0b10000000
        )

        pub.subscribe(self.setEyesColor, "eyecolor")
        pub.subscribe(self.setEyesPattern, "eyepattern")

        

    def setLeftEye(self, color):
        self.pixels[0] = Color(color[0], color[1], color[2])
        
    def setRightEye(self, color):
        self.pixels[1] = Color(color[0], color[1], color[2])

    def show(self):
        self.pixels.show()
        
    def setOff(self):
        self.pixels[0] = Color(0,0,0)
        self.pixels[1] = Color(0,0,0)
        self.show()

    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.pixels[i] = color
            self.show()
            time.sleep(wait_ms / 1000.0)
    
    def setEyesColor(self, colorL=(0,0,0), colorR=(0,0,0)):
        self.setLeftEye(colorL)
        self.setRightEye(colorR)
        self.show()        
        
    def setEyesPattern(self, color, type):
        print("eye pattern:\t" + type)
        if type == 'breathe':            
            self.breathe(color)
        elif type == 'angry':
            self.setEyesColor((255,0,0),(255,0,0))
        elif type == 'happy':
            self.setEyesColor((160,160,255),(160,160,255))       

    def breathe(self, color):

        c = 0
        delta = 1
        while 1:
            self.setLeftEye((c,c,c))
            self.setRightEye((c,c,c))
            self.show()
            c = c + delta
            if c == 255:
                delta = -1
            if c == 0:
                delta = 1
            sleep(0.005)


if __name__ == '__main__':
    eye = Eye()

    # eye.setOff()

    # eye.breathe((120,120,120))

    while 1:
        pub.sendMessage('eyepattern', color = (0,0,0), type="angry")
        time.sleep(1)
        # pub.sendMessage('eyepattern', color = (0,0,0), type="breathe")
        # time.sleep(3)
        pub.sendMessage('eyepattern', color = (0,0,0), type="happy")
        time.sleep(1)
    # while 1:
        # eye.colorWipe(Color(255, 0, 0))  # Red wipe
        # eye.colorWipe(Color(0, 255, 0))  # Green wipe
        # eye.colorWipe(Color(0, 0, 255))  # Blue wipe
        # eye.breathe((255,120,120))
    

        # eye.setLeftEye((100,0,0))
        # time.sleep(0.1)
        # eye.setLeftEye([0,100,0])
        # time.sleep(0.1)
        # eye.setLeftEye([0,0,100])
        # time.sleep(0.1)
        # eye.setRightEye([100,0,0])
        # time.sleep(0.1)
        # eye.setRightEye([0,100,0])
        # time.sleep(0.1)
        # eye.setRightEye([0,0,100])
        # time.sleep(0.1)
    
