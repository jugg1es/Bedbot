#!/usr/bin/python


import time
from enum import Enum
import math
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from threading import Timer,Thread,Event
import os
import sys
import subprocess
import shlex

class ScreenState(Enum):
    CLOSED = 0
    MOVING = 1
    OPEN = 2

hasIOLibraries_screen = False

try:
    import RPi.GPIO as IO
    hasIOLibraries_screen = True
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

    screenGPIO = 508 #this is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one
    screenGPIOInitialized = False

    currentAngle = None    
    currentState = None


    '''
    moveSpeed = 0.02

    #Setting angleTestMode to True will skip the slow movement and just set the
    #angles quickly
    angleTestMode = False

    #ranges from 500-2500 but those may not be safe for the servo
    bottomRange = 600  
    topRange = 2400

    #middle is always safe at 1500
    middle = 1500
    pi = None
    '''
    

    openAngle = 60
    closeAngle = 175


    servoScriptFile = "Scripts/servo.py"

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
        print("has IO libraries (screen manager): " + str(hasIOLibraries_screen))
        if(hasIOLibraries_screen and self.btnPowerInitialized == False):
            IO.setmode(IO.BCM)
            IO.setup(self.buttonPowerPin, IO.OUT)
            self.btnPowerInitialized = True
            self.toggleButtonPower(False)
        
        
        

        t = Thread(target=self._initializeScreenToggle, args=(self,))
        t.start()

        

        
        if(pigpioLibraryFound and self.servoInitialized == False):           
            self.emit(QtCore.SIGNAL('logEvent'),"servo initialized") 
            self.servoInitialized = True
            
            subprocess.Popen(shlex.split(self.servoScriptFile + " init"))
            #self.setAngle(90)


            self.currentAngle = 90
            self.openLid()
            self.setCurrentLidState(ScreenState.OPEN)

        
        
        
    def _initializeScreenToggle(self, parent):
        try:
            subprocess.Popen(shlex.split("sudo sh -c \"echo " + str(parent.screenGPIO) + " > /sys/class/gpio/export\"")) 
            subprocess.Popen(shlex.split("sudo sh -c \"echo 'out' > /sys/class/gpio/gpio" + str(parent.screenGPIO) + "/direction\""))  
        except:
            print("error changing screen state")

    def _turnScreenOn(self, parent):
        try:
            subprocess.Popen(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio" + str(parent.screenGPIO) + "/value\""))   
        except:
            print("error changing screen state")

    def _turnScreenOff(self, parent):
        try:
            subprocess.Popen(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio" + str(parent.screenGPIO) + "/value\""))   
        except:
            print("error changing screen state")

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
        if(isOn):
            t = Thread(target=self._turnScreenOn, args=(self,))
            t.start()
            #subprocess.call(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))
        else:
            t = Thread(target=self._turnScreenOff, args=(self,))
            t.start()
            #subprocess.call(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))       
    
     
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
             else:
                 subprocess.Popen(shlex.split(self.servoScriptFile + " open " + str(self.currentAngle)))
                 self.currentAngle = self.openAngle
             self.setCurrentLidState(ScreenState.OPEN)
             
         
      
    def closeLid(self):
        if(pigpioLibraryFound):
             if(self.angleTestMode):
                 self.setAngle(self.closeAngle)
             else:
                 subprocess.Popen(shlex.split(self.servoScriptFile + " close " + str(self.currentAngle)))
                 self.currentAngle = self.closeAngle
             self.setCurrentLidState(ScreenState.CLOSED)     

    def dispose(self):
        
        print("disposing of screen manager pins")
        try: 
            IO.cleanup() 
        except Exception:
            print("Problem disposing of IO in screen manager")

        print("disposed screen manager")

