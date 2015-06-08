#!/usr/bin/python


from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from Helpers.perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Objects.internetStation import *
from Modules.Widgets.InternetRadioWidget import *
from Modules.Objects.AlarmState import *
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
    onButton = None


    Enabled = True    
    audioStatusDisplay = ""
    menuOrder = 4

    settingsFilename = "internetStations.json"
    stations = []

    currentPlaylist = []

    isPlaying = False
    
    subprocessAvailable = True
    widgetVisible = False

    webserviceEnabled = False

    alarmTypeDisplay = "INTERNET RADIO"

    def __init__(self):
        super(InternetRadio, self).__init__()
        try:
            subprocess.Popen(shlex.split("echo Checking if subprocess module is available")) 
        except:
            print("** subprocess module unavailable **")
            self.subprocessAvailable = False

    def setPin(self, pinConfig):
        self.offButton = pinConfig["OFF_BUTTON"]
        self.onButton = pinConfig["ON_BUTTON"]
        self.audioRelayPin = pinConfig["AUDIO_ONE_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.onButton == pinNum):
            if(self.widgetVisible == True):
                s = self.inetradio_widget.getCurrentStation()
                if(s != None):
                    self.stationSelectedCallback(s)
        if(self.offButton == pinNum and self.isPlaying == True):
            self.stop()

    def showWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.inetradio_widget.setVisible(True)
        self.widgetVisible =  True
        self.showButtonIndicators()

    def hideWidget(self):
        """Required for main modules to be inserted into the menu"""
        self.inetradio_widget.setVisible(False)
        self.widgetVisible =  False

    def addMenuWidget(self, parent):
        """Required for main modules to be inserted into the menu"""
        self.inetradio_widget = InternetRadioWidget(parent)       
        self.inetradio_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.inetradio_widget.setVisible(False)
        self.initialize()

    def getMenuIcon(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/globe.svg"

    def getMenuIconSelected(self):
        """Required for main modules to be inserted into the menu"""
        return "icons/globeSelected.svg"

    def getMenuIconHeight(self):
        """Required for main modules to be inserted into the menu"""
        return 65
    def getMenuIconWidth(self):
        """Required for main modules to be inserted into the menu"""
        return 65


    def initialize(self):
        self.loadFromJSON()
        self.inetradio_widget.fillStationList(self.stations)
        self.connect(self.inetradio_widget, QtCore.SIGNAL('stationSelected'), self.stationSelectedCallback)
        self.reset()

        if(self.webserviceEnabled):
            currentLocation = str(os.path.dirname(os.path.realpath(__file__)))
            location =self.findWebServiceFile("InetRadioWebService.py", currentLocation)
            t = Thread(target=self.spinupWebService, args=(self,location,))
            t.start()


    def alarmFired(self, args):     
        for x in range(0, len(self.stations)):
            sta = self.stations[x]
            if(sta.name == args["details"]):
                self.stationSelectedCallback(sta.id)
                break
    

    def getPossibleAlarmDetails(self):
        result = {}
        result["name"] = self.alarmTypeDisplay
        result["moduleName"] = type(self).__name__
        result["alarmType"] = AlarmState.INETRADIO
        possible = []
        for x in range(0, len(self.stations)):
            sta = self.stations[x]
            possible.append(str(sta.name))
        result["options"] = possible
        return result


    def findWebServiceFile(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def spinupWebService(self, parent, location):        
        if(location.find("\\")):
            location = location.replace("\\", "\\\\")
            parent.webservice = subprocess.Popen(shlex.split("python " + location)) 
        else:
            parent.webservice = subprocess.Popen(shlex.split("sudo python " + location)) 


    def stationSelectedCallback(self, stationID):
        if(stationID < len(self.stations)):
            station = self.stations[stationID]
            self.currentPlaylist = self.retrievePlaylist(station.url)          
            if(self.currentPlaylist != None): 
                self.isPlaying = True
                self.play()
                self.audioStatusDisplay = station.name
                self.emit(QtCore.SIGNAL('audioStarted'), self)
                self.emit(QtCore.SIGNAL('pinRequested'), self.audioRelayPin)
                self.showButtonIndicators()


    def showButtonIndicators(self):
        if(self.widgetVisible):
            btns =[]
            btns.append("ON")
            if(self.isPlaying):
                btns.append("OFF")
            self.emit(QtCore.SIGNAL('requestButtonPrompt'),btns)

    def getAudioStatusDisplay(self):
        return self.audioStatusDisplay

    def play(self):
        if(self.subprocessAvailable):
            self.reset()
            self.isPlaying = True
            for pl in self.currentPlaylist:
                subprocess.Popen(shlex.split("mpc add " + pl)) 
                subprocess.Popen(shlex.split("mpc play"))  
                self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "audioStatusChange", "on", None, "ScreenManager") 
        
                  
    def reset(self):
        print("resetting mpc")
        if(self.subprocessAvailable):
            subprocess.Popen(shlex.split("mpc stop")) 
            subprocess.Popen(shlex.split("mpc clear"))        

    def stop(self):
        if(self.isPlaying):
            self.reset()   
            self.inetradio_widget.deselectAllStations()
            self.isPlaying = False
            self.emit(QtCore.SIGNAL('audioStopped'), self)
            self.emit(QtCore.SIGNAL('broadcastModuleRequest'), self, "audioStatusChange", "off", None, "ScreenManager")
        self.showButtonIndicators()
        

    def retrievePlaylist(self, url):       
        url = url.strip() 
        url = url.encode(encoding='UTF-8',errors='strict')
        print("retreiving playlist from: " + str(url))
        buffer = StringIO()
        try:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.perform()
            c.close()
        except:
            return None
        

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
        stationData = None
        buildDefaultData = False

        if(os.path.isfile(self.settingsFilename) == False):
            buildDefaultData = True
        try:
            with open(self.settingsFilename) as data_file:    
                stationData = json.load(data_file)
        except:
            buildDefaultData = True

        if(buildDefaultData == True or stationData == None):
            stationData = []
            with open(self.settingsFilename, 'w') as outfile:
                json.dump(stationData, outfile)

        with open(self.settingsFilename) as data_file:    
            stationData = json.load(data_file)            
            
        self.stations = []
        for x in range(0, len(stationData)):
            s = stationData[x]
            sObj = internetStation(s, x)
            self.stations.append(sObj)

    def dispose(self):
        print("Disposing of Internet Radio")
        self.reset()   

