
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.PlaybackWidget import *

class Playback(QObject):

    Enabled = True    
    menuOrder = 1

    ListenForPinEvent = True

    audioOnPin = None
    audioOffPin = None

    audioSwitchOnePin = None
    audioSwitchTwoPin = None

    def __init__(self):
        super(Playback, self).__init__()

    def showWidget(self):
        print("showing playback")
        self.playback_widget.setVisible(True)
    def hideWidget(self):
        print("hiding playback")
        self.playback_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.playback_widget = PlaybackWidget(parent)       
        self.playback_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.playback_widget.setVisible(False)
        self.playback_widget.initialize()

    def getMenuIcon(self):
        return "icons/connection.svg"

    def getMenuIconSelected(self):
        return "icons/connectionSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 70

    def setPin(self, pinConfig):
        self.audioOnPin =  pinConfig["ON_BUTTON"]
        self.audioOffPin =  pinConfig["OFF_BUTTON"]
        self.audioSwitchOnePin =  pinConfig["AUDIO_ONE_SWITCH"]
        self.audioSwitchTwoPin =  pinConfig["AUDIO_TWO_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.audioOnPin == pinNum):
            print("audio on")
        elif(self.audioOffPin == pinNum):
            print("audio off")

   


    def dispose(self):
        print("Disposing of Alarm")

