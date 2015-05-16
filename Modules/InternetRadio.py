#!/usr/bin/env python


from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Objects.internetStation import *
from Modules.Widgets.InternetRadioWidget import *
import pycurl
import json

from StringIO import StringIO 
import os

class InternetRadio(QObject):

    UsesAudio = True

    Enabled = True    
    audioStatusDisplay = ""
    menuOrder = 4

    settingsFilename = "internetStations.json"
    stations = []

    currentPlaylist = []



    def __init__(self):
        super(InternetRadio, self).__init__()

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

    def getAudioStatusDisplay(self):
        return self.audioStatusDisplay

    def play(self):
        self.reset()
        if(self.currentPlaylist != None):
            try:
                for pl in self.currentPlaylist:
                    fullCommand = "mpc add " + pl
                    os.system(fullCommand)    
                os.system("mpc play")      
            except:
                print("mpc failed")
        

    def reset(self):
        try:
            print("stopping playback of internet stream")
            os.system("mpc stop")      
            os.system("mpc clear")     
        except:
            print("mpc failed")

    def stop(self):
        self.reset()
        self.inetradio_widget.deselectAllStations()

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

