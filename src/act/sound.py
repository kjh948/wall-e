#!/usr/bin/python

import time
import pygame
from pubsub import pub
from time import sleep
import os.path

class Sound:
       
    def __init__(self, **kwargs):
        pygame.init()
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../../resources/sound/wall-e/'
        pub.subscribe(self.playFile, "sound")
        pub.subscribe(self.setVol, "setVol")        

    def playFile(self, fname):

        file = self.path + fname
        if not os.path.isfile(file):
            raise ValueError('Sound does not exist: ' + file)
        print(file)

        pygame.mixer_music.load(file)
        pygame.mixer_music.play()

    def setVol(self, val):
        if type(val) is 'str':
            val = int(val)
        pygame.mixer_music.set_volume(val)

    def getVol(self):
        val = pygame.mixer_music.set_volume()
        pub.sendMessage('getVol', vol=str(val))
        return val
    
if __name__ == '__main__':
    sound = Sound()
    #sound.playFile("Sound_Uh-Huh.ogg")

    pub.sendMessage('sound', fname="Sound_Uh-Huh.ogg")
    pub.sendMessage('sound', fname="Sound_Tada.ogg")
    while 1:
        time.sleep(1)

# class SoundNode:
#     def __init__(self):
#         self.sound = Sound()
#         pub.subscribe(self.animate, "animate")
#     def playFile(self, fname):
