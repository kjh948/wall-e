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

class HeadControl:
    def __init__(self, **kwargs):
        
        self.pid = PIDController(kP=4, kI=0, kD=0)
        self.pid.reset()

        self.target_ratio = [0.5,0.5]
        self.current_ratio = [0.5,0.5]
        self.target_pos = [90,90]

        pub.subscribe(self.detectResults, "detectHuman")
        pub.subscribe(self.headControlStatus, 'headControlStatus')
        pub.subscribe(self.exit, 'exit')

        self.status = 'stop'
        

    def controlGaze(self):
        while 1:
            idx = 0
            error = self.current_ratio[idx] - self.target_ratio[idx]
            self.target_pos[idx] = 10*self.pid.update(error)
            pub.sendMessage('setHeadDelta', dpos=[0,int(self.target_pos[idx])], vel=1)        

            if self.target_pos[idx] > 1:
                pub.sendMessage('eyecolor', colorL=[50,50,50], colorR=[150,150,250])        
            elif self.target_pos[idx] < -1:
                pub.sendMessage('eyecolor', colorL=[150,150,250], colorR=[50,50,50])        
            else:
                pub.sendMessage('eyecolor', colorL=[50,50,155], colorR=[50,50,155])        


            print("cratio: "+str(self.current_ratio[idx])+" tratio: "+str(self.target_ratio[idx])+" error:", str(error)+" tpos:", str(self.target_pos[idx]))
            time.sleep(0.10)

    def detectResults(self, bb, ratio):
        self.current_ratio = ratio

    def exit(self):
        self._thread.join()
    def headControlStatus(self, status):
        if status == 'start':
            if self.status is not 'working':
                self.status = 'working'
                self._thread = Thread(target=self.controlGaze)        
                self._thread.start()
        elif status == 'stop':
            self._thread.join()
            self.status = 'stop'