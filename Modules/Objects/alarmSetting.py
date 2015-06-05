import datetime
from enum import Enum
import re
from Modules.Objects.AlarmState import *


    
class TimeOfDay(Enum):
    AM = 0
    PM=1
    
class Direction(Enum):
    UP = 0
    DOWN=1
    NONE =2
    
class ScanTarget(Enum):
    HOUR = 0
    MINUTE=1
    NONE =2

timeSaveFormat = "%H:%M"

    
class alarmSetting(object):
    
    timeSetting = None
    state = AlarmState.OFF
    details = None
    moduleName = None

    
    alarmStartTime = None
    alarmSnoozeTime = None
    
    def __init__(self, settingName, config):
        if(config == None):
            self.timeSetting = datetime.date.today()
            self.state = AlarmState.OFF
            self.details = None
            self.moduleName = None
        else:
            s = config.get(settingName, "time")
            self.timeSetting=datetime.datetime(*map(int, re.split('[^\d]', s)[:-1]))
            self.state = AlarmState(int(config.get(settingName, "status")))
            self.details = config.get(settingName, "details")
            self.moduleName = config.get(settingName, "moduleName")
           
    def setSnoozeTime(self, start):
        self.alarmSnoozeTime = start

    def setAlarmStartTime(self):
        self.alarmStartTime = datetime.datetime.now()
        
    def getTimeSinceSnooze(self):
        if(self.alarmSnoozeTime != None):
            now = datetime.datetime.now()
            timeSince = now - self.alarmSnoozeTime
            return timeSince
        else:
            return None
        
    def setStartTime(self, start):
        self.alarmStartTime = start
        
    def getTimeSinceStart(self):
        if(self.alarmStartTime != None):
            now = datetime.datetime.now()
            timeSince = now - self.alarmStartTime
            return timeSince
        else:
            return None
    def setHour(self, h):
        self.timeSetting = self.timeSetting.replace(hour=h)

    def setMinute(self, m):
        self.timeSetting = self.timeSetting.replace(minute=m)
   
    def setTimeOfDayType(self, tod):
        if(self.timeSetting.strftime("%p") != tod.name ):
            if(tod == TimeOfDay.AM):
                self.timeSetting = self.timeSetting + datetime.timedelta(hours=-12)
            elif(tod == TimeOfDay.PM):
                self.timeSetting = self.timeSetting + datetime.timedelta(hours=12)      
                
    def getTimeOfDayType(self):
        if(self.timeSetting.strftime("%p") == "AM"):
            return TimeOfDay.AM
        elif(self.timeSetting.strftime("%p") == "PM"):
            return TimeOfDay.PM
        
    def getSaveTimeString(self):
        return self.timeSetting.isoformat()
    
    def getDisplayTimeString(self):
        return str(self.timeSetting.strftime("%I:%M %p"))
    
    def getHourString(self):
        return str(self.timeSetting.strftime("%I").lstrip('0'))
    
    def getMinuteString(self):
        return str(self.timeSetting.strftime("%M"))
    
    