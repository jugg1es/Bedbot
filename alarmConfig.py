
import datetime
import time
from configparser import SafeConfigParser
import os.path
from alarmSetting import *


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
                    t = datetime.time(0,0,0,0)
                    self.config.set(section, "time", t.strftime(timeSaveFormat))
                    self.config.set(section, "status", str(AlarmState.OFF.value))      
        self.alarmSettings = []          
        for x in range(0, 3):
            section = "alarm" + str(x)
            setting = alarmSetting(section, self.config)
            self.alarmSettings.append(setting)
        self.saveSettings(self.alarmSettings)
        return self.alarmSettings