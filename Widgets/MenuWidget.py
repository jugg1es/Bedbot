
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from threading import Timer,Thread,Event
import sys
from PyQt4.QtGui import *
from PyQt4.Qt import QBrush
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget


try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
class MenuWidget(QtGui.QWidget):
    
    #showAlarm = pyqtSignal()
    #showPlayback = pyqtSignal()
    #showClock = pyqtSignal()
    
    def __init__(self, parent):
        super(MenuWidget, self).__init__(parent)
        self.resize(320, 70)
                
        self.setAutoFillBackground(True)
        self.alarmButton = QSvgWidget("icons/bell.svg", self)
        self.alarmButton.setGeometry(QtCore.QRect(10, 0, 70, 65))
        clickable(self.alarmButton).connect(self.alarmButtonClicked)
        
        
        self.playbackButton = QSvgWidget("icons/connection.svg", self)
        self.playbackButton.setGeometry(QtCore.QRect(125, 0, 70, 65))
        clickable(self.playbackButton).connect(self.playbackButtonClicked)
        
        
        self.clockButton = QSvgWidget("icons/clockSelected.svg", self)
        self.clockButton.setGeometry(QtCore.QRect(240, 0, 65, 65))
        clickable(self.clockButton).connect(self.clockButtonClicked)
        
        
        
    def deselectAll(self):
        self.clockButton.load("icons/clock.svg")
        self.playbackButton.load("icons/connection.svg")
        self.alarmButton.load("icons/bell.svg")
        
        
    def clockButtonClicked(self):  
        self.deselectAll()
        self.clockButton.load("icons/clockSelected.svg")
        self.t = QTimer()
        self.t.timeout.connect(self.doShowClock)
        self.t.start(500)
        print("clock")
        
    def doShowClock(self):
        self.emit(QtCore.SIGNAL('showClock'))
        #self.showClock.emit() 
        self.t.stop() 
        
    def alarmButtonClicked(self):  
        self.deselectAll()
        self.alarmButton.load("icons/bellSelected.svg")
        self.t = QTimer()
        self.t.timeout.connect(self.doShowAlarm)
        self.t.start(500)      
        
    def doShowAlarm(self):
        self.emit(QtCore.SIGNAL('showAlarm'))
        #self.showAlarm.emit()
        self.t.stop()
        
        
    def playbackButtonClicked(self):  
        self.deselectAll()
        self.playbackButton.load("icons/connectionSelected.svg")
        self.t = QTimer()
        self.t.timeout.connect(self.doShowPlayback)
        self.t.start(500)
        
    def doShowPlayback(self):
        self.emit(QtCore.SIGNAL('showPlayback'))
        #self.showPlayback.emit()   
        self.t.stop()     
        
        
        
       
        
        