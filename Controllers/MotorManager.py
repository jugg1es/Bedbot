import time
from enum import Enum
from Controllers.ButtonManager import *
import math

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

    moveSpeed = 0.02

    #ranges from 500-2500 but those may not be safe for the servo    
    bottomRange = 600  
    topRange = 2500

    #middle is always safe at 1500
    middle = 1500
    pi = None
    
    #openAngle = 60
    #closeAngle = 180
    
    openAngle = 80
    closeAngle = 120
    
    def __init__(self):
        super(MotorManager, self).__init__()
        
       
            
    def initialize(self):
        if(pigpioLibraryFound):            
            self.pi = pigpio.pi()
            self.setAngle(90)
            self.currentAngle = 90
            self.openLid()
        self.emit(QtCore.SIGNAL('turnScreenOn')) 
            
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
        print("finished moving")
        #self.pi.set_servo_pulsewidth(self.servo, 0)
        return angleTracker
        
    
    def positionToggled(self):     
        print("position toggled   state: " + str(self.currentState))   
        if(pigpioLibraryFound and self.currentState != None):
            if(self.currentState == ScreenState.CLOSED):
                self.emit(QtCore.SIGNAL('turnScreenOn')) 
                self.openLid()
            elif(self.currentState == ScreenState.OPEN):
                self.emit(QtCore.SIGNAL('turnScreenOff')) 
                print("SCREEN CLOSING...")
                self.closeLid()
    
    def getCurrentState(self):
        return self.currentState

    def openLid(self):
        if(pigpioLibraryFound and self.currentState != ScreenState.MOVING):             
            self.currentState = ScreenState.MOVING
            self.currentAngle = self.move(self.openAngle)
            self.currentState = ScreenState.OPEN
            print("screen opened")
            
        
        
    def closeLid(self):
        if(pigpioLibraryFound and self.currentState != ScreenState.MOVING):
            self.currentState = ScreenState.MOVING            
            self.currentAngle = self.move(self.closeAngle)
            self.currentState = ScreenState.CLOSED
            print("screen closed")
                        

    def dispose(self):
        print("disposing of motor manager")
        if(pigpioLibraryFound):
            self.pi.set_servo_pulsewidth(self.servo, 0)
            self.pi.stop()
       
        




