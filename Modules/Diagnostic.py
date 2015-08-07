
from PyQt4.QtCore import QObject

from PyQt4 import QtCore, QtGui, uic
from Helpers.perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.DiagnosticWidget import *

class Diagnostic(QObject):
    menuOrder =6
    Enabled = True
    ListenForPinEvent = True
    widgetVisible = False

    displayingPin = False


    def __init__(self):
        super(Diagnostic, self).__init__()

    
    def showWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.diag_widget.setVisible(True)
        self.widgetVisible = True

    def hideWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.diag_widget.setVisible(False)
        self.widgetVisible = False

    def addMenuWidget(self, parent):
        """Required for main modules to be inserted into the menu"""        
        self.diag_widget = DiagnosticWidget(parent)       
        self.diag_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.diag_widget.setVisible(False)
        

    def getMenuIcon(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/gear.svg"

    def getMenuIconSelected(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/gearSelected.svg"

    def getMenuIconHeight(self):
        """Required for main modules to be inserted into the menu"""
        return 60
    def getMenuIconWidth(self):
        """Required for main modules to be inserted into the menu"""
        return 53


    def processPinEvent(self, pinNum):
        if(self.widgetVisible):
            self.displayingPin = True
            self.diag_widget.updatePinDisplay(pinNum)
            self.pinDisplayResetTimer = QtCore.QTimer()
            self.pinDisplayResetTimer.timeout.connect(self.resetPinDisplay)
            self.pinDisplayResetTimer.start(500)      

    def resetPinDisplay(self):      
        self.displayingPin = False
        self.diag_widget.updatePinDisplay("")

    def dispose(self):
        print("Disposing of Diagnostic")
        #self.clockUpdateTimer.cancel()

