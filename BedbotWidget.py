
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
import os


hasIOLibraries = False


try:
    import RPi.GPIO as IO
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

    


    pinConfig = {}

    def __init__(self, parent,modules):
        super(BedbotWidget, self).__init__(parent)

        self.resize(320, 240)      

        self.loadPinConfig()

        self.loadedModules = modules

        self.initializeMenu()

        for m in self.loadedModules:
            self.connect(m, QtCore.SIGNAL('logEvent'), self.logEvent)
            if(hasattr(m, "Enabled") == True and m.Enabled == True):                
                if(self.moduleHasFunction(m, "addMenuWidget")):
                    self.addMainWidget(m)
                if(self.moduleHasFunction(m, "setPin")):
                    self.addPinBasedObject(m)


        self.menu_widget.configureMenu()            
        QtCore.QMetaObject.connectSlotsByName(self)    

    def logEvent(self, evtStr):
        print(evtStr)
        logging.info(str(evtStr))  
       
        try:
            os.system("echo \"" + str(evtStr) + "\" | wall")  
        except Exception:
            print("no wall command")
        


    def initializeMenu(self):
        self.menu_widget = DynamicMenu(self)
        self.menu_widget.setGeometry(QtCore.QRect(0, 85, 320, 70))  
        self.menu_widget.setVisible(True)
        self.connect(self.menu_widget, QtCore.SIGNAL('showWidget'), self.showWidgetCallback)

    def contextButtonPressed(self):
        print("context button pressed")

    
    def showWidgetCallback(self, w):
        self.hideMainWidgets()
        w.showWidget()

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

    def loadPinConfig(self):      
        
        with open("pinConfig.json") as data_file:    
            data = json.load(data_file)    
        self.pinConfig = {}

        self.logEvent("IO libraries initialized: " + str(hasIOLibraries))

        if(hasIOLibraries):
            IO.setmode(IO.BCM)

        for x in range(0, len(data["pins"])):
            p = data["pins"][x]
            self.pinConfig[p["type"]] = p["pin"]
            if(hasIOLibraries and self.listenToButtons == True and p["listenForPress"] == True):
                self.logEvent("adding event to pin: " + str(p["pin"]))
                IO.setup(p["pin"], IO.IN, pull_up_down = IO.PUD_DOWN)
                IO.add_event_detect(p["pin"], IO.RISING, callback=self.pinEventCallback, bouncetime=3000)



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


      
        
        
        
