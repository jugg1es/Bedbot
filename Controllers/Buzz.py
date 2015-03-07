import time
from threading import Timer,Thread,Event
from enum import Enum

try:
    import RPi.GPIO as IO
except ImportError:
    print('Raspberry Pi GPIO library not found')

class BuzzerState(Enum):
    ON = 0
    OFF=1

class Buzz:
    
    pinNumber = None
    currentState = BuzzerState.OFF
    buzzThread = None
    IOLibraryFound = False
    
    def __init__(self, pin):
        self.pinNumber = pin
        try:
            IO.setmode(IO.BCM)
            IO.setup(self.pinNumber, IO.OUT)
            self.IOLibraryFound = True
        except Exception:
            print('Raspberry Pi GPIO library not found')
        
    def startBuzzer(self):
        if(self.IOLibraryFound == True):
            if(self.buzzThread != None):
                self.buzzThread.cancel()
                self.buzzThread = None
            self.doBuzz()
        
    def doBuzz(self):
        if(self.buzzThread != None):
            self.buzzThread =  Timer(1,self.doBuzz)
            IO.output(self.pinNumber, True)
            time.sleep(1)
            IO.output(self.pinNumber, False)
            if(self.buzzThread != None):
                self.buzzThread.start()
            else:
                IO.output(self.pinNumber, False)
        else:
            self.stopBuzzer()
        
    def stopBuzzer(self):
        if(self.IOLibraryFound == True):
            if(self.buzzThread != None):
                self.buzzThread.cancel()
                self.buzzThread = None
            try:
                IO.output(self.pinNumber, False)
                IO.cleanup()
            except Exception:
                print("BUZZ: Error stopping")
        