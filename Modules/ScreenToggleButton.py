
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from threading import Timer,Thread,Event
from Modules.PhysicalButton import *

class ScreenToggleButton(QObject):

    Enabled = True

    ListenForPinEvent = True

    screenToggleButton = None
    
    btnManager = None

    def __init__(self):
        super(ScreenToggleButton, self).__init__()

    def setPin(self, pinConfig):
        self.screenToggleButton = pinConfig["SCREEN_TOGGLE"]
        self.initialize()

    def initialize(self):
        self.btnManager = PhysicalButton()
        self.btnManager.configure(self.screenToggleButton, 1000)
        self.connect(self.btnManager, QtCore.SIGNAL('logEvent'), self.logEvent)
        self.connect(self.btnManager, QtCore.SIGNAL('buttonPressed'), self.screenToggleButtonPressed)

    def screenToggleButtonPressed(self):
        self.emit(QtCore.SIGNAL('logEvent'),"Screen toggle button pressed") 
        self.emit(QtCore.SIGNAL('pushFired')) 

    
    def logEvent(self, evtStr):
        self.emit(QtCore.SIGNAL('logEvent'),evtStr) 

    


    def dispose(self):
        try:
            self.btnManager.dispose()

        except Exception:
            self.emit(QtCore.SIGNAL('logEvent'),"Problem disposing of screen toggle button") 
        

