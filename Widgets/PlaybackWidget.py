
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from perpetualTimer import perpetualTimer

from enum import Enum

from clickable import *


class PlaybackType(Enum):
    RADIO = 0
    PANDORA=1
    AUX = 2,
    WWWSTREAM = 3

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
    

    
class PlaybackWidget(QtGui.QWidget):
    
    playbackUnselectedStyle = "font-size:20px;background-color:#000;border: 2px solid #000; color:#fff;"
    playbackSelectedStyle = "font-size:20px;border: 2px solid #fff; color:#fff;"
    
    currentPlaybackType = PlaybackType.RADIO
    
    def __init__(self, parent):
        super(PlaybackWidget, self).__init__(parent)
        
        self.resize(318, 40)
        
        self.horizontalLayoutWidget = QtGui.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 318, 40))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        
        
        self.radioPlaybackButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.radioPlaybackButton.name = PlaybackType.RADIO
        self.radioPlaybackButton.setText("RADIO")
        clickableSender(self.radioPlaybackButton).connect(self.setPlaybackType)
        self.horizontalLayout.addWidget(self.radioPlaybackButton)
        
        
        self.pandoraPlaybackButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.pandoraPlaybackButton.name = PlaybackType.PANDORA
        self.pandoraPlaybackButton.setText("PANDORA")
        clickableSender(self.pandoraPlaybackButton).connect(self.setPlaybackType)
        self.horizontalLayout.addWidget(self.pandoraPlaybackButton)
        
        
       
        self.auxPlaybackButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.auxPlaybackButton.name = PlaybackType.AUX
        self.auxPlaybackButton.setText("AUX")
        clickableSender(self.auxPlaybackButton).connect(self.setPlaybackType)
        self.horizontalLayout.addWidget(self.auxPlaybackButton)
        
        
        self.updatePlaybackDisplay()
     
        QtCore.QMetaObject.connectSlotsByName(self)  
        
    def setPlaybackType(self, obj):        
        newType = PlaybackType(obj.name)
        self.currentPlaybackType = newType
        self.updatePlaybackDisplay()
        self.emit(QtCore.SIGNAL('changePlayback'), newType)
        
    
    def updatePlaybackDisplay(self):
        self.radioPlaybackButton.setStyleSheet(self.playbackUnselectedStyle)
        self.pandoraPlaybackButton.setStyleSheet(self.playbackUnselectedStyle)
        self.auxPlaybackButton.setStyleSheet(self.playbackUnselectedStyle)
        if(self.currentPlaybackType == PlaybackType.RADIO):
            self.radioPlaybackButton.setStyleSheet(self.playbackSelectedStyle)
        elif(self.currentPlaybackType == PlaybackType.PANDORA):
            self.pandoraPlaybackButton.setStyleSheet(self.playbackSelectedStyle)
        elif(self.currentPlaybackType == PlaybackType.AUX):
            self.auxPlaybackButton.setStyleSheet(self.playbackSelectedStyle)