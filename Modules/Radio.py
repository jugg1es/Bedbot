
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.RadioWidget import *
from Modules.Objects.radioPreset import *
import json
import os.path


class Radio(QObject):


    UsesAudio = True
    ListenForPinEvent = True
    offButton = None
    onButton = None
    audioRelayPin = None

    audioStatusDisplay =""
    Enabled = True    
    menuOrder = 2
    
    isPlaying = False
    
    widgetVisible = False

    radioPresetFile = "radioPresets.json"

    radioPresets = []

    def __init__(self):
        super(Radio, self).__init__()

    def showWidget(self):
        self.radio_widget.setVisible(True)
        self.widgetVisible = True

    def hideWidget(self):
        self.radio_widget.setVisible(False)
        self.widgetVisible = False

    def addMenuWidget(self, parent):
        self.radio_widget = RadioWidget(parent)       
        self.radio_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))  
        self.radio_widget.setVisible(False)
        self.connect(self.radio_widget, QtCore.SIGNAL('presetChanged'), self.presetChangedCallback)        
        self.loadRadioPresets()
        self.radio_widget.fillPresets(self.radioPresets)


    def getMenuIcon(self):
        return "icons/radio-tower.svg"

    def getMenuIconSelected(self):
        return "icons/radio-towerSelected.svg"

    def getMenuIconHeight(self):
        return 65
    def getMenuIconWidth(self):
        return 65

    def presetChangedCallback(self, d):
        print(d)        
        for x in range(0, len(self.radioPresets)):
            pre = self.radioPresets[x]
            print(int(pre.id));
            print(int(d[0]));
            if(int(pre.id) == int(d[0])):
                pre.frequency = str(d[1])
        self.saveRadioPresets()
        self.radio_widget.fillPresets(self.radioPresets)

    def loadRadioPresets(self):
        presetData = None
        buildDefaultData = False

        if(os.path.isfile(self.radioPresetFile) == False):
            buildDefaultData = True
        try:
            with open(self.radioPresetFile) as data_file:    
                presetData = json.load(data_file)
        except:
            buildDefaultData = True

        if(buildDefaultData == True or presetData == None):
            presetData = []
            for x in range(0,3):
                d = {}
                d["frequency"] = "88.1"
                d["id"] = str(x)
                presetData.append(d)

            with open(self.radioPresetFile, 'w') as outfile:
                json.dump(presetData, outfile)

        self.radioPresets = []

        with open(self.radioPresetFile) as data_file:    
            data = json.load(data_file)     

        for x in range(0, len(data)):
            pre = radioPreset(data[x])
            self.radioPresets.append(pre)

    def saveRadioPresets(self):
        data = []
        for x in range(0, len(self.radioPresets)):
            pre = self.radioPresets[x]
            d = {}
            d["frequency"] = str(pre.frequency)
            d["id"] = str(pre.id)
            data.append(d)

        with open(self.radioPresetFile, 'w') as outfile:
             json.dump(data, outfile)




    def setPin(self, pinConfig):
        self.offButton = pinConfig["OFF_BUTTON"]
        self.onButton = pinConfig["ON_BUTTON"]
        self.audioRelayPin = pinConfig["AUDIO_ONE_SWITCH"]

    def processPinEvent(self, pinNum):
        if(self.offButton == pinNum and self.isPlaying == True):
            self.stop()
        elif(self.onButton == pinNum):
            self.play()

    def getAudioStatusDisplay(self):
        return self.audioStatusDisplay

    def play(self):
        if(self.widgetVisible == True):
            print("starting radio")
            self.audioStatusDisplay = str(self.radio_widget.currentFrequency)
            self.isPlaying = True
            self.emit(QtCore.SIGNAL('audioStarted'), self)
            self.emit(QtCore.SIGNAL('pinRequested'), self.audioRelayPin)
                


    def stop(self):
        if(self.isPlaying == True):
            print("stopping radio")
            self.audioStatusDisplay = ""
            self.isPlaying = False
            self.emit(QtCore.SIGNAL('audioStopped'), self)
    
    def dispose(self):
        print("Disposing of Radio")
        try:
            self.stop()
        except:
            print("problem disposing of radio")

