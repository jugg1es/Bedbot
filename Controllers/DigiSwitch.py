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
        
        self.t = Thread(target=self.switchOperation, args=(self.pinNumber,self))
        self.t.start()
        
        
    def turnOff(self):
        self.isPowerOn = False
        
            
    def turnOn(self):        
        self.isPowerOn = True
            
    def switchOperation(self, pin, parent):
        initialized = False
        try:
            IO.setmode(IO.BCM)
            IO.setup(pin, IO.OUT)
            initialized = True
            
            IO.output(pin, IO.LOW)
            currentState = 0
            
            if(initialized):
                while(parent.disposing == False):
                    if(currentState == 0 and parent.isPowerOn == True):
                        #if power is set to ON and previous state is OFF, set to HIGH
                        IO.output(pin, IO.HIGH)
                        currentState = 1
                    elif(currentState == 1 and parent.isPowerOn == False):
                        #if power is set to OFF and previous state is ON, set to HIGH
                        IO.output(pin, IO.LOW)
                        currentState = 0
                    time.sleep(0.1)
                    
                #When the disposing flag is set to True, it will break and cleanup
                IO.output(pin, IO.LOW)
                IO.cleanup()       
        except Exception:
            print('Raspberry Pi GPIO library not found')    
            
    def dispose(self):        
        self.isPowerOn = False
        self.disposing = True
        