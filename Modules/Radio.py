
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.RadioWidget import *

class Radio(QObject):

    Enabled = True    
    menuOrder = 2



    def __init__(self):
        super(Radio, self).__init__()

    def showWidget(self):
        self.radio_widget.setVisible(True)

    def hideWidget(self):
        self.radio_widget.setVisible(False)

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



    def dispose(self):
        print("Disposing of Radio")

