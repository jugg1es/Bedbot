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
            IO.setup(self.pinNumber, IO.IN)
            self.initialized = True
        except Exception:
            print('Raspberry Pi GPIO library not found')
            
        if(self.initialized): 
            self.isListening = True
            self.spinupThread()  
            
    def listenForPush(self, pin, parent):
        lastInput = -1
        while parent.isListening:
            ioinput = IO.input(pin)
            if((not lastInput) and ioinput and lastInput != -1):
                parent.emit(QtCore.SIGNAL('buttonPressed'))  
            lastInput = ioinput
            time.sleep(0.1)
            
    def spinupThread(self):
        self.t = Thread(target=self.listenForPush, args=(self.pinNumber,self))
        self.t.start()
            
    def dispose(self):
        self.isListening = False
        time.sleep(0.2)
        try:
            if(self.initialized):
                IO.cleanup()
        except Exception:
            print('Raspberry Pi GPIO library not found')