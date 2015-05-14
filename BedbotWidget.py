
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
import logging
from DynamicMenu import *

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


    audioOnButtonPin = 5
    audioOffButtonPin = 6
    contextButtonPin = 12
    screenToggleButtonPin = 22
    buttonPowerPin = 27
    audioToggleOne = 4
    audioToggleTwo = 17
    
    buzzerPin = 16
    
    def __init__(self, parent,modules):
        super(BedbotWidget, self).__init__(parent)

        self.resize(320, 240)      

        self.loadedModules = modules

        self.menu_widget = DynamicMenu(self)
        self.menu_widget.setGeometry(QtCore.QRect(0, 85, 320, 70))  
        self.menu_widget.setVisible(True)
        self.connect(self.menu_widget, QtCore.SIGNAL('showWidget'), self.showWidget)


        for m in self.loadedModules:
            if(m.isMainWidget):
                self.addMainWidget(m)


        self.menu_widget.configureMenu()
            
        QtCore.QMetaObject.connectSlotsByName(self)    
    
    def showWidget(self, w):
        print(w)

    def addMainWidget(self, w):
        w.addWidget(self)
        self.menu_widget.addMenuItem(w)

    def contextButtonPressed(self):
        print("context button pressed")

    def doClose(self):        
        for m in self.loadedModules:
            try:
                m.dispose()
            except BaseException:
                print("problem disposing")


      
        
        
        
