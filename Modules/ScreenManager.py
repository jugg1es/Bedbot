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
    import pigpio
    hasIOLibraries_screen = True
except ImportError:
    print('Raspberry Pi GPIO library not found')


class ScreenManager(QObject):

    Enabled = True
    ListenForPinEvent = True

    servo = None

    togglePin = None
    toggleInitialized = False

    buttonPowerPin = None
    btnPowerInitialized = False

    screenGPIO = 252 #this is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one
    screenGPIOInitialized = False

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

        self.pi = pigpio.pi()
        if(hasIOLibraries_screen and self.btnPowerInitialized == False):
            self.pi.set_mode(self.buttonPowerPin, pigpio.OUTPUT)

            #IO.setmode(IO.BCM)
            #IO.setup(self.buttonPowerPin, IO.OUT)
            self.btnPowerInitialized = True
            self.toggleButtonPower(False)
        
        
        

        subprocess.Popen(shlex.split("sudo sh -c \"echo " + str(self.screenGPIO) + " > /sys/class/gpio/export\"")) 
        subprocess.Popen(shlex.split("sudo sh -c \"echo 'out' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/direction\""))

        time.sleep(0.5)
        '''
        try:
            subprocess.Popen(shlex.split("sudo python " + self.servoScriptFile))
            self.openLid()
            self.setCurrentLidState(ScreenState.OPEN)
        except: 
            print("problem using subprocess")
        '''


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
            self.pi.write(self.buttonPowerPin,1)
            #IO.output(self.buttonPowerPin, IO.HIGH)
        else:
            self.pi.write(self.buttonPowerPin,0)
            #IO.output(self.buttonPowerPin, IO.LOW)

    def changeScreenState(self, isOn):
        if(isOn):
            subprocess.Popen(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))
            #t = Thread(target=self._turnScreenOn, args=(self,))
            #t.start()
            #subprocess.call(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))
        else:
            subprocess.Popen(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))  
            #t = Thread(target=self._turnScreenOff, args=(self,))
            #t.start()
            #subprocess.call(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))       
    
     
    def positionToggled(self):     
         print("position toggled   state: " + str(self.currentState))   
         if(self.currentState != None):
             if(self.currentState == ScreenState.CLOSED):
                 self.openLid()
             elif(self.currentState == ScreenState.OPEN):
                 self.closeLid()
     
    def getCurrentState(self):
         return self.currentState
  
    def openLid(self):
        subprocess.Popen(shlex.split("sudo python " + self.servoScriptFile + " open" ))
        #time.sleep(0.5)
        self.setCurrentLidState(ScreenState.OPEN)
             
         
      
    def closeLid(self):
        subprocess.Popen(shlex.split("sudo python " + self.servoScriptFile + " close"))
        #time.sleep(0.5)
        self.setCurrentLidState(ScreenState.CLOSED)     

    def dispose(self):
        
        print("disposing of screen manager pins")
        try: 
            IO.cleanup() 
        except Exception:
            print("Problem disposing of IO in screen manager")

        print("disposed screen manager")

