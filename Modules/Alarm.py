
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.AlarmWidget import *
import json
import datetime




class Alarm(QObject):

    Enabled = True
    
    menuOrder = 1

    ListenForPinEvent = True

    snoozeButtonPin = None

    alarmSettings = None
    settingsFilename = "alarmConfig.json"

    isVisible = False

    currentPopupType = None

    def __init__(self):
        super(Alarm, self).__init__()

    

    def showWidget(self):
        self.isVisible = True
        self.alarm_widget.setVisible(True)

    def hideWidget(self):
        self.isVisible = False
        self.alarm_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.alarm_widget = AlarmWidget(parent)       
        self.connect(self.alarm_widget, QtCore.SIGNAL('selectAlarmType'), self.selectAlarmTypeCallback)
        self.connect(self.alarm_widget, QtCore.SIGNAL('selectTimeHour'), self.selectTimeHourCallback)
        self.connect(self.alarm_widget, QtCore.SIGNAL('selectTimeMinute'), self.selectTimeMinuteCallback)
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

    def selectTimeHourCallback(self):
        self.currentPopupType = "hour"
        self.emit(QtCore.SIGNAL('showPopup'), self, "Select Hour", "numberSelect", 2)

    def selectTimeMinuteCallback(self):
        self.currentPopupType = "min"
        self.emit(QtCore.SIGNAL('showPopup'), self, "Select Minute", "numberSelect", 2)

    def selectAlarmTypeCallback(self):
        self.currentPopupType = "alarmType"
        options = ["Off", "Radio", "Internet Radio"]
        self.emit(QtCore.SIGNAL('showPopup'), self, "Configure Alarm", "optionSelect", options)


    def setCurrentPopup(self, popup):
        if(self.currentPopupType != None):
            self.screenPowerPopup = popup

    def popupResult(self, result):
        if(self.currentPopupType != None):
            if(self.currentPopupType == "alarmType"):
                print("received result: " + result)
                if(result == "Off"):
                    self.alarm_widget.setAlarmStateCallback(AlarmState.OFF)
                elif(result == "Radio"):
                    self.alarm_widget.setAlarmStateCallback(AlarmState.RADIO)
                elif(result == "Internet Radio"):
                    self.alarm_widget.setAlarmStateCallback(AlarmState.INETRADIO)
            elif(self.currentPopupType == "hour"):
                self.alarm_widget.setHourCallback(result)
            elif(self.currentPopupType == "min"):
                self.alarm_widget.setMinuteCallback(result)

            self.currentPopupType = None

    def dispose(self):
        print("Disposing of Alarm")

