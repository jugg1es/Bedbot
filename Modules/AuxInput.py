#!/usr/bin/python


from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.AuxWidget import *


class AuxInput(QObject):
    menuOrder = 3
    Enabled = True    

    UsesAudio = True
    ListenForPinEvent = True
    audioRelayPin = None
    onButton = None
    audioStatusDisplay = "AUX"

    isVisible = False

    def __init__(self):
        super(AuxInput, self).__init__()

    def showWidget(self):
        self.isVisible = True
        self.aux_widget.setVisible(True)
        self.showButtonIndicators()

    def hideWidget(self):
        self.isVisible = False
        self.aux_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.aux_widget = AuxWidget(parent)       
        self.aux_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.aux_widget.setVisible(False)

    def getMenuIcon(self):
        return "icons/ipod.svg"

    def getMenuIconSelected(self):
        return "icons/ipodSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 65
    def getAudioStatusDisplay(self):
        return self.audioStatusDisplay
    def setPin(self, pinConfig):
        self.onButton = pinConfig["ON_BUTTON"]
        self.audioRelayPin = pinConfig["AUDIO_TWO_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.onButton == pinNum and self.isVisible == True):
            print("requested aux pin")
            self.emit(QtCore.SIGNAL('pinRequested'), self.audioRelayPin)
            self.emit(QtCore.SIGNAL('audioStarted'), self)
            

    def showButtonIndicators(self):
        if(self.isVisible):
            btns =[]
            btns.append("ON")
            self.emit(QtCore.SIGNAL('requestButtonPrompt'),btns)



    def dispose(self):
        print("Disposing of Internet Radio")

