
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from inspect import currentframe
from Helpers.clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
from Helpers.perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.Popup import *
from Modules.Widgets.ButtonIndicator import *
import json

    
class RadioWidget(QtGui.QWidget):
    
    currentFrequency = 88.1
    scanInterval = 0.5
    scanDirection = "none"
    scanTimer = None
    playing = False
    radioManager = None
    
    buttonDefaultStyle = "border: 2px solid #000;"
    buttonPressedStyle = "border: 2px solid #fff;"

    presetFrameStyle = "border: 2px solid #7f7f7f; border-radius: 10px; margin:10px; "
    presetFrameSelectedStyle = "border: none; background-color: #fff200; border-radius: 10px; margin:10px; "


    presetContentsStyle = "border: none; color:#fff"
    presetContentsSelectedStyle = "border: none; color:#000"


    settingPreset = False
    
    def __init__(self, parent):
        super(RadioWidget, self).__init__(parent)
        self.resize(320, 240)
                
        freqFont = QtGui.QFont()
        freqFont.setPointSize(35)
        
        self.frequencyDisplay = QtGui.QLCDNumber(self)
        self.frequencyDisplay.setGeometry(QtCore.QRect(90, 15, 131, 51))
        self.frequencyDisplay.setFont(freqFont)
        self.frequencyDisplay.setStyleSheet('color: white')
        self.frequencyDisplay.setFrameShape(QtGui.QFrame.NoFrame)
        self.updateRadioFrequency();
        
       

        self.slideUpFrame = QFrame(self)        
        self.slideUpFrame.setGeometry(QtCore.QRect(230, 15, 50, 50))  
        self.slideUpFrame.setFrameShape(QtGui.QFrame.Box)
        self.slideUpFrame.setFrameShadow(QtGui.QFrame.Plain)
        self.slideUpFrame.setStyleSheet(self.buttonDefaultStyle)
        
        self.slideUpButton = QSvgWidget("icons/forward3.svg", self.slideUpFrame)
        self.slideUpButton.setGeometry(QtCore.QRect(5, 5, 40, 40))  

        pressable(self.slideUpButton).connect(self.doFreqUpPressed)        
        
        self.slideDownFrame = QFrame(self)        
        self.slideDownFrame.setGeometry(QtCore.QRect(50, 15, 50, 50))  
        self.slideDownFrame.setFrameShape(QtGui.QFrame.Box)
        self.slideDownFrame.setFrameShadow(QtGui.QFrame.Plain)
        self.slideDownFrame.setStyleSheet(self.buttonDefaultStyle)
        
        self.slideDownButton = QSvgWidget("icons/backward2.svg", self.slideDownFrame)
        self.slideDownButton.setGeometry(QtCore.QRect(0, 5, 40, 40))    

        pressable(self.slideDownButton).connect(self.doFreqDownPressed)


        self.horizontalLayoutWidget = QtGui.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 100, 300, 80))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setAlignment(self.horizontalLayoutWidget, QtCore.Qt.AlignCenter)
        self.horizontalLayout.setMargin(0)

        QtCore.QMetaObject.connectSlotsByName(self)       
        
    def fillPresets(self, presets, selected=False):
        self.settingPreset = selected
        print("Filling Radio presets")
        self.clearPresets()
        font = QtGui.QFont()
        font.setPointSize(18)
        self.changingPreset = None
        for x in range(0, len(presets)):
            pre = presets[x]
            presetButton = QFrame()       
            presetButton.setFrameShape(QtGui.QFrame.Box)
            
            if(selected == True):
                presetButton.setStyleSheet(self.presetFrameSelectedStyle)
            else:
                presetButton.setStyleSheet(self.presetFrameStyle)
            presetButton.freq = pre.frequency;
            presetButton.preID = pre.id
            releaseableSender(presetButton).connect(self.presetSelected)

            presetDisplay = QtGui.QLabel(presetButton)
            presetDisplay.setGeometry(QtCore.QRect(5,0,90,80))
            presetDisplay.setAlignment(QtCore.Qt.AlignCenter)
            if(selected == True):
                presetDisplay.setStyleSheet(self.presetContentsSelectedStyle)
            else:
                presetDisplay.setStyleSheet(self.presetContentsStyle)
            presetDisplay.setFont(font)
            presetDisplay.setText(str(pre.frequency))


            self.horizontalLayout.addWidget(presetButton)
    
    def presetSelected(self, obj):     
        if(self.settingPreset):
            self.emit(QtCore.SIGNAL('presetChanged'), [obj.preID, self.currentFrequency])
        else:
            print("preset selected: " + str(obj.freq))
            self.currentFrequency = float(obj.freq)
            self.updateRadioFrequency()
            self.emit(QtCore.SIGNAL('frequencyChanged'),self.currentFrequency)

    def clearPresets(self):
        for i in reversed(range(self.horizontalLayout.count())): 
            self.horizontalLayout.itemAt(i).widget().deleteLater()

        
    def updateRadioFrequency(self):
        self.frequencyDisplay.display("{0:.1f}".format(self.currentFrequency))
        newFreq = str(self.frequencyDisplay.value())
    
    def isFreqValid(self, freq):
        if(freq >= 88.1 and freq <= 108.1):
            return True
        else:
            return False
    
    
    def doFreqDownPressed(self):
        self.scanDirection = "down"
        self.doChangeFrequency()
        
        
    def doFreqUpPressed(self):
        self.scanDirection = "up"
        self.doChangeFrequency()

    def doChangeFrequency(self):
        t = Thread(target=self.changeFrequency, args=(self,))        
        t.start()        
        
    
    def changeFrequency(self, parent):
        
        freq = parent.currentFrequency
        if(self.scanDirection == "down"):
            freq = freq - 0.2;
        elif (self.scanDirection =="up"):
            freq = freq + 0.2;
        if(self.isFreqValid(freq)):
            parent.currentFrequency = freq
            parent.updateRadioFrequency()
        
    
    
        
    
        