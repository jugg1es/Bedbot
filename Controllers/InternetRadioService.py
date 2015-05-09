
import datetime
import time
import json
import os.path


class InternetRadioService(object):
    config = None
    
    settingsFilename = "internetStations.json"
    alarmSettings = None
    
    data = None
    
    def __init__(self):
        print("initializing Internet radio service")        
        
        with open(self.settingsFilename) as data_file:    
            self.data = json.load(data_file)            
        
        
                
    