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

    angle_delay = 0.02

    openAngle = 65
    closeAngle = 195

    
    
    
    def __init__(self):
        super(MotorManager, self).__init__()
        
        if(rpiLibraryFound):
            
            startAngle = self.openAngle + int(round((self.closeAngle - self.openAngle)/2))
            self.setServoQuickAngle(startAngle)
            self.currentAngle = startAngle;
            self.openLid()
            
    
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
            self.emit(QtCore.SIGNAL('turnScreenOn'))  
            self.currentState = ScreenState.MOVING
            t = Thread(target=self.private_doOpenLid, args=(self.currentAngle, self.openAngle, self))
            t.start()
            self.currentAngle = self.openAngle
        
        
    def closeLid(self):
        if(rpiLibraryFound and self.currentState != ScreenState.MOVING):
            self.emit(QtCore.SIGNAL('turnScreenOff')) 
            self.currentState = ScreenState.MOVING
            t = Thread(target=self.private_doCloseLid, args=(self.currentAngle, self.closeAngle, self))
            t.start()
            self.currentAngle = self.closeAngle



    def setServoQuickAngle(self, angle):
        self.setPWMValue("delayed", "0")
        self.setPWMValue("servo_max", str(self.closeAngle))
        self.setPWMValue("mode", "servo")
        self.setPWMValue("active", "1")
        #print("set servo to :" + str(angle))
        self.setPWMValue("servo", str(angle))
        time.sleep(1)
        self.setPWMValue("active", "0")
        

    def private_doOpenLid(self, current, targetAngle, parent):
        set("delayed", "0")
        set("servo_max", str(self.closeAngle))
        set("mode", "servo")
        set("active", "1")
        angleDiff = current - targetAngle
        for angle in range(angleDiff):
            current = current - 1
            set("servo", str(current))
            time.sleep(angle_delay)
        set("active", "0")

    def private_doCloseLid(self, current, targetAngle, parent):
        set("delayed", "0")
        set("servo_max", str(closeAngle))
        set("mode", "servo")
        set("active", "1")
        angleDiff = targetAngle - current
        for angle in range(angleDiff):
            current = current + 1
            set("servo", str(current))
            time.sleep(angle_delay)
        set("active", "0")


    def dispose(self):
        print("disposing of motor manager")
        




