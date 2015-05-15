import time
from enum import Enum
import math
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from threading import Timer,Thread,Event

class ScreenState(Enum):
    CLOSED = 0
    MOVING =1
    OPEN =2

pigpioLibraryFound = False

try:
    import pigpio
    pigpioLibraryFound = True
except ImportError:
    print('pigpio library not found or pigpiod not running')
    

class ScreenServo(QObject):

    Enabled = True
    servo = None
    togglePin = None


    currentAngle = None    
    currentState = None
    moveSpeed = 0.02

    #ranges from 500-2500 but those may not be safe for the servo    
    #bottomRange = 600  
    #topRange = 2400

    bottomRange = 800  
    topRange = 2200

    #middle is always safe at 1500
    middle = 1500
    pi = None
    
    openAngle = 80
    closeAngle = 160

    #openAngle = 60
    #closeAngle = 180
    

    def __init__(self):
        super(ScreenServo, self).__init__()

    def setPin(self, pinConfig):
        self.servo = pinConfig["SERVO"]
        self.togglePin = pinConfig["SCREEN_TOGGLE"]
        self.initialize()

    def processPinEvent(self, pinNum):
        print("screen servo processing pin: " + str(pinNum) + " servo: " + str(self.togglePin))
        if(self.currentState != ScreenState.MOVING and self.togglePin == pinNum):
            self.emit(QtCore.SIGNAL('logEvent'),"servo button pressed") 
            self.positionToggled()

    def initialize(self):
        if(pigpioLibraryFound):           
            self.emit(QtCore.SIGNAL('logEvent'),"servo initialized") 
            self.pi = pigpio.pi()
            self.setAngle(90)
            self.currentAngle = 90
            self.openLid()



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
         #self.pi.set_servo_pulsewidth(self.servo, 0)
         return angleTracker
         
     
    def positionToggled(self):     
         print("position toggled   state: " + str(self.currentState))   
         if(pigpioLibraryFound and self.currentState != None):
             if(self.currentState == ScreenState.CLOSED):
                 #self.emit(QtCore.SIGNAL('turnScreenOn')) 
                 self.emit(QtCore.SIGNAL('logEvent'),"screen opening")
                 self.openLid()
             elif(self.currentState == ScreenState.OPEN):
                 #self.emit(QtCore.SIGNAL('turnScreenOff')) 
                 self.emit(QtCore.SIGNAL('logEvent'),"screen closing")
                 self.closeLid()
     
    def getCurrentState(self):
         return self.currentState
  
    def openLid(self):
         if(pigpioLibraryFound and self.currentState != ScreenState.MOVING):             
             self.currentState = ScreenState.MOVING
             self.currentAngle = self.move(self.openAngle)
             self.currentState = ScreenState.OPEN
             self.emit(QtCore.SIGNAL('logEvent'), "lid opened  current angle: " + str(self.currentAngle))
             
         
         
    def closeLid(self):
         if(pigpioLibraryFound and self.currentState != ScreenState.MOVING):
             self.currentState = ScreenState.MOVING            
             self.currentAngle = self.move(self.closeAngle)
             self.currentState = ScreenState.CLOSED
             self.emit(QtCore.SIGNAL('logEvent'), "lid closed  current angle: " + str(self.currentAngle))
                         
  
    def dispose(self):
         self.emit(QtCore.SIGNAL('logEvent'),"disposing of motor manager")
         if(pigpioLibraryFound):
             self.pi.set_servo_pulsewidth(self.servo, 0)
             self.pi.stop()

