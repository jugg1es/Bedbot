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
    OPEN = 1

hasIOLibraries = False

try:
    import pigpio
    hasIOLibraries = True
except ImportError:
    print('PIGPIO library not found')


class ScreenManager(QObject):

    Enabled = True
    ListenForPinEvent = True

    servo = None
    togglePin = None
    buttonPowerPin = None

    screenGPIO = None #this is dependent on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one
    screenGPIOInitialized = False

    bottomRange = 700
    topRange = 2500
    middle = 1500
    moveSpeed = 0.02

    openAngle = 60
    closeAngle = 177

    above90Range = topRange - middle
    below90Range = middle - bottomRange
    
    subprocessAvailable = True

    savedPreviousPulseWidth = None

    initAngle = closeAngle - openAngle

    def __init__(self):
        super(ScreenManager, self).__init__()
        try:
            subprocess.Popen(shlex.split("echo Checking if subprocess module is available")) 
        except:
            print("** subprocess module unavailable **")
            self.subprocessAvailable = False

    def setPin(self, pinConfig):
        self.servo = pinConfig["SERVO"]
        self.togglePin = pinConfig["SCREEN_TOGGLE"]
        self.buttonPowerPin = pinConfig["BUTTON_LED_POWER"]
        self.screenGPIO = pinConfig["SCREEN_POWER"]
        self.initialize()

    def processPinEvent(self, pinNum):
        if(self.togglePin == pinNum):
            self.positionToggled()


    def initialize(self):
        print("has IO libraries (screen manager): " + str(hasIOLibraries))

        if(self.subprocessAvailable):
            subprocess.Popen(shlex.split("sudo sh -c \"echo " + str(self.screenGPIO) + " > /sys/class/gpio/export\"")) 
            subprocess.Popen(shlex.split("sudo sh -c \"echo 'out' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/direction\""))      


        if(hasIOLibraries):
            self.pi = pigpio.pi()
            self.pi.set_mode(self.buttonPowerPin, pigpio.OUTPUT)
            self.toggleButtonPower(False)
            
            print("setting to initial angle: " + str(self.initAngle))
            self.setAngle(self.initAngle)
            time.sleep(0.5)
            self.move(self.openAngle)
            self.setCurrentLidState(ScreenState.OPEN)
        
        

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
        else:
            self.pi.write(self.buttonPowerPin,0)

    def changeScreenState(self, isOn):
        if(self.subprocessAvailable):
            if(isOn):
                subprocess.Popen(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))
            else:
                subprocess.Popen(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""))      
    
     
    def positionToggled(self):     
        
        currentAngle = self.getAngleFromPulseWidth()
        print("checking if toggling possible  current angle: " + str(currentAngle))
        if(currentAngle == self.openAngle or currentAngle == self.closeAngle or currentAngle == self.initAngle):
            print("now toggling ")
            self.savedPreviousPulseWidth = None
            t = Thread(target=self.togglePosition, args=(self,))
            t.start()
     
    def togglePosition(self, parent):
        ang = parent.getAngleFromPulseWidth()
        if(ang == self.openAngle):
            self.move(self.closeAngle)
            self.setCurrentLidState(ScreenState.CLOSED)
        elif(ang == self.closeAngle):
            self.move(self.openAngle)
            self.setCurrentLidState(ScreenState.OPEN)
        parent.savedPreviousPulseWidth = self.pi.get_servo_pulsewidth(self.servo)
        self.pi.set_servo_pulsewidth(self.servo,0)

    def getAngleFromPulseWidth(self):
        pw = None
        if(self.savedPreviousPulseWidth != None):
            pw = self.savedPreviousPulseWidth
        else:
            pw = self.pi.get_servo_pulsewidth(self.servo)
        print(pw)
        if(pw == self.middle):
            return 90
        elif(pw >= self.bottomRange and pw < self.middle):		
            adj = float((pw - float(self.bottomRange))) / self.below90Range
            adj = adj * 90
            return int(round(adj))
        elif(pw > self.middle and pw <= self.topRange):
            adj = float((pw - float(self.middle))) / self.above90Range
            adj = (adj * 90) + 90
            return int(round(adj))


    def getPulseWidth(self, angle):	
        mod = self.middle
        if(angle > 90 and angle <= 180):		
            percent = float((angle - 90)) / 90
            mod = math.trunc(self.middle + (float(percent) * self.above90Range))
        elif(angle < 90 and angle >= 0):
            percent = float(angle) / 90
            mod = math.trunc(self.bottomRange + (float(percent) * self.below90Range))
        return mod

    def setAngle(self, angle):
        mod = self.getPulseWidth(angle)
        self.pi.set_servo_pulsewidth(self.servo, mod)


    def move(self, angle):
        currentAngle = self.getAngleFromPulseWidth()
        if(currentAngle == self.openAngle or currentAngle == self.closeAngle or currentAngle ==  self.initAngle):
            #print("current angle: " + str(currentAngle))
            angleDiff = currentAngle - angle
            angleTracker = currentAngle
            angleDir = 0
            if(angleDiff < 0):
                angleDir = 1
            elif(angleDiff > 0):
                angleDir = -1
            for angle in range(abs(angleDiff)):		
                angleTracker += angleDir		
                self.setAngle(angleTracker)	
                time.sleep(self.moveSpeed)
            return currentAngle
        return None

    def dispose(self):
        
        print("disposing of screen manager pins")
        '''
        try: 
            IO.cleanup() 
        except Exception:
            print("Problem disposing of IO in screen manager")

        print("disposed screen manager")
        '''

