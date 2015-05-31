
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
import time

hasIOLibraries = False

try:
    import pigpio
    hasIOLibraries = True
except ImportError:
    print('PIGPIO library not found')




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
            self.pi = pigpio.pi()
            self.pi.set_mode(self.audioPin1, pigpio.OUTPUT)
            self.pi.set_mode(self.audioPin2, pigpio.OUTPUT)
            self.doDisablePins()
            self.audioPinsInitialized = True


    def processPinEvent(self, pinNum):
        if(self.audioPinsInitialized):
            if(self.audioPin1 == pinNum):
                self.pi.write(self.audioPin2,0)
                self.pi.write(self.audioPin1,1)
            elif(self.audioPin2 == pinNum):
                self.pi.write(self.audioPin1,0)
                self.pi.write(self.audioPin2,1)
            self.doDisablePins()

    def doDisablePins(self):
        t = Thread(target=self._disablePins, args=(self,))        
        t.start()

    def _disablePins(self, parent):
        time.sleep(0.5)
        self.pi.write(self.audioPin1,0)
        self.pi.write(self.audioPin2,0)

    def dispose(self):
        print("disposed of audio relay switch")


