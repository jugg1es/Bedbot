
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.ClockWidget import *

class Clock(QObject):

    isMainWidget = True
    menuOrder = 2

    def __init__(self):
        super(Clock, self).__init__()

    
    def showWidget(self):
        print("showing clock")
        self.time_widget.setVisible(True)

    def hideWidget(self):
        print("hiding clock")
        self.time_widget.setVisible(False)

    def addWidget(self, parent):
        self.time_widget = ClockWidget(parent)       
        self.time_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.time_widget.setVisible(False)
        self.startClockTimer()

    def getMenuIcon(self):
        return "icons/clock.svg"

    def getMenuIconSelected(self):
        return "icons/clockSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 65


    def startClockTimer(self):
        self.clockUpdateTimer = perpetualTimer(1, self.processClockTime)
        self.clockUpdateTimer.start()
        
    def stopClockTimer(self):
        self.clockUpdateTimer.cancel()    

    def processClockTime(self):
        self.time_widget.updateCurrentTime()


    def dispose(self):
        print("Disposing of Clock")
        self.clockUpdateTimer.cancel()

