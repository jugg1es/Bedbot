
import datetime
import time
from ConfigParser import SafeConfigParser
import os.path
from Modules.Objects.alarmSetting import *


class alarmConfig(object):
    config = None
    settingsFilename = None
    alarmSettings = None
    
    def __init__(self, filename):
        self.settingsFilename = filename 
        
    def saveSettings(self, settings):
        if(self.config == None):
            self.loadSettings()
        else:
            self.alarmSettings = settings
            for x in range(0, 3):
                current = self.alarmSettings[x]
                section = "alarm" + str(x)    
                self.config.set(section, "time", current.getSaveTimeString())
                self.config.set(section, "status", str(current.state.value))
                self.config.set(section, "details", current.details)
                self.config.set(section, "moduleName", current.moduleName)
        with open(self.settingsFilename, 'w') as f:
            self.config.write(f)
            
    def loadSettings(self):
        if(self.config == None):
            self.config = SafeConfigParser()
            if(os.path.isfile(self.settingsFilename) == True):
                self.config.read(self.settingsFilename)
            else:
                for x in range(0, 3):
                    section = "alarm" + str(x)
                    self.config.add_section(section)
                    t = datetime.datetime(2015,1,1,0,0,0)
                    defaultTime = t.isoformat()
                    self.config.set(section, "time", defaultTime)
                    self.config.set(section, "status", str(AlarmState.OFF.value))   
                    self.config.set(section, "details", "")     
                    self.config.set(section, "moduleName","")
        self.alarmSettings = []          
        for x in range(0, 3):
            section = "alarm" + str(x)
            setting = alarmSetting(section, self.config)
            self.alarmSettings.append(setting)
        self.saveSettings(self.alarmSettings)
        return self.alarmSettings