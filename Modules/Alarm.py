
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.AlarmWidget import *
import json
import datetime
from perpetualTimer import perpetualTimer
from enum import Enum
from Modules.Objects.AlarmState import *


class AlarmPopupType(Enum):
    ALARM_TYPE = 0
    ALARM_DETAILS=1
    HOUR=2
    MINUTE=3




class Alarm(QObject):

    Enabled = True
    
    menuOrder = 1

    ListenForPinEvent = True

    """Context button is used for either snoozing or scrolling through alarm presets"""
    contextButton = None

    alarmSettings = None
    settingsFilename = "alarmConfig.json"

    isVisible = False

    currentPopupType = None

    isAlarmActive = False

    possibleAlarms = None
    currentAlarmType = None
    currentAlarmModule = None


    def __init__(self):
        super(Alarm, self).__init__()
        


    def showWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.isVisible = True
        self.alarm_widget.setVisible(True)
        btns =["CONTEXT"]
        self.emit(QtCore.SIGNAL('requestButtonPrompt'),btns)

    def hideWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.isVisible = False
        self.alarm_widget.setVisible(False)

    def addMenuWidget(self, parent):
        """Required for main modules to be inserted into the menu"""
        self.alarm_widget = AlarmWidget(parent)       
        self.connect(self.alarm_widget, QtCore.SIGNAL('selectAlarmType'), self.selectAlarmTypeCallback)
        self.connect(self.alarm_widget, QtCore.SIGNAL('selectTimeHour'), self.selectTimeHourCallback)
        self.connect(self.alarm_widget, QtCore.SIGNAL('selectTimeMinute'), self.selectTimeMinuteCallback)
        self.alarm_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.alarm_widget.setVisible(False)
        self.alarm_widget.initialize()
        self.alarmTimer = perpetualTimer(1, self.processAlarmTime)
        self.alarmTimer.start()
        

        
    def getMenuIcon(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/bell.svg"

    def getMenuIconSelected(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/bellSelected.svg"

    def getMenuIconHeight(self):
        """Required for main modules to be inserted into the menu"""
        return 65
    def getMenuIconWidth(self):
        """Required for main modules to be inserted into the menu"""
        return 70

    def setPin(self, pinConfig):
        self.contextButton =  pinConfig["CONTEXT_BUTTON"]
        

    def processPinEvent(self, pinNum):
        if(self.contextButton == pinNum):
            if(self.isVisible and self.isAlarmActive == False):
               self.alarm_widget.setTestAlarm()
            elif(self.isAlarmActive):
                self.alarm_widget.doAlarmSnooze()
        '''
        if(self.contextButton == pinNum):
            if(self.isVisible and self.isAlarmActive == False):
               self.alarm_widget.cycleSelectedAlarm()
            elif(self.isAlarmActive):
                self.alarm_widget.doAlarmSnooze()
        '''


    def processAlarmTime(self):
        t = Thread(target=self.doProcessAlarm, args=(self,))        
        t.start()     
        
            
    def doProcessAlarm(self, parent):
        newAlarms = parent.checkAlarms()
        if(parent.isAlarmActive == False and len(newAlarms) > 0):
            firedAlarm = newAlarms[0]
            firedAlarm.setAlarmStartTime()
            t = {}
            t["details"] = str(firedAlarm.details)
            parent.emit(QtCore.SIGNAL('broadcastModuleRequest'), parent, "alarmFired", t, None, str(firedAlarm.moduleName))
            parent.isAlarmActive = True
            parent.emit(QtCore.SIGNAL('showPopup'), self, None, "alarm")


    def checkAlarms(self):
        currentTime = datetime.datetime.now()
        activeAlarms = []
        for x in range(0, 3):
            current = self.alarm_widget.alarmSettings[x]
            if(current.state != AlarmState.OFF and current.timeSetting.strftime("%I:%M %p") == currentTime.strftime("%I:%M %p")):
                activeAlarms.append(current)
        return activeAlarms

    def selectTimeHourCallback(self):
        self.currentPopupType =  AlarmPopupType.HOUR
        self.emit(QtCore.SIGNAL('showPopup'), self, "Select Hour", "numberSelect", 2)

    def selectTimeMinuteCallback(self):
        self.currentPopupType =AlarmPopupType.MINUTE
        self.emit(QtCore.SIGNAL('showPopup'), self, "Select Minute", "numberSelect", 2)

    def selectAlarmTypeCallback(self):
        """Tells the main module to poll all other active modules for 'getPossibleAlarmDetails' method
        and return the results to 'alarmDetailsCallback'
        """
        self.possibleAlarms = None
        self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "getPossibleAlarmDetails", None, "alarmDetailsCallback")



    def alarmDetailsCallback(self, alarmDetails):
        self.possibleAlarms = alarmDetails
        self.currentPopupType = AlarmPopupType.ALARM_TYPE
        options = ["OFF"]
        for x in self.possibleAlarms:
            options.append(x["name"])
        self.emit(QtCore.SIGNAL('showPopup'), self, "Configure Alarm", "optionSelect", options)

           

    def popupResult(self, result):
        if(self.currentPopupType != None):
            if(self.currentPopupType ==  AlarmPopupType.ALARM_DETAILS):
                self.alarm_widget.setAlarmStateCallback(self.currentAlarmType, result,self.currentAlarmModule)
                self.currentAlarmType = None
            elif(self.currentPopupType == AlarmPopupType.ALARM_TYPE):
                """Once the alarm type is selected (assuming it's not OFF), it uses the data retrieved in 'alarmDetailsCallback' 
                to then query the user for further details about how the alarm should work using 'showPopup'
                """
                if(result == "OFF"):
                    self.alarm_widget.setAlarmStateCallback(AlarmState.OFF)
                else:         
                    """Find the selected alarm type in data retrieved from 'alarmDetailsCallback'       """            
                    selectedAlarm = None
                    selectedAlarmModule = None
                    selectedAlarmState = None
                    for x in self.possibleAlarms:
                        if(x["name"] == str(result)):
                            selectedAlarm = x         
                            selectedAlarmModule  =x["moduleName"]
                            selectedAlarmState = x["alarmType"]
                            break

                    """setup for the alarm details popup"""
                    self.currentPopupType = AlarmPopupType.ALARM_DETAILS
                    self.currentAlarmType = selectedAlarmState
                    self.currentAlarmModule = selectedAlarmModule
                    if(self.currentAlarmType != None):
                        self.emit(QtCore.SIGNAL('showPopup'), self, "Select Alarm", "optionSelect", selectedAlarm["options"])
            elif(self.currentPopupType == AlarmPopupType.HOUR):
                self.alarm_widget.setHourCallback(result)
                self.currentPopupType = None
            elif(self.currentPopupType == AlarmPopupType.MINUTE):
                self.alarm_widget.setMinuteCallback(result)
                self.currentPopupType = None

    def dispose(self):
        self.alarmTimer.cancel()
        print("Disposing of Alarm")

