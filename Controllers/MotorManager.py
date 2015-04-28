import time
from enum import Enum
from Controllers.ButtonManager import *
import math
from _overlapped import NULL

pigpioLibraryFound = False

class ScreenState(Enum):
    CLOSED = 0
    MOVING =1
    OPEN =2

try:
    import pigpio
    pigpioLibraryFound = True
except ImportError:
    print('pigpio library not found or pigpiod not running')
    

class MotorManager(QObject):
        
    currentAngle = None    
    currentState = None
    
    servo = 18

    moveSpeed = 0.008

    #ranges from 500-2500 but those may not be safe for the servo    
    bottomRange = 600  
    topRange = 2300

    #middle is always safe at 1500
    middle = 1500
    pi = None
    
    openAngle = 50
    closeAngle = 130
    
    def __init__(self):
        super(MotorManager, self).__init__()
        
        if(pigpioLibraryFound):            
            self.pi = pigpio.pi()
            self.setAngle(90)
            self.currentAngle = 90
            
    def getPulseWidth(self, angle):
        above90Range = self.topRange - self.middle
        below90Range = self.middle - self.bottomRange
        mod = self.middle
        if(angle > 90 and angle <= 180):
            percent = float((angle - 90)) / 90
            mod = math.trunc(self.middle + (float(percent) * above90Range))
        elif(angle < 90 and angle >= 0):
            percent = float(angle) / 90
            mod = math.trunc(self.bottomRange + (float(percent) * below90Range))
        return mod
    
    def setAngle(self, angle):
        mod = self.getPulseWidth(angle)
        self.pi.set_servo_pulsewidth(self.servo, mod)
        
    def move(self, angle):
        angleDiff = self.currentAngle - angle
        angleTracker = self.currentAngle
        angleDir = 0
        if(angleDiff < 0):
            angleDir = 1
        elif(angleDiff > 0):
            angleDir = -1
        for angle in range(abs(angleDiff)):
            angleTracker += angleDir
            self.setAngle(angleTracker)
            time.sleep(self.moveSpeed)
        return angleTracker
        
    
    def positionToggled(self):
        if(pigpioLibraryFound and self.currentState != None):
            if(self.currentState == ScreenState.CLOSED):
                print("SCREEN OPENING...")
                self.openLid()
            elif(self.currentState == ScreenState.OPEN):
                print("SCREEN CLOSING...")
                self.closeLid()
    
    def getCurrentState(self):
        return self.currentState

    def openLid(self):
        if(pigpioLibraryFound and self.currentState != ScreenState.MOVING):
            self.emit(QtCore.SIGNAL('turnScreenOn'))  
            self.currentState = ScreenState.MOVING
            self.currentAngle = self.move(self.openAngle)
            self.currentState = ScreenState.OPEN
            
        
        
    def closeLid(self):
        if(pigpioLibraryFound and self.currentState != ScreenState.MOVING):
            self.emit(QtCore.SIGNAL('turnScreenOff')) 
            self.currentState = ScreenState.MOVING
            
            self.currentAngle = self.move(self.closeAngle)
            self.currentState = ScreenState.CLOSED
                        

    def dispose(self):
        print("disposing of motor manager")
        if(pigpioLibraryFound):
            self.pi.set_servo_pulsewidth(self.servo, 0)
            self.pi.stop()
       
        




