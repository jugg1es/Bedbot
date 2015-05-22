
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.RadioWidget import *

class Radio(QObject):


    UsesAudio = True
    ListenForPinEvent = True
    offButton = None
    onButton = None
    audioRelayPin = None

    audioStatusDisplay =""
    Enabled = True    
    menuOrder = 2
    
    isPlaying = False
    
    widgetVisible = False

    def __init__(self):
        super(Radio, self).__init__()

    def showWidget(self):
        self.radio_widget.setVisible(True)
        self.widgetVisible = True

    def hideWidget(self):
        self.radio_widget.setVisible(False)
        self.widgetVisible = False

    def addMenuWidget(self, parent):
        self.radio_widget = RadioWidget(parent)       
        self.radio_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.radio_widget.setVisible(False)

    def getMenuIcon(self):
        return "icons/radio-tower.svg"

    def getMenuIconSelected(self):
        return "icons/radio-towerSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 65

    def setPin(self, pinConfig):
        self.offButton = pinConfig["OFF_BUTTON"]
        self.onButton = pinConfig["ON_BUTTON"]
        self.audioRelayPin = pinConfig["AUDIO_ONE_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.offButton == pinNum and self.isPlaying == True):
            self.stop()
        elif(self.onButton == pinNum):
            self.play()

    def getAudioStatusDisplay(self):
        return self.audioStatusDisplay

    def play(self):
        if(self.widgetVisible == True):
            print("starting radio")
            self.audioStatusDisplay = str(self.radio_widget.currentFrequency)
            self.isPlaying = True
            self.emit(QtCore.SIGNAL('audioStarted'), self)
            self.emit(QtCore.SIGNAL('pinRequested'), self.audioRelayPin)
                


    def stop(self):
        if(self.isPlaying == True):
            print("stopping radio")
            self.audioStatusDisplay = ""
            self.isPlaying = False
            self.emit(QtCore.SIGNAL('audioStopped'), self)
    
    def dispose(self):
        print("Disposing of Radio")
        try:
            self.stop()
        except:
            print("problem disposing of radio")

