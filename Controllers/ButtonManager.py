import time
from threading import Thread
from enum import Enum
from PyQt4 import QtCore
from PyQt4.QtCore import QObject


try:
    import RPi.GPIO as IO
except ImportError:
    print('Raspberry Pi GPIO library not found')
    


class ButtonManager(QObject):
    
    pinNumber = None
    isListening = False
    bounceTime = 300
    
    def buttonPressed(self, channel):
        self.emit(QtCore.SIGNAL('buttonPressed'))  
        print("Button pressed at pin: " + str(self.pinNumber))
    
    def __init__(self, pin, bounceTime):
        super(ButtonManager, self).__init__()
        self.pinNumber = pin
        self.initialized = False
        self.bounceTime = bounceTime
        try:
            IO.setmode(IO.BCM)
            IO.setup(self.pinNumber, IO.IN, pull_up_down = IO.PUD_DOWN)
            self.initialized = True
        except Exception:
            print('Raspberry Pi GPIO library not found')
            
        if(self.initialized): 
            self.isListening = True
            IO.add_event_detect(self.pinNumber, IO.RISING, callback=self.buttonPressed, bouncetime=self.bounceTime)
            print("Initialized button on pin: " + str(self.pinNumber))
    
    
        
    def dispose(self):
        self.isListening = False        
        
        try:            
            IO.remove_event_detect(self.pinNumber)
            IO.cleanup()
        except Exception:
            print('Raspberry Pi GPIO library not found')