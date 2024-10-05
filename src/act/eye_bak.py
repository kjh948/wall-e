#!/usr/bin/python
import time
from rpi_ws281x import PixelStrip, Color
import board
import neopixel_spi as neopixel

from pubsub import pub
from time import sleep

# LED strip configuration:
LED_COUNT = 2        # Number of LED pixels.
# LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class Eye:
       
    def __init__(self, **kwargs):
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.setOff()

        pub.subscribe(self.setEyesColor, "eyecolor")
        pub.subscribe(self.setEyesPattern, "eyepattern")

    def setLeftEye(self, color):
        self.strip.setPixelColor(0, Color(color[0], color[1], color[2]))
        
    def setRightEye(self, color):
        self.strip.setPixelColor(1, Color(color[0], color[1], color[2]))

    def show(self):
        self.strip.show()
        
    def setOff(self):
        self.strip.setPixelColor(0, Color(0,0,0))
        self.strip.setPixelColor(1, Color(0,0,0))
        self.strip.show()

    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
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
            self.setEyesColor((80,80,255),(80,80,255))       


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

            sleep(0.1)
            # self.setOff()
            # sleep(0.05)
        # c = 0
        # while 1:
            
        #     eye.setLeftEye((c,0,0))
        #     eye.setRightEye((c,c,c))
        #     eye.show()
        #     sleep(0.1)
        #     c = c+1
        #     print(c)
        #     if c>100:
        #         c = 0

        # start = 0
        # lighter = True
        # increment = 2
        # while start >= 0:            
        #     eye.setLeftEye([(x * start)%255 for x in color])
        #     eye.setRightEye([(x * start)%255 for x in color])
        #     if lighter is True:
        #         start = start + increment
        #     else:
        #         start = start - increment
        #     if start > 100:
        #         lighter =  not lighter
        #         start = 100
        #         sleep(1)
        #     sleep(0.05)
        # sleep(1)

if __name__ == '__main__':
    eye = Eye()

    # eye.setOff()

    # eye.breathe((120,120,120))

    while 1:
        pub.sendMessage('eyepattern', color = (0,0,0), type="angry")
        time.sleep(1)
        pub.sendMessage('eyepattern', color = (0,0,0), type="breathe")
        time.sleep(3)
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
    
