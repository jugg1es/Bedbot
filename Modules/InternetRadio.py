#!/usr/bin/python


from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Objects.internetStation import *
from Modules.Widgets.InternetRadioWidget import *
import pycurl
import shlex
import json
import subprocess
from StringIO import StringIO 
import os

class InternetRadio(QObject):

    UsesAudio = True
    ListenForPinEvent = True
    offButton = None
    audioRelayPin = None


    Enabled = True    
    audioStatusDisplay = ""
    menuOrder = 4

    settingsFilename = "internetStations.json"
    stations = []

    currentPlaylist = []

    isPlaying = False


    def __init__(self):
        super(InternetRadio, self).__init__()

    def setPin(self, pinConfig):
        self.offButton = pinConfig["OFF_BUTTON"]
        self.audioRelayPin = pinConfig["AUDIO_ONE_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.offButton == pinNum and self.isPlaying == True):
            self.stop()

    def showWidget(self):
        self.inetradio_widget.setVisible(True)

    def hideWidget(self):
        self.inetradio_widget.setVisible(False)

    def addMenuWidget(self, parent):
        self.inetradio_widget = InternetRadioWidget(parent)       
        self.inetradio_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.inetradio_widget.setVisible(False)
        self.initialize()

    def getMenuIcon(self):
        return "icons/globe.svg"

    def getMenuIconSelected(self):
        return "icons/globeSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 65


    def initialize(self):
        self.loadFromJSON()
        self.inetradio_widget.fillStationList(self.stations)
        self.connect(self.inetradio_widget, QtCore.SIGNAL('stationSelected'), self.stationSelectedCallback)

    def stationSelectedCallback(self, stationID):
        if(stationID < len(self.stations)):
            station = self.stations[stationID]
            self.currentPlaylist = self.retrievePlaylist(station.url)           
            self.play()
            self.audioStatusDisplay = station.name
            self.emit(QtCore.SIGNAL('audioStarted'), self)
            self.emit(QtCore.SIGNAL('pinRequested'), self.audioRelayPin)

    def getAudioStatusDisplay(self):
        return self.audioStatusDisplay

    def play(self):
        self.reset()

        for pl in self.currentPlaylist:
            subprocess.call(shlex.split("mpc add " + pl)) 
            subprocess.call(shlex.split("mpc play"))  
                  
        self.isPlaying = True
        

    def reset(self):
        subprocess.call(shlex.split("mpc stop")) 
        subprocess.call(shlex.split("mpc clear"))        

    def stop(self):
        if(self.isPlaying):
            self.reset()   
            self.inetradio_widget.deselectAllStations()
            self.emit(QtCore.SIGNAL('audioStopped'), self)
        self.isPlaying = False

    def retrievePlaylist(self, url):       
        url = url.strip() 
        url = url.encode(encoding='UTF-8',errors='strict')
        print("retreiving playlist from: " + str(url))
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()

        playlist = []
        
        allLines = buffer.buflist      
        playlist = []
        for line in allLines:
            line = line.strip()
            if(line[0] != '#'):
                print("found stream: " + line)
                playlist.append(line)
        
        return playlist
    

    def getPlaylist(self, station):
        print("get playlist")

    def loadFromJSON(self):      
            
        with open(self.settingsFilename) as data_file:    
            data = json.load(data_file)            
            
        self.stations = []
        for x in range(0, len(data["Stations"])):
            s = data["Stations"][x]
            sObj = internetStation(s, x)
            self.stations.append(sObj)

    def dispose(self):
        print("Disposing of Internet Radio")
        self.stop()

