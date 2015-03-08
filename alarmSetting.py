import datetime
from enum import Enum
import re


class AlarmState(Enum):
    OFF = 0
    BUZZ=1
    RADIO=2
    PANDORA=3
    
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

timeSaveFormat = "%H:%M";

    
class alarmSetting(object):
    
    timeSetting = None
    state = AlarmState.OFF
    
    alarmStartTime = None
    alarmSnoozeTime = None
    
    def __init__(self, settingName, config):
        if(config == None):
            #self.timeSetting = datetime.time(0,0,0,0)
            self.timeSetting = datetime.date.today()
            self.state = AlarmState.OFF
        else:
            s = config.get(settingName, "time")
            self.timeSetting=datetime.datetime(*map(int, re.split('[^\d]', s)[:-1]))
            #self.timeSetting = datetime.datetime.strptime(config.get(settingName, "time"), timeSaveFormat) 
            self.state = AlarmState(int(config.get(settingName, "status")))
           
    def setSnoozeTime(self, start):
        self.alarmSnoozeTime = start
        
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
        
    def changeHour(self, d):
        if(d == Direction.UP):
            self.timeSetting = self.timeSetting + datetime.timedelta(hours=1)
        elif(d == Direction.DOWN):
            self.timeSetting = self.timeSetting + datetime.timedelta(hours=-1)
            
    def changeMinute(self, d):
        if(d == Direction.UP):
            self.timeSetting = self.timeSetting + datetime.timedelta(minutes=1)
        elif(d == Direction.DOWN):
            self.timeSetting = self.timeSetting + datetime.timedelta(minutes=-1)     
    
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
        #return str(self.timeSetting.strftime("%H:%M"))  
        return self.timeSetting.isoformat()
    
    def getDisplayTimeString(self):
        return str(self.timeSetting.strftime("%I:%M %p"))
    
    def getHourString(self):
        return str(self.timeSetting.strftime("%I"))
    
    def getMinuteString(self):
        return str(self.timeSetting.strftime("%M"))
    
    