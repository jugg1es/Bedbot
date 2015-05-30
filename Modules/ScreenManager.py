#!/usr/bin/python


import time
from enum import Enum
import math
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from threading import Timer,Thread,Event
from Modules.Widgets.Popup import *
import os
import sys
import subprocess
import shlex

class ScreenState(Enum):
    CLOSED = 0
    MOVING = 1
    OPEN = 2

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
    toggleInitialized = False

    buttonPowerPin = None

    screenGPIO = None #this is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one
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

    currentAngleTracker = None

    screenPowerPopup = None

    def __init__(self):
        super(ScreenManager, self).__init__()
        try:
            subprocess.Popen(shlex.split("echo Checking if subprocess module is available")) 
        except:
            print("** subprocess module unavailable **")
            self.subprocessAvailable = False

    def setPin(self, pinConfig):
        self.screenGPIO = pinConfig["SCREEN_POWER"]
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
        
        if(hasIOLibraries):
            self.pi = pigpio.pi()
            self.pi.set_mode(self.buttonPowerPin, pigpio.OUTPUT)
            self.toggleButtonPower(False)
            self.setAngle(90)
            self.setCurrentLidState(ScreenState.OPEN)
            self.currentAngleTracker = self.move(self.openAngle)
            print("** OPENED **")
            
        
        

    def setCurrentLidState(self, state):
        self.currentState = state
        
        if(self.currentState == ScreenState.OPEN):
            self.toggleButtonPower(True)
            t = Thread(target=self.changeScreenState, args=(self,True,))
            t.start()
        elif(self.currentState == ScreenState.CLOSED):            
            self.toggleButtonPower(False)
            t = Thread(target=self.changeScreenState, args=(self,False,))
            t.start()
        

    def toggleButtonPower(self, isOn):
        if(isOn):            
            self.pi.write(self.buttonPowerPin,1)
        else:
            self.pi.write(self.buttonPowerPin,0)

    def changeScreenState(self, parent, isOn):
        
        if(parent.subprocessAvailable):
            if(isOn):         
                subprocess.Popen(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio508/value\""))         
            else:
                parent.emit(QtCore.SIGNAL('showPopup'),[self, "Turning Screen Off"])
                offproc = subprocess.Popen(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio508/value\"")) 
                offproc.communicate()
            self.screenPowerPopup.close()

    def setCurrentPopup(self, popup):
        self.screenPowerPopup = popup

    def popupResult(self, name, tag):
        t = Thread(target=self.changeScreenState, args=(self,True,))
        t.start()

     
    def positionToggled(self):     
        currentAngle = self.getCurrentAngle()
        if(currentAngle == self.openAngle or currentAngle == self.closeAngle or currentAngle == 90):
            t = Thread(target=self.togglePosition, args=(self,))
            t.start()
     
    def togglePosition(self, parent):
        ang = self.getCurrentAngle()
        if(ang == self.openAngle):
            parent.setCurrentLidState(ScreenState.CLOSED)
            parent.currentAngleTracker = self.move(self.closeAngle)            
            print("** CLOSED **")
        elif(ang == self.closeAngle):
            parent.setCurrentLidState(ScreenState.OPEN)
            parent.currentAngleTracker = self.move(self.openAngle)            
            print("** OPENED **")

    def getAngleFromPulseWidth(self):
        pw = self.pi.get_servo_pulsewidth(self.servo)
        if(pw == 0):
            return None
        elif(pw == self.middle):
            return 90
        elif(pw >= self.bottomRange and pw < self.middle):		
            adj = float((pw - float(self.bottomRange))) / self.below90Range
            adj = adj * 90
            return int(round(adj))
        elif(pw > self.middle and pw <= self.topRange):
            adj = float((pw - float(self.middle))) / self.above90Range
            adj = (adj * 90) + 90
            return int(round(adj))

    def getCurrentAngle(self):
        pwa = self.getAngleFromPulseWidth()
        if(pwa == None):
            pwa = self.currentAngleTracker
        return pwa

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
        currentAngle = self.getCurrentAngle()
        if(currentAngle == self.openAngle or currentAngle == self.closeAngle or currentAngle == 90):
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
            self.pi.set_servo_pulsewidth(self.servo,0)
            return angleTracker
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
