import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from ButtonManager import *

rpiLibraryFound = False

try:
    import RPi.GPIO as IO
    rpiLibraryFound = True
except ImportError:
    print('Raspberry Pi GPIO library not found')
    

class MotorManager(QObject):
    
    closeSensor = None
    openSensor = None
    angle_delay = 0.009
    
    openAngle = 25
    closeAngle = 190
    
    currentAngle = None
    
    
    isClosed = False
    isOpen = False
    
    def __init__(self, closeSensorPin, openSensorPin):
        super(MotorManager, self).__init__()
        
        if(rpiLibraryFound):
            self.closeSensor = ButtonManager(closeSensorPin)            
            self.connect(self.closeSensor, QtCore.SIGNAL('buttonPressed'), self.closeSensorFired)
            
            self.openSensor = ButtonManager(openSensorPin)
            self.connect(self.openSensor, QtCore.SIGNAL('buttonPressed'), self.openSensorFired)
            
            self.setServoQuickAngle(self.closeAngle)
            self.currentAngle = self.closeAngle;
            self.isClosed = True
    
    def closeSensorFired(self):
        print("lid is closed")
        self.isClosed = True
        self.isOpen = False
        
    def openSensorFired(self):
        print("lid is open")
        self.isOpen = True
        self.isClosed = False

    def set(self, p, value):
        if(rpiLibraryFound):
            try:
                f = open("/sys/class/rpi-pwm/pwm0/" + p, 'w')
                f.write(value)
                f.close()    
            except:
                print("Error writing to: " + p + " value: " + value)


    def openLid(self):
        if(rpiLibraryFound):
            self.isClosed = False
            self.isOpen = False
            self.private_doOpenLid(self.currentAngle, self.openAngle)
            self.currentAngle = self.openAngle
        
        
    def closeLid(self):
        if(rpiLibraryFound):
            self.isClosed = False
            self.isOpen = False
            self.private_doCloseLid(self.currentAngle, self.closeAngle)
            self.currentAngle = self.closeAngle



    def setServoQuickAngle(self, angle):
        set("delayed", "0")
        set("servo_max", "190")
        set("mode", "servo")
        set("active", "1")
        #print("set servo to :" + str(angle))
        set("servo", str(angle))
        time.sleep(1)
        set("active", "0")

    def private_doOpenLid(self, current, targetAngle):
        set("delayed", "0")
        set("servo_max", "190")
        set("mode", "servo")
        set("active", "1")
        print("current: " + str(current))
        angleDiff = current - targetAngle
        for angle in range(angleDiff):
            current = current - 1
            set("servo", str(current))
            time.sleep(self.angle_delay)
            if(self.isOpen):
                break
        time.sleep(1)
        set("active", "0")
        self.isOpen = True
        self.isClosed = False

    def private_doCloseLid(self, current, targetAngle):
        set("delayed", "0")
        set("servo_max", "190")
        set("mode", "servo")
        set("active", "1")
        print("current: " + str(current))
        angleDiff = targetAngle - current
        for angle in range(angleDiff):
            current = current + 1
            set("servo", str(current))
            print("current now: " + str(current))
            time.sleep(self.angle_delay)
            if(self.isClosed):
                break
        time.sleep(1)
        set("active", "0")
        self.isClosed = True
        self.isOpen = False







