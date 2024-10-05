import argparse
from time import sleep
from pubsub import pub
import time

from sense import vision
from act import eye
from act import motor
from act import sound
from act import headcontrol
from act import follow


# vision = vision.Vision(preview=False)
motor = motor.Motor()
sound = sound.Sound()
eye = eye.Eye()
head_control = headcontrol.HeadControl()
follow_control = follow.FollowControl()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    try:
        pub.sendMessage('sound', fname="Sound_Wow_810.ogg")
        # pub.sendMessage('headControlStatus', status="start")
        pub.sendMessage('followStatus', status="start")
        
        while 1:
            time.sleep(1)
    finally:
        # pub.sendMessage('headControlStatus', status="stop")
        pub.sendMessage('exit')

