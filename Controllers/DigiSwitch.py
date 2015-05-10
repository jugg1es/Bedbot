import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject


try:
    import RPi.GPIO as IO
except ImportError:
    print('Raspberry Pi GPIO library not found')
    


class DigiSwitch(QObject):    
    pinNumber = None    
    isPowerOn = False
    disposing = False
    
    def __init__(self, pin):
        super(DigiSwitch, self).__init__()
        self.pinNumber = pin
        self.isPowerOn = False
        
        self.initialized = False
        
        try:
            IO.setmode(IO.BCM)
            IO.setup(pin, IO.OUT)
            self.initialized = True
            self.turnOff()
            
        except Exception:
            print('Cannot initialize button power switch')   
            
        
        
        
    def turnOff(self):
        self.isPowerOn = False
        if(self.initialized):
            IO.output(self.pinNumber, IO.LOW)            
        
            
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
        