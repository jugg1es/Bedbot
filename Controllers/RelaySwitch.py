import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject


try:
    import RPi.GPIO as IO
except ImportError:
    print('Raspberry Pi GPIO library not found')
    


class RelaySwitch(QObject):    
    pinNumber1 = None     
    pinNumber2 = None   
    
    currentState = 1
    
    
    def __init__(self, pin1, pin2):
        super(RelaySwitch, self).__init__()
        self.pinNumber1 = pin1
        self.pinNumber2 = pin2
        
        
        self.initialized = False
        
        try:
            IO.setmode(IO.BCM)
            IO.setup(self.pinNumber1, IO.OUT)
            IO.setup(self.pinNumber2, IO.OUT)
            self.initialized = True
            self.setState(1)
            
        except Exception:
            print('Cannot initialize button power switch')   
            
        
        
        
    def setState(self, state):
        self.currentState = state
        if(self.initialized):
            IO.output(self.pinNumber, IO.LOW)            
        
    
    def sendSignal(self, pin):
        print("send signal to " + str(pin))
        
    def turnOn(self):        
        self.isPowerOn = True
        if(self.initialized):
            IO.output(self.pinNumber, IO.HIGH)    
            

    def dispose(self):        
        self.isPowerOn = False
        self.disposing = True
        try:
            IO.output(self.pinNumber, IO.LOW) 
            IO.cleanup()            
        except Exception:
            print('Raspberry Pi GPIO library not found')    
        