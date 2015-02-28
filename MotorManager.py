import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject


try:
    import RPi.GPIO as IO
except ImportError:
    print('Raspberry Pi GPIO library not found')
    

class MotorManager(QObject):
    
    pinNumber = None
    readyToMove = False
    
    enablePin = None
    coilA1Pin = None
    coilA2Pin = None
    coilB1Pin = None
    coilB2Pin = None
    tiltPin = None
    
    positionUp = False
    
    stepDelay = .002 #in milliseconds
    totalSteps = 1028
    
    def __init__(self, enablePin, a1Pin, a2Pin, b1Pin, b2Pin, tiltPin):
        super(MotorManager, self).__init__()
                
        
        self.enablePin = enablePin
        self.coilA1Pin = a1Pin
        self.coilA2Pin = a2Pin
        self.coilB1Pin = b1Pin
        self.coilB2Pin = b2Pin
        #self.tiltPin = tiltPin
        
        
        initialized = False
        try:
            IO.setmode(IO.BCM)
            IO.setup(self.enablePin, IO.OUT)
            IO.setup(self.coilA1Pin, IO.OUT)
            IO.setup(self.coilA2Pin, IO.OUT)
            IO.setup(self.coilB1Pin, IO.OUT)
            IO.setup(self.coilB2Pin, IO.OUT)
            #IO.setup(self.tiltPin, IO.IN)
            initialized = True
        except Exception:
            print('Raspberry Pi GPIO library not found')
            
        if(initialized): 
            self.readyToMove = True
            IO.output(self.enablePin, 1)
            
    def togglePosition(self):
        if(self.readyToMove):
            if(self.positionUp):
                print("going down")
                self.goDown()
            else:
                print("going up")
                self.goUp()
            
    def goUp(self):
        self.readyToMove = False
        for i in range(0, self.totalSteps):
            self.setStep(1, 0, 1, 0)
            time.sleep(self.stepDelay)
            self.setStep(0, 1, 1, 0)
            time.sleep(self.stepDelay)
            self.setStep(0, 1, 0, 1)
            time.sleep(self.stepDelay)
            self.setStep(1, 0, 0, 1)
            time.sleep(self.stepDelay)
        self.readyToMove = True
            
    def goDown(self):
        self.readyToMove = False
        for i in range(0, self.totalSteps):
            self.setStep(1, 0, 0, 1)
            time.sleep(self.stepDelay)
            self.setStep(0, 1, 0, 1)
            time.sleep(self.stepDelay)
            self.setStep(0, 1, 1, 0)
            time.sleep(self.stepDelay)
            self.setStep(1, 0, 1, 0)
            time.sleep(self.stepDelay)
            
        self.readyToMove = True
            
    def setStep(self, w1, w2, w3, w4):
        IO.output(self.coilA1Pin, w1)
        IO.output(self.coilA2Pin, w2)
        IO.output(self.coilB1Pin, w3)
        IO.output(self.coilB2Pin, w4)
    
            
    def dispose(self):
        self.readyToMove = False
        try:
            IO.cleanup()
        except Exception:
            print('Raspberry Pi GPIO library not found')