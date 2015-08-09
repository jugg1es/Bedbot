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
from Modules.Objects.ScreenState import *
from Helpers.perpetualTimer import perpetualTimer

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

    servo = None

    togglePin = None
    toggleInitialized = False

    buttonPowerPin = None

    """This is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one"""
    screenGPIO = None 
    screenGPIOInitialized = False

    """ Bottom range of pulse width for the servo (minimum is 500, but that may break the servo) """
    bottomRange = 700

    """ Top range of pulse width for the servo (maximum is 2500, but that may break the servo) """
    topRange = 2500

    """Always represents the middle of the servo range of motion, should not be changed from 1500"""
    middle = 1500

    """specifies the amount of time it takes to move the screen (in seconds). Higher is slower, lower is faster"""
    moveSpeed = 0.02

    """_openAngle determines the angle at which the screen is open.  
    This is not really the actual angle, since the angle limits are determined by the 'topRange' and 'bottomRange' values
    """
    openAngle = 60
    """_closeAngle determines the angle at which the screen is closed.  
    This is not really the actual angle, since the angle limits are determined by the 'topRange' and 'bottomRange' values
    """
    closeAngle = 177

    above90Range = topRange - middle
    below90Range = middle - bottomRange

    subprocessAvailable = True

    """Keeps track of the last angle set.  This is necessary because the angle is determined by pulse width, but the PW is 
    set to zero after movement is complete to prevent the servo from constantly trying to correct itself
    """
    currentAngleTracker = None

    audioOffScreenTimoutTimer = None
    
    audioOffScreenTimoutEndTime = None
    
    """10 minutes of no audio before the lid closes"""
    #audioOffScreenTimeoutDuration = 10 * 60
    audioOffScreenTimeoutDuration = 30


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
            print("Screen toggle")
            if(self.currentState == ScreenState.OPEN):
                self.positionToggled(ScreenState.CLOSED)
            elif(self.currentState == ScreenState.CLOSED):
                self.positionToggled(ScreenState.OPEN)


    def initialize(self):
        print("has IO libraries (screen manager): " + str(hasIOLibraries))        
        if(hasIOLibraries):
            self.pi = pigpio.pi()
            self.pi.set_mode(self.buttonPowerPin, pigpio.OUTPUT)
            self.toggleButtonPower(False)
            self.setAngle(90)
            self.setCurrentLidState(ScreenState.OPEN)
            self.currentAngleTracker = self.move(self.openAngle)
            self.audioStatusChange("off")
            
        
    def requestScreenPosition(self, arg):
        if(hasIOLibraries):
            ang = self.getCurrentAngle()
            if(arg == ScreenState.OPEN and ang != self.openAngle):
                self.positionToggled(ScreenState.CLOSED)
            elif(arg == ScreenState.CLOSED and ang != self.closeAngle):
                self.positionToggled(ScreenState.OPEN)
                
    def audioStatusChange(self, arg):
        print("AUDIO STATUS: " + str(arg))
        print("Duration: " + str(self.audioOffScreenTimeoutDuration))
        if(self.audioOffScreenTimoutTimer != None):
            self.audioOffScreenTimoutEndTime = None
            self.audioOffScreenTimoutTimer.cancel()
        if(str(arg) == "off"):
            self.audioOffScreenTimoutEndTime = datetime.datetime.now() + datetime.timedelta(seconds = int(self.audioOffScreenTimeoutDuration))
            self.audioOffScreenTimoutTimer = perpetualTimer(1, self.audioTimoutTimerCallback)
            self.audioOffScreenTimoutTimer.start()          
        else:
            self.audioOffScreenTimoutEndTime = datetime.datetime.now() + datetime.timedelta(seconds = int(self.audioOffScreenTimeoutDuration))

    def audioTimoutTimerCallback(self):
        if(self.audioOffScreenTimoutEndTime != None):
            remaining =self.audioOffScreenTimoutEndTime - datetime.datetime.now()
            print("remaining time left: " + str(remaining))
            if(remaining.seconds <= 0):
                self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "getIsAlarmActive", None, "checkAlarmStatusCallback", "Alarm") 
                 

    def checkAlarmStatusCallback(self, arg):
        val = arg
        if(hasattr(arg, "__len__")):
            val = arg[0]
        print(val)
        if(val == False):
            self.requestScreenPosition(ScreenState.CLOSED)
       

    def setCurrentLidState(self, state):
        self.currentState = state        
        if(self.currentState == ScreenState.OPEN):
            self.audioStatusChange("off")
            self.toggleButtonPower(True)
            t = Thread(target=self.changeScreenState, args=(self,True,))
            t.start()
        elif(self.currentState == ScreenState.CLOSED):            
            self.emit(QtCore.SIGNAL('closeAllPopups'))  
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
                offproc = subprocess.Popen(shlex.split("sudo sh -c \"echo '0' > /sys/class/gpio/gpio508/value\"")) 
                offproc.communicate()
            
    def positionToggled(self, desiredState):     
        currentAngle = self.getCurrentAngle()
        if((currentAngle == self.openAngle and desiredState == ScreenState.CLOSED) or 
           (currentAngle == self.closeAngle and desiredState == ScreenState.OPEN) or currentAngle == 90):
            t = Thread(target=self.togglePosition, args=(self,))
            t.start()
     
    def togglePosition(self, parent):
        ang = self.getCurrentAngle()
        if(ang == self.openAngle):
            parent.setCurrentLidState(ScreenState.CLOSED)
            parent.emit(QtCore.SIGNAL('stopAllAudio'))     
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
        if(self.audioOffScreenTimoutTimer != None):
            self.audioOffScreenTimoutTimer.cancel()
        print("Disposing of ScreenManager")