import argparse
from time import sleep
from pubsub import pub
import time

from sense import vision
from act import eye
from act import motor
from act import sound
from act import headcontrol

motor = motor.Motor()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    try:
        # pub.sendMessage('setHead', pos=[100,120], vel=8)        
        pub.sendMessage('setVel', l=50, r=50)
        while 1:
            time.sleep(1)
    finally:
        pub.sendMessage('exit')

