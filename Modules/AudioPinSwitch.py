
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
import time

hasIOLibraries = False

try:
    import RPi.GPIO as IO
    hasIOLibraries = True
except ImportError:
    print('Raspberry Pi GPIO library not found')




class AudioPinSwitch(QObject):

    Enabled = True    
    ListenForPinEvent = True
    audioPin1 = None
    audioPin2 = None

    audioPinsInitialized = False


    def __init__(self):
        super(AudioPinSwitch, self).__init__()

    def setPin(self, pinConfig):
        self.audioPin1 = pinConfig["AUDIO_ONE_SWITCH"]
        self.audioPin2 = pinConfig["AUDIO_TWO_SWITCH"]
        self.initialize()


    def initialize(self):
        if(hasIOLibraries):
            IO.setmode(IO.BCM)
            IO.setup(self.audioPin1, IO.OUT)
            IO.setup(self.audioPin2, IO.OUT)
            IO.output(self.audioPin1, IO.LOW)
            IO.output(self.audioPin2, IO.LOW)
            self.audioPinsInitialized = True


    def processPinEvent(self, pinNum):
        if(self.audioPinsInitialized):
            if(self.audioPin1 == pinNum or self.audioPin2 == pinNum):
                self.flipRelay(pinNum)

    def flipRelay(self, pin):
        IO.output(pin, IO.HIGH)    
        time.sleep(0.5)
        IO.output(pin, IO.LOW)    


    def dispose(self):
        print("Disposing of Audio Relay switch")
        try: 
            IO.cleanup() 
        except Exception:
            print("Problem disposing of IO in audio relay switch")

        print("disposed of audio relay switch")


