
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event


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
            self.audioPinsInitialized = True


    def processPinEvent(self, pinNum):
        if(self.audioPinsInitialized):
            if(self.audioPin1 == pinNum or self.audioPin2 == pinNum):
                self.flipRelay(pinNum)

    def flipRelay(self, pin):
        IO.output(pin, IO.HIGH)    
        time.sleep(0.2)
        IO.output(pin, IO.LOW)    


    def dispose(self):
        print("Disposing of Radio")

