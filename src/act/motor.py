#!/usr/bin/python

from .Emakefun_MotorHAT import Emakefun_MotorHAT, Emakefun_Servo
import time
from pubsub import pub
from time import sleep
import os.path

class Motor:
       
    def __init__(self, **kwargs):
        self.mh = Emakefun_MotorHAT(addr=0x60)
        self.servo = []
        self.servo.append(self.mh.getServo(1))#left arm
        self.servo.append(self.mh.getServo(2))#right arm
        self.servo.append(self.mh.getServo(3))#pan
        self.servo.append(self.mh.getServo(4))#tilt

        self.wheel = []
        self.wheel.append(self.mh.getMotor(1))#left wheel
        self.wheel.append(self.mh.getMotor(2))#right wheel

        self.headOffset = [100,105]
        self.armOffset = [90,90]

        self.setInit()

        pub.subscribe(self.setHead, "setHead")
        pub.subscribe(self.setHeadDelta, "setHeadDelta")
        pub.subscribe(self.setArm, "setArm")
        pub.subscribe(self.setVel, "setVel")

    def setInit(self):
        self.setHead(self.headOffset, 10)
        self.setArm(self.armOffset, 10)
        self.turnOffMotors()

    def setHead(self, pos, vel):
        self.setPoswithVel(2, pos[0], vel)
        self.setPoswithVel(3, pos[1], vel)

    def setHeadDelta(self, dpos, vel):
        self.setDeltaPoswithVel(2, dpos[0], vel)
        self.setDeltaPoswithVel(3, dpos[1], vel)

    def setArm(self, pos, vel):
        self.setPoswithVel(0, pos[0], vel)
        self.setPoswithVel(1, pos[1], vel)
        
    def setPos(self, id, pos):
        self.servo[id].writeServo(pos)            

    def setPoswithVel(self, id, pos, vel=0):
        self.servo[id].writeServoWithSpeed(pos, vel)    
        # self.servo[id].writeServo(pos)    

    def setDeltaPoswithVel(self, id, dpos, vel=0):
        newpos = self.servo[id].readDegrees() - dpos
        self.servo[id].writeServoWithSpeed(newpos, vel)

    def setVel(self, l, r):
        if l < 0:
            self.wheel[0].run(Emakefun_MotorHAT.BACKWARD)
        else:
            self.wheel[0].run(Emakefun_MotorHAT.FORWARD)
        if r < 0:
            self.wheel[1].run(Emakefun_MotorHAT.FORWARD)
        else:
            self.wheel[1].run(Emakefun_MotorHAT.BACKWARD)

        self.wheel[0].setSpeed(abs(l))
        self.wheel[1].setSpeed(abs(r))

    def turnOffMotors(self):
        self.wheel[0].run(Emakefun_MotorHAT.RELEASE)
        self.wheel[1].run(Emakefun_MotorHAT.RELEASE)


# myServo = mh.getServo(4)
# speed = 9
# while (True):
#     myServo.writeServoWithSpeed(0, speed)
#     time.sleep(1)

#     myServo.writeServoWithSpeed(90, speed)
#     time.sleep(1)

#     myServo.writeServoWithSpeed(180, speed)
#     time.sleep(1)

    # for i in range (0, 181, 10):
    #     myServo.writeServo(i, 9)
    #     time.sleep(0.02)
    # time.sleep(1)
    # for i in range (180, -1, -10):
    #     myServo.writeServo(i, 9)
    #     time.sleep(0.02)
    # time.sleep(1)


if __name__ == '__main__':
    motor = Motor()


    pub.sendMessage('setHead', pos=[100,102], vel=8)
    time.sleep(1)

    # pub.sendMessage('setHead', pos=[110,70], vel=8)
    # time.sleep(1)

    # pub.sendMessage('setHead', pos=[100,110], vel=8)
    # time.sleep(1)

    # pub.sendMessage('setHead', pos=[90,90], vel=8)
    # time.sleep(1)

    # pub.sendMessage('setHead', pos=[100,90], vel=0.1)
    # time.sleep(1)

    # pub.sendMessage('setArm', pos=[90,90], vel=0)
    # time.sleep(1)
    # pub.sendMessage('setArm', pos=[130,130], vel=0)
    # time.sleep(1)
    # pub.sendMessage('setArm', pos=[50,50], vel=0)
    # time.sleep(1)



    # motor.setPos(0, 100)
    # time.sleep(1)
    # motor.setPos(0, 200)
    # time.sleep(1)
    # motor.setPos(0, 100)
    # time.sleep(1)
    # motor.setPos(0, 0)
'''
    

    print ("Forward! ")

    print ("\tSpeed up...")
    for i in range(255):
        motor.setVel(i,i)
        time.sleep(0.01)

    print ("\tSlow down...")
    for i in reversed(range(255)):
        motor.setVel(i,i)
        time.sleep(0.01)
    print ("Backward! ")
    print ("\tSpeed up...")
    for i in range(255):
        motor.setVel(-i,-i)
        time.sleep(0.01)

    print ("\tSlow down...")
    for i in reversed(range(255)):
        motor.setVel(-i,-i)
        time.sleep(0.01)

    print ("Release")
    motor.turnOffMotors()        
    time.sleep(1.0)

'''