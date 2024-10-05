from time import sleep
from pubsub import pub
import time
from threading import Thread, Timer

# import necessary packages
import time


class PIDController:
    def __init__(self, kP=100, kI=10, kD=0):

        # initialize gains
        self.kP = kP
        self.kI = kI
        self.kD = kD

    def reset(self):
        # intialize the current and previous time
        self.time_curr = time.time()
        self.time_prev = self.time_curr

        # initialize the previous error
        self.error_prev = 0

        # initialize the term result variables
        self.cP = 0
        self.cI = 0
        self.cD = 0

    def update(self, error, sleep=0.01):

        time.sleep(sleep)
        # grab the current time and calculate delta time / error
        self.time_curr = time.time()
        time_delta = self.time_curr - self.time_prev
        error_delta = error - self.error_prev

        # proportional term
        self.cP = error

        # integral term
        self.cI += error * time_delta

        # derivative term and prevent divide by zero
        self.cD = (error_delta / time_delta) if time_delta > 0 else 0

        # save previous time and error for the next update
        self.time_prev = self.time_curr
        self.error_prev = error

        # sum the terms and return
        return sum([
            self.kP * self.cP,
            self.kI * self.cI,
            self.kD * self.cD]
        )

class FollowControl:
    def __init__(self, **kwargs):
        
        self.pid_angular = PIDController(kP=4, kI=0, kD=0)
        self.pid_angular.reset()

        self.pid_linear = PIDController(kP=4, kI=0, kD=0)
        self.pid_linear.reset()

        self.target_ratio = [0.5,0.7]
        self.current_ratio = [0.5,0.5]
        self.target_vel = [0,0]
        self.bb = [0,0,0,0]

        pub.subscribe(self.detectResults, "detectHuman")
        pub.subscribe(self.followStatus, 'followStatus')
        pub.subscribe(self.exit, 'exit')

        self.status = 'stop'
        

    def controlFollow(self):
        while 1:
            l=0
            r=0
            idx = 0
            error_angular = self.current_ratio[idx] - self.target_ratio[idx]
            self.target_vel[idx] = 50*self.pid_angular.update(error_angular)
            l = -self.target_vel[idx]
            r = self.target_vel[idx]

            idx = 1
            # error_linear = self.current_ratio[idx] - self.target_ratio[idx]
            error_linear = self.bb[3] - 238
            self.target_vel[idx] = -self.pid_linear.update(error_linear)        
            l += self.target_vel[idx]
            r += self.target_vel[idx]

            # print(l)
            
            pub.sendMessage('setVel', l=l, r=r)

            idx = 0
            if self.target_vel[idx] > 1:                
                pub.sendMessage('eyecolor', colorL=[50,50,50], colorR=[150,150,250])                        
            elif self.target_vel[idx] < -1:
                pub.sendMessage('eyecolor', colorL=[150,150,250], colorR=[50,50,50])        
            else:
                pub.sendMessage('eyecolor', colorL=[50,50,155], colorR=[50,50,155])        


            # print("cratio: "+str(self.current_ratio[idx])+" tratio: "+str(self.target_ratio[idx])+" error:", str(error)+" tpos:", str(self.target_pos[idx]))
            time.sleep(0.10)

    def detectResults(self, bb, ratio):
        self.current_ratio = ratio
        self.bb = bb
        # print(bb)

    def exit(self):
        self._thread.join()
    def followStatus(self, status):
        if status == 'start':
            if self.status is not 'working':
                self.status = 'working'
                self._thread = Thread(target=self.controlFollow)        
                self._thread.start()
        elif status == 'stop':
            self._thread.join()
            self.status = 'stop'
