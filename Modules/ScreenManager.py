import time
from enum import Enum
import math
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from threading import Timer,Thread,Event
import os
import subprocess
import sys
import shlex

class ScreenState(Enum):
    CLOSED = 0
    MOVING = 1
    OPEN = 2

hasIOLibraries = False

try:
    import RPi.GPIO as IO
    hasIOLibraries = True
except ImportError:
    print('Raspberry Pi GPIO library not found')


pigpioLibraryFound = False

try:
    import pigpio
    pigpioLibraryFound = True
except ImportError:
    print('pigpio library not found or pigpiod not running')



    

class ScreenManager(QObject):

    Enabled = True
    ListenForPinEvent = True
    servo = None
    servoInitialized = False

    togglePin = None
    toggleInitialized = False

    buttonPowerPin = None
    btnPowerInitialized = False

    screenGPIO = 252 #this is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one
    screenGPIOInitialized = False

    currentAngle = None    
    currentState = None
    moveSpeed = 0.02

    #Setting angleTestMode to True will skip the slow movement and just set the
    #angles quickly
    angleTestMode = False

    #ranges from 500-2500 but those may not be safe for the servo
    #bottomRange = 600
    #topRange = 2400

    bottomRange = 700  
    topRange = 2400

    #middle is always safe at 1500
    middle = 1500
    pi = None
    
    

    openAngle = 60
    closeAngle = 180
    

    def __init__(self):
        super(ScreenManager, self).__init__()

    def setPin(self, pinConfig):
        self.servo = pinConfig["SERVO"]
        self.togglePin = pinConfig["SCREEN_TOGGLE"]
        self.buttonPowerPin = pinConfig["BUTTON_LED_POWER"]
        self.initialize()

    def processPinEvent(self, pinNum):
        if(self.togglePin == pinNum):
            if(self.currentState != ScreenState.MOVING):
                self.positionToggled()


    def initialize(self):
        print("has IO libraries (screen manager): " + str(hasIOLibraries))
        if(hasIOLibraries and self.btnPowerInitialized == False):
            IO.setmode(IO.BCM)
            IO.setup(self.buttonPowerPin, IO.OUT)
            self.btnPowerInitialized = True
        
        
        if(pigpioLibraryFound and self.servoInitialized == False):           
            self.emit(QtCore.SIGNAL('logEvent'),"servo initialized") 
            self.servoInitialized = True
            self.pi = pigpio.pi()
            
            self.setAngle(90)
            self.currentAngle = 90
            self.openLid()
            self.setCurrentLidState(ScreenState.OPEN)

        
        try:
            subprocess.call(shlex.split("sudo sh -c \"echo " + str(self.screenGPIO) + " > /sys/class/gpio/export\"")) 
            subprocess.call(shlex.split("sudo sh -c \"echo 'out' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/direction\"")) 
        except: 
            print(" no subprocess module")
        
        
        

    def setCurrentLidState(self, state):
        self.currentState = state
        if(self.currentState == ScreenState.OPEN):
            self.toggleButtonPower(True)
            self.changeScreenState(True)
        elif(self.currentState == ScreenState.CLOSED):
            self.toggleButtonPower(False)
            self.changeScreenState(False)

    def toggleButtonPower(self, isOn):
        if(isOn):
            IO.output(self.buttonPowerPin, IO.HIGH)
        else:
            IO.output(self.buttonPowerPin, IO.LOW)

    def changeScreenState(self, isOn):
        state = 0
        if(isOn):
            state = 1
        try:
            subprocess.call(shlex.split("sudo sh -c \"echo '" + str(state) + "' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\"")) 
        except: 
            print(" no subprocess module")
                   
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
         if(self.pi == None):
             self.initPigpio()
         mod = self.getPulseWidth(angle)
         self.pi.set_servo_pulsewidth(self.servo, mod)
         
    def move(self, angle):
         if(self.pi == None):
            self.initPigpio()
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
         self.pi.set_servo_pulsewidth(self.servo, 0)
         return angleTracker
         
     
    def positionToggled(self):     
         print("position toggled   state: " + str(self.currentState))   
         if(pigpioLibraryFound and self.currentState != None):
             if(self.currentState == ScreenState.CLOSED):
                 self.openLid()
             elif(self.currentState == ScreenState.OPEN):
                 self.closeLid()
     
    def getCurrentState(self):
         return self.currentState
  
    def openLid(self):
         if(pigpioLibraryFound):
             if(self.angleTestMode):
                 self.setAngle(self.openAngle)
             elif(self.currentState != ScreenState.MOVING):             
                 self.setCurrentLidState(ScreenState.MOVING)
                 self.currentAngle = self.move(self.openAngle)
             self.setCurrentLidState(ScreenState.OPEN)
             
         
         
    def closeLid(self):
        if(pigpioLibraryFound):
             if(self.angleTestMode):
                 self.setAngle(self.closeAngle)
             elif(self.currentState != ScreenState.MOVING):    
                 self.setCurrentLidState(ScreenState.MOVING)          
                 self.currentAngle = self.move(self.closeAngle)   
             self.setCurrentLidState(ScreenState.CLOSED)     
                         
  
    def dispose(self):
         
         self.emit(QtCore.SIGNAL('logEvent'),"disposing of motor manager")
       
         if(pigpioLibraryFound):
             self.pi.set_servo_pulsewidth(self.servo, 0)
             self.pi.stop()

         

         try: 
             IO.cleanup()
         except Exception:
             self.emit(QtCore.SIGNAL('logEvent'),"Problem disposing of IO in screen manager")

