
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from Helpers.perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.AlarmWidget import *
import json
import datetime
from enum import Enum
from Modules.Objects.AlarmState import *
from Modules.Objects.ScreenState import *


class AlarmPopupType(Enum):
    ALARM_TYPE = 0
    ALARM_DETAILS=1
    HOUR=2
    MINUTE=3
    ALARM_ON =4
    SNOOZING=5




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
    isSnoozeActive = False


    possibleAlarms = None
    currentAlarmType = None
    currentAlarmModule = None

    snoozeDurationSec = 0.2 * 60
    alarmDurationSec = 0.5 * 60

    firedAlarm = None

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
            if(self.isVisible ):
               self.alarm_widget.setTestAlarm()
               #self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "requestScreenPosition", ScreenState.CLOSED, None, "ScreenManager") 
        '''
        if(self.contextButton == pinNum):
            if(self.isVisible and self.isAlarmActive == False):
               self.alarm_widget.cycleSelectedAlarm()
        '''


    def processAlarmTime(self):
        t = Thread(target=self.doProcessAlarm, args=(self,))        
        t.start()     
        
    def getIsAlarmActive(self):
        if(self.isAlarmActive or self.isSnoozeActive):
            return True
        return False
            
    def doProcessAlarm(self, parent):
        newAlarms = parent.checkAlarms()
        if(parent.isAlarmActive == False and len(newAlarms) > 0):
            self.firedAlarm = newAlarms[0]
            """Prevent alarms from firing twice in the same minute"""
            continueFiringAlarm = True
            if(self.firedAlarm.alarmStartTime != None):
                diff = datetime.datetime.now() - self.firedAlarm.alarmStartTime
                if(diff.total_seconds() < 60):
                    continueFiringAlarm = False

            if(continueFiringAlarm):
                parent.fireAlarm(self.firedAlarm)

    def fireAlarm(self, alarm):
        self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "requestScreenPosition", ScreenState.OPEN, None, "ScreenManager")  

        alarm.setAlarmStartTime()
        t = {}
        t["details"] = str(alarm.details)
        self.isAlarmActive = True
        self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "alarmFired", t, None, str(alarm.moduleName))        
        self.currentPopupType = AlarmPopupType.ALARM_ON
        self.emit(QtCore.SIGNAL('showPopup'), self, None, "alarm", self.alarmDurationSec)
            
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

    def doAlarmSnooze(self):
        if(self.isAlarmActive):
            self.isSnoozeActive = True
            self.currentPopupType = AlarmPopupType.SNOOZING
            self.emit(QtCore.SIGNAL('stopAllAudio'))   
            self.emit(QtCore.SIGNAL('showPopup'), self, None, "snooze", self.snoozeDurationSec)
            

    def doAlarmOff(self):
        if(self.isAlarmActive):
            self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "requestScreenPosition", ScreenState.CLOSED, None, "ScreenManager")  
            self.isSnoozeActive = False
            self.isAlarmActive = False
            self.emit(QtCore.SIGNAL('stopAllAudio'))   
            

    def doAlarmDisable(self):
        if(self.isAlarmActive):
            self.isSnoozeActive = False
            self.isAlarmActive = False

    def doAlarmSnoozeExpired(self):
        print("snooze expired")
        if(self.isAlarmActive):
            self.isSnoozeActive = False
            self.fireAlarm(self.firedAlarm)


    
    def processAlarmPopupResult(self, result):
        time.sleep(0.3)
        if(str(result) == "alarmSnooze"):
            self.doAlarmSnooze()
        elif(str(result) == "alarmOff"):
            self.doAlarmOff()
        elif(str(result) == "alarmDisable"):
            self.doAlarmDisable()

    def popupResult(self, result):
        if(self.currentPopupType != None):
            if(self.currentPopupType == AlarmPopupType.ALARM_ON):
                t = Thread(target=self.processAlarmPopupResult, args=(result,))        
                t.start()  
            elif(self.currentPopupType == AlarmPopupType.SNOOZING):
                self.doAlarmSnoozeExpired()
            elif(self.currentPopupType ==  AlarmPopupType.ALARM_DETAILS):
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

