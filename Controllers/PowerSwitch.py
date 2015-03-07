import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject


try:
    import RPi.GPIO as IO
except ImportError:
    print('Raspberry Pi GPIO library not found')
    


class PowerSwitch(QObject):    
    pinNumber = None    
    isPowerOn = False
    
    def __init__(self, pin):
        super(PowerSwitch, self).__init__()
        self.pinNumber = pin
        
    def turnOff(self):
        self.isPowerOn = False
        
            
    def turnOn(self):
        if(self.isPowerOn == False):
            print("Turning ON")
            self.isPowerOn = True
            self.t = Thread(target=self.waitForOff, args=(self.pinNumber,self))
            self.t.start()
            
    def waitForOff(self, pin, parent):
        initialized = False
        try:
            IO.setmode(IO.BCM)
            IO.setup(pin, IO.OUT)
            initialized = True
               
            if(initialized):
                IO.output(pin, IO.HIGH)
                
                #Continue to send HIGH signal until power is explicitly set to off
                while parent.isPowerOn:
                    time.sleep(0.5)
                    
                #Now that power is turned off, switch the output to low and then dispose of it
                IO.output(pin, IO.LOW)
                IO.cleanup()       
        except Exception:
            print('Raspberry Pi GPIO library not found')    
            
    def dispose(self):
        
        self.isPowerOn = False
        try:            
            IO.cleanup()
        except Exception:
            print('Problem cleaning up amplifier controller')