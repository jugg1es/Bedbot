
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.ClockWidget import *

class Playback(QObject):

    Enabled = True    
    menuOrder = 1

    def __init__(self):
        super(Playback, self).__init__()

    def showWidget(self):
        print("showing playback")
        self.playback_widget.setVisible(True)
    def hideWidget(self):
        print("hiding playback")
        self.playback_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.playback_widget = ClockWidget(parent)       
        self.playback_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.playback_widget.setVisible(False)

    def getMenuIcon(self):
        return "icons/connection.svg"

    def getMenuIconSelected(self):
        return "icons/connectionSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 70


   


    def dispose(self):
        print("Disposing of Alarm")

