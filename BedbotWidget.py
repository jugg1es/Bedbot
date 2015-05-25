#!/usr/bin/python

from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
import logging
from DynamicMenu import *
from enum import Enum
import json
import shlex 
import subprocess

hasIOLibraries = False


try:
    import RPi.GPIO as IO
    import pigpio
    hasIOLibraries = True
except ImportError:
    print('Raspberry Pi GPIO library not found')


#Required pins
#    Amplifier Power (to transistor)
#    Screen Toggle
#    Sound On
#    Sound Off
#    Snooze
#    Servo Control  (must be pin 18)
#    Open Sensor (servo)
#    Close Sensor (servo)
#    OLED pins (6?)
#    Buzzer

class BedbotWidget(QtGui.QWidget):
    
    loadedModules = None

    currentWidget = None        
    currentWidgetIndex = 2

    listenToButtons = True

    hasIOLibraries = False

    
    autoCloseTimer = None

    currentAudioModule = None
    pinConfig = {}

    pinCallbacks = []
    disabledPins = []

    pinStatusTimer = None

    def __init__(self, parent,modules):
        super(BedbotWidget, self).__init__(parent)

        self.resize(320, 240)      

        self.loadPinConfig()

        self.loadedModules = modules

        self.initializeMenu()

        menuWidgets = []
        for m in self.loadedModules:
            self.connect(m, QtCore.SIGNAL('logEvent'), self.logEvent)

            if(hasattr(m, "Enabled") == True and m.Enabled == True):     
                if(self.moduleHasFunction(m, "addMenuWidget")):
                    if(hasattr(m, "menuOrder") == True): 
                        menuWidgets.insert(m.menuOrder, m)   
                    else:
                       menuWidgets.insert(len(menuWidgets), m)
                if(self.moduleHasFunction(m, "setPin")):
                    self.addPinBasedObject(m)

                if(hasattr(m, "UsesAudio") == True and m.UsesAudio == True): 
                    self.connect(m, QtCore.SIGNAL('audioStarted'), self.audioStartedCallback)
                    self.connect(m, QtCore.SIGNAL('audioStopped'), self.audioStoppedCallback)
                    self.connect(m, QtCore.SIGNAL('pinRequested'), self.pinRequestedCallback)


        for i in range(0,len(menuWidgets)):
            menuWidgets[i].menuOrder = i
            self.addMainWidget(menuWidgets[i])

        self.menu_widget.configureMenu()          
        self.toggleMainMenu(True)
        QtCore.QMetaObject.connectSlotsByName(self)   


    def pinRequestedCallback(self, pin):
        self.pinEventCallback(pin)


    def audioStoppedCallback(self, sourceModule):
        self.currentAudioModule = None
        self.stopAllAudio(self.currentAudioModule)
        self.statusDisplay.setText("")

    def audioStartedCallback(self, sourceModule):
        self.currentAudioModule = sourceModule
        self.stopAllAudio(self.currentAudioModule)
        self.statusDisplay.setText("")
        if(self.moduleHasFunction(self.currentAudioModule, "getAudioStatusDisplay")):
            self.statusDisplay.setText(self.currentAudioModule.getAudioStatusDisplay())

    def stopAllAudio(self, ignoredModule):
        for m in self.loadedModules:
            if(hasattr(m, "UsesAudio") == True and m.UsesAudio == True and (ignoredModule == None or (ignoredModule != None and m != ignoredModule))):
                if(self.moduleHasFunction(m, "stop")):
                    m.stop()


    def logEvent(self, evtStr):
        print(evtStr)
        logging.info(str(evtStr))  


    def initializeMenu(self):
        self.menu_widget = DynamicMenu(self)
        self.menu_widget.setGeometry(QtCore.QRect(10, 10, 320, 190))  
        self.menu_widget.setVisible(True)
        self.connect(self.menu_widget, QtCore.SIGNAL('showWidget'), self.showWidgetCallback)

        self.menuButton = QSvgWidget("icons/three-bars.svg", self)
        self.menuButton.setGeometry(QtCore.QRect(10,200,30,35))
        pressableSender(self.menuButton).connect(self.menuButtonPressed)
        releaseableSender(self.menuButton).connect(self.menuButtonReleased)
        self.menuButton.setVisible(False)


        font = QtGui.QFont()
        font.setPointSize(15)
        self.statusDisplay = QtGui.QLabel(self)
        self.statusDisplay.setGeometry(QtCore.QRect(50, 200, 260, 35))
        self.statusDisplay.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusDisplay.setStyleSheet('color: #eaf736')
        self.statusDisplay.setFont(font)
        pressableSender(self.statusDisplay).connect(self.audioStatusPressed)

    def audioStatusPressed(self, obj):
        if(self.currentAudioModule != None):
            self.menu_widget.setMenuItemSelected(self.currentAudioModule)
            self.showWidgetCallback(self.currentAudioModule)

    def toggleMainMenu(self, showMenu):
        if(showMenu):
            self.hideMainWidgets()
            self.autoCloseTimer = QTimer()
            self.autoCloseTimer.timeout.connect(self.autoCloseMainMenu)
            self.autoCloseTimer.start(5000)
        self.menuButton.setVisible(not showMenu)
        self.menu_widget.setVisible(showMenu)

    def autoCloseMainMenu(self):
        if(self.currentWidget != None):
            self.showWidgetCallback(self.currentWidget)
        

    def menuButtonReleased(self, obj):
        self.menuButton.load("icons/three-bars.svg")
        self.toggleMainMenu(True)

    def menuButtonPressed(self, obj):
        self.menuButton.load("icons/three-barsSelected.svg")


    def contextButtonPressed(self):
        print("context button pressed")

    
    def showWidgetCallback(self, w):
        if(self.autoCloseTimer != None):
            self.autoCloseTimer.stop()
            self.autoCloseTimer = None
        self.hideMainWidgets()
        w.showWidget()
        self.currentWidget = w
        self.toggleMainMenu(False)

    def hideMainWidgets(self):
        for m in self.loadedModules:
            if(hasattr(m, "Enabled") == True and m.Enabled == True):
                if(self.moduleHasFunction(m, "hideWidget")):
                    m.hideWidget()
        self.menu_widget.setVisible(False)

    def moduleHasFunction(self, m, functionName):
        funct = getattr(m, functionName, None)
        if(callable(funct)):
            return True
        return False

    def addMainWidget(self, w):
        w.addMenuWidget(self)
        self.menu_widget.addMenuItem(w)

    def addPinBasedObject(self, w):
        w.setPin(self.pinConfig)
        if(hasattr(w, "ListenForPinEvent") == True and w.ListenForPinEvent == True):
            self.connect(w, QtCore.SIGNAL('pinEventCallback'), self.pinEventCallback)

    def pinEventCallback(self, channel):
        self.logEvent("pin callback for channel: " + str(channel))
        for m in self.loadedModules:
            if(self.moduleHasFunction(m, "processPinEvent")):
                m.processPinEvent(channel)

    def pigpioCallback(self, gpio, level, tick):
       #print(gpio, level, tick)
       self.logEvent("pin callback for channel: " + str(gpio))
       if(self.disabledPins.index(gpio) == -1):
           for m in self.loadedModules:
                if(self.moduleHasFunction(m, "processPinEvent")):
                    m.processPinEvent(gpio)
           self.disabledPins.append(gpio)




    def loadPinConfig(self):      
        
        
        with open("pinConfig.json") as data_file:    
            data = json.load(data_file)    
        self.pinConfig = {}
        
        if(hasIOLibraries):
            pi = pigpio.pi()
            #IO.setmode(IO.BCM)

        for x in range(0, len(data["pins"])):
            p = data["pins"][x]
            self.pinConfig[p["type"]] = p["pin"]
            if(hasIOLibraries and self.listenToButtons == True and p["listenForPress"] == True):
                self.logEvent("adding event to pin: " + str(p["pin"]))
                pi.set_pull_up_down(p["pin"], pigpio.PUD_DOWN)
                cb1 = pi.callback(p["pin"], pigpio.RISING_EDGE, self.pigpioCallback)
                self.pinCallbacks.append(cb1)
                #IO.setup(p["pin"], IO.IN, pull_up_down = IO.PUD_DOWN)
                #IO.add_event_detect(p["pin"], IO.RISING, callback=self.pinEventCallback, bouncetime=3000)



    def doClose(self):        
        try:
            IO.cleanup()
        except BaseException:
            print("problem cleaning up IO")

        for m in self.loadedModules:
            try:
                m.dispose()
            except BaseException:
                print("problem disposing")
                print(m)

        print("finished closing widgets")


      
        
        
        
