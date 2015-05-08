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
    
    
    def __init__(self, pin):
        super(ButtonManager, self).__init__()
        self.pinNumber = pin
        self.initialized = False
        try:
            IO.setmode(IO.BCM)
            IO.setup(self.pinNumber, IO.IN, pull_up_down = IO.PUD_UP)
            self.initialized = True
        except Exception:
            print('Raspberry Pi GPIO library not found')
            
        if(self.initialized): 
            self.isListening = True
            self.spinupThread()  
            print("Initialized button on pin: " + str(self.pinNumber))
            
    def listenForPush(self, pin, parent):
        try:
            while parent.isListening:
                #IO.wait_for_edge(pin, IO.RISING)           
                inVal = IO.input(pin)
                print(str(inVal))     
                #parent.emit(QtCore.SIGNAL('buttonPressed'))  
                #print("Button pressed at pin: " + str(parent.pinNumber))
                time.sleep(1)
        except Exception:
            print('Error while listening for button, probably during dispose')
            
    def spinupThread(self):
        self.t = Thread(target=self.listenForPush, args=(self.pinNumber,self))
        self.t.start()
            
    def dispose(self):
        self.isListening = False
        try:
            if(self.initialized):
                IO.cleanup()
        except Exception:
            print('Raspberry Pi GPIO library not found')