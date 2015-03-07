import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from Controllers.ButtonManager import *

rpiLibraryFound = False

class ScreenState(Enum):
    CLOSED = 0
    MOVING =1
    OPEN =2

try:
    import RPi.GPIO as IO
    rpiLibraryFound = True
except ImportError:
    print('Raspberry Pi GPIO library not found')
    

class MotorManager(QObject):
        
    currentAngle = None    
    currentState = None
    closeSensor = None
    openSensor = None
    
    openAngle = 25
    closeAngle = 190
    angle_delay = 0.01
    
    
    
    def __init__(self, closeSensorPin, openSensorPin):
        super(MotorManager, self).__init__()
        
        if(rpiLibraryFound):
            self.closeSensor = ButtonManager(closeSensorPin)            
            self.connect(self.closeSensor, QtCore.SIGNAL('buttonPressed'), self.closeSensorFired)
            
            self.openSensor = ButtonManager(openSensorPin)
            self.connect(self.openSensor, QtCore.SIGNAL('buttonPressed'), self.openSensorFired)
            
            self.setServoQuickAngle(self.closeAngle)
            self.currentAngle = self.closeAngle;
            
            self.currentState = ScreenState.CLOSED
    
    def positionToggled(self):
        if(rpiLibraryFound and self.currentState != None):
            if(self.currentState == ScreenState.CLOSED):
                print("SCREEN OPENING...")
                self.openLid()
            elif(self.currentState == ScreenState.OPEN):
                print("SCREEN CLOSING...")
                self.closeLid()
    
    def getCurrentState(self):
        return self.currentState
    
    def closeSensorFired(self):
        print("lid sensor says closed")
        self.currentState = ScreenState.CLOSED
        
    def openSensorFired(self):
        print("lid sensor says open")
        self.currentState = ScreenState.OPEN

    def setPWMValue(self, p, value):
        if(rpiLibraryFound):
            try:
                f = open("/sys/class/rpi-pwm/pwm0/" + p, 'w')
                f.write(value)
                f.close()    
            except:
                print("Error writing to: " + p + " value: " + value)


    def openLid(self):
        if(rpiLibraryFound and self.currentState != ScreenState.MOVING):
            self.currentState = ScreenState.MOVING
            t = Thread(target=self.private_doOpenLid, args=(self.currentAngle, self.openAngle, self))
            t.start()
            self.currentAngle = self.openAngle
        
        
    def closeLid(self):
        if(rpiLibraryFound and self.currentState != ScreenState.MOVING):
            self.currentState = ScreenState.MOVING
            t = Thread(target=self.private_doCloseLid, args=(self.currentAngle, self.closeAngle, self))
            t.start()
            self.currentAngle = self.closeAngle



    def setServoQuickAngle(self, angle):
        self.setPWMValue("delayed", "0")
        self.setPWMValue("servo_max", "190")
        self.setPWMValue("mode", "servo")
        self.setPWMValue("active", "1")
        #print("set servo to :" + str(angle))
        self.setPWMValue("servo", str(angle))
        time.sleep(1)
        self.setPWMValue("active", "0")
        

    def private_doOpenLid(self, current, targetAngle, parent):
        self.setPWMValue("delayed", "0")
        self.setPWMValue("servo_max", "190")
        self.setPWMValue("mode", "servo")
        self.setPWMValue("active", "1")
        angleDiff = current - targetAngle
        for angle in range(angleDiff):
            current = current - 1
            self.setPWMValue("servo", str(current))
            time.sleep(self.angle_delay)
            if(parent.currentState == ScreenState.OPEN):
                break
        time.sleep(1)
        self.setPWMValue("active", "0")
        parent.currentState = ScreenState.OPEN

    def private_doCloseLid(self, current, targetAngle, parent):
        self.setPWMValue("delayed", "0")
        self.setPWMValue("servo_max", "190")
        self.setPWMValue("mode", "servo")
        self.setPWMValue("active", "1")
        angleDiff = targetAngle - current
        for angle in range(angleDiff):
            current = current + 1
            self.setPWMValue("servo", str(current))
            time.sleep(self.angle_delay)
            if(parent.currentState == ScreenState.CLOSED):
                break
        time.sleep(1)
        self.setPWMValue("active", "0")
        parent.currentState = ScreenState.CLOSED


    def dispose(self):
        try:
            self.closeSensor.dispose()
        except Exception:
            print("Problem disposing of close sensor")
            
        try:
            self.openSensor.dispose()
        except Exception:
            print("Problem disposing of open sensor")
        




