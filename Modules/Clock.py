
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.ClockWidget import *

class Clock(QObject):
    menuOrder = 0
    Enabled = True

    def __init__(self):
        super(Clock, self).__init__()

    
    def showWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.time_widget.setVisible(True)

    def hideWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.time_widget.setVisible(False)

    def addMenuWidget(self, parent):
        """Required for main modules to be inserted into the menu"""
        self.time_widget = ClockWidget(parent)       
        self.time_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.time_widget.setVisible(False)
        self.startClockTimer()

    def getMenuIcon(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/clock.svg"

    def getMenuIconSelected(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/clockSelected.svg"

    def getMenuIconHeight(self):
        """Required for main modules to be inserted into the menu"""
        return 65
    def getMenuIconWidth(self):
        """Required for main modules to be inserted into the menu"""
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

