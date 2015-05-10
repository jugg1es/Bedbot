
import datetime
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
import time
import json
import os.path
import os
from Objects.internetStation import *


class InternetRadioService(QObject):
    config = None
    
    settingsFilename = "internetStations.json"
    alarmSettings = None
    isPlaying = False
    
    stations = []
    
    def __init__(self):
        super(InternetRadioService, self).__init__()
        print("initializing Internet radio service")   
        self.loadFromJSON()     
        
    def playStation(self, stationID):
        if(self.isPlaying == True):
            self.stop()
        station = self.stations[stationID]
        print("playing stream at: " + station.url)   
        fullCommand = "mpc add " + station.url
        os.system(fullCommand)    
        self.isPlaying = True
        self.emit(QtCore.SIGNAL('internetRadioPlay'))  
        
        
    def stop(self):
        print("stopping playback of internet stream")
        os.system("mpc stop")      
        os.system("mpc clear")     
        self.isPlaying = False
        self.emit(QtCore.SIGNAL('internetRadioStop'))  
    
    def loadFromJSON(self):      
            
        with open(self.settingsFilename) as data_file:    
            data = json.load(data_file)            
            
        self.stations = []
        for x in range(0, len(data["Stations"])):
            s = data["Stations"][x]
            sObj = internetStation(s, x)
            self.stations.append(sObj)
            
    def dispose(self):
        self.stop()
            
    #def saveStations(self):
        