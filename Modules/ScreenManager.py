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
    """Controls the servo that lifts the screen up/down, the button LEDs and the screen backlight power"""

    Enabled = True
    ListenForPinEvent = True

    _servo = None

    _togglePin = None
    _toggleInitialized = False

    _buttonPowerPin = None

    """This is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one"""
    _screenGPIO = None 
    screenGPIOInitialized = False

    """ Bottom range of pulse width for the servo (minimum is 500, but that may break the servo) """
    _bottomRange = 700

    """ Top range of pulse width for the servo (minimum is 2500, but that may break the servo) """
    _topRange = 2500

    """Always represents the middle of the servo range of motion, should not be changed from 1500"""
    _middle = 1500

    """specifies the amount of time it takes to move the screen (in seconds). Higher is slower, lower is faster"""
    _moveSpeed = 0.02

    """_openAngle determines the angle at which the screen is open.  
    This is not really the actual angle, since the angle limits are determined by the 'topRange' and 'bottomRange' values
    """
    _openAngle = 60
    """_closeAngle determines the angle at which the screen is closed.  
    This is not really the actual angle, since the angle limits are determined by the 'topRange' and 'bottomRange' values
    """
    _closeAngle = 177

    _above90Range = _topRange - _middle
    _below90Range = _middle - _bottomRange

    _subprocessAvailable = True

    """Keeps track of the last angle set.  This is necessary because the angle is determined by pulse width, but the PW is 
    set to zero after movement is complete to prevent the servo from constantly trying to correct itself
    """
    _currentAngleTracker = None


    def __init__(self):
        super(ScreenManager, self).__init__()
        try:
            subprocess.Popen(shlex.split("echo Checking if subprocess module is available")) 
        except:
            print("** subprocess module unavailable **")
            self._subprocessAvailable = False

    def setPin(self, pinConfig):
        print("setting pins: " + str(pinConfig["SERVO"]))
        self._screenGPIO = pinConfig["SCREEN_POWER"]
        self._servo = pinConfig["SERVO"]
        self._togglePin = pinConfig["SCREEN_TOGGLE"]
        self._buttonPowerPin = pinConfig["BUTTON_LED_POWER"]
        self.initialize()

    def processPinEvent(self, pinNum):
        print("process pin event: " + str(pinNum))
        if(self._togglePin == pinNum):
            if(self.currentState != ScreenState.MOVING):
                self.positionToggled()


    def initialize(self):
        print("has IO libraries (screen manager): " + str(hasIOLibraries))
        
        if(hasIOLibraries):
            self.pi = pigpio.pi()
            self.pi.set_mode(self._buttonPowerPin, pigpio.OUTPUT)
            self.toggleButtonPower(False)
            self.setAngle(90)
            self.setCurrentLidState(ScreenState.OPEN)
            self._currentAngleTracker = self.move(self._openAngle)
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
            self.pi.write(self._buttonPowerPin,1)
        else:
            self.pi.write(self._buttonPowerPin,0)

    def changeScreenState(self, parent, isOn):
        
        if(parent._subprocessAvailable):
            if(isOn):         
                subprocess.Popen(shlex.split("sudo sh -c \"echo '1' > /sys/class/gpio/gpio508/value\""))         
            else:
                offproc = subprocess.Popen(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio508/value\"")) 
                offproc.communicate()
            
     
    def positionToggled(self):     
        currentAngle = self.getCurrentAngle()
        if(currentAngle == self._openAngle or currentAngle == self._closeAngle or currentAngle == 90):
            t = Thread(target=self.togglePosition, args=(self,))
            t.start()
     
    def togglePosition(self, parent):
        ang = self.getCurrentAngle()
        if(ang == self._openAngle):
            parent.setCurrentLidState(ScreenState.CLOSED)
            parent.emit(QtCore.SIGNAL('stopAllAudio'))     
            parent._currentAngleTracker = self.move(self._closeAngle)       
            print("** CLOSED **")
        elif(ang == self._closeAngle):
            parent.setCurrentLidState(ScreenState.OPEN)
            parent._currentAngleTracker = self.move(self._openAngle)            
            print("** OPENED **")

    def getAngleFromPulseWidth(self):
        pw = self.pi.get_servo_pulsewidth(self._servo)
        if(pw == 0):
            return None
        elif(pw == self._middle):
            return 90
        elif(pw >= self._bottomRange and pw < self._middle):		
            adj = float((pw - float(self._bottomRange))) / self._below90Range
            adj = adj * 90
            return int(round(adj))
        elif(pw > self._middle and pw <= self._topRange):
            adj = float((pw - float(self._middle))) / self._above90Range
            adj = (adj * 90) + 90
            return int(round(adj))

    def getCurrentAngle(self):
        pwa = self.getAngleFromPulseWidth()
        if(pwa == None):
            pwa = self._currentAngleTracker
        return pwa

    def getPulseWidth(self, angle):	
        mod = self._middle
        if(angle > 90 and angle <= 180):		
            percent = float((angle - 90)) / 90
            mod = math.trunc(self._middle + (float(percent) * self._above90Range))
        elif(angle < 90 and angle >= 0):
            percent = float(angle) / 90
            mod = math.trunc(self._bottomRange + (float(percent) * self._below90Range))
        return mod

    def setAngle(self, angle):
        mod = self.getPulseWidth(angle)
        self.pi.set_servo_pulsewidth(self._servo, mod)


    def move(self, angle):
        currentAngle = self.getCurrentAngle()
        if(currentAngle == self._openAngle or currentAngle == self._closeAngle or currentAngle == 90):
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
                time.sleep(self._moveSpeed)
            self.pi.set_servo_pulsewidth(self._servo,0)
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
