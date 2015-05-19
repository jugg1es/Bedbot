#!/usr/bin/python


from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.RadioWidget import *

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

    def hideWidget(self):
        isVisible = False
        self.aux_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.aux_widget = RadioWidget(parent)       
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

    def setPin(self, pinConfig):
        self.onButton = pinConfig["ON_BUTTON"]
        self.audioRelayPin = pinConfig["AUDIO_TWO_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.onButton == pinNum and self.isVisible == True):
            self.emit(QtCore.SIGNAL('audioStarted'), self)
            self.emit(QtCore.SIGNAL('pinRequested'), self.audioRelayPin)




    def dispose(self):
        print("Disposing of Internet Radio")

