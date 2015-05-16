
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.AlarmWidget import *

class Alarm(QObject):

    Enabled = True
    
    menuOrder = 0

    ListenForPinEvent = True

    snoozeButtonPin = None

    def __init__(self):
        super(Alarm, self).__init__()

    

    def showWidget(self):
        print("showing alarm")
        self.alarm_widget.setVisible(True)

    def hideWidget(self):
        print("hiding alarm")
        self.alarm_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.alarm_widget = AlarmWidget(parent)       
        self.alarm_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.alarm_widget.setVisible(False)
        self.alarm_widget.initialize()
        


    def getMenuIcon(self):
        return "icons/bell.svg"

    def getMenuIconSelected(self):
        return "icons/bellSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 70

    def setPin(self, pinConfig):
        self.snoozeButtonPin =  pinConfig["CONTEXT_BUTTON"]

    def processPinEvent(self, pinNum):
        if(self.snoozeButtonPin == pinNum):
            self.alarm_widget.doAlarmSnooze()
   

   


    def dispose(self):
        print("Disposing of Alarm")

