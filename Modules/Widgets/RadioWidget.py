
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from inspect import currentframe
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
from perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
from Modules.Widgets.Popup import *
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
        releaseable(self.slideUpButton).connect(self.doFreqUpReleased)
        pressable(self.slideUpButton).connect(self.doFreqUpPressed)        
        
        self.slideDownFrame = QFrame(self)        
        self.slideDownFrame.setGeometry(QtCore.QRect(50, 15, 50, 50))  
        self.slideDownFrame.setFrameShape(QtGui.QFrame.Box)
        self.slideDownFrame.setFrameShadow(QtGui.QFrame.Plain)
        self.slideDownFrame.setStyleSheet(self.buttonDefaultStyle)
        
        self.slideDownButton = QSvgWidget("icons/backward2.svg", self.slideDownFrame)
        self.slideDownButton.setGeometry(QtCore.QRect(0, 5, 40, 40))    
        releaseable(self.slideDownButton).connect(self.doFreqDownReleased) 
        pressable(self.slideDownButton).connect(self.doFreqDownPressed)

        self.horizontalLayoutWidget = QtGui.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 100, 300, 80))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setAlignment(self.horizontalLayoutWidget, QtCore.Qt.AlignCenter)
        self.horizontalLayout.setMargin(0)

        QtCore.QMetaObject.connectSlotsByName(self)       
        
    def fillPresets(self, presets):
        print("filling presets")
        self.clearPresets()
        font = QtGui.QFont()
        font.setPointSize(20)
        for x in range(0, len(presets)):
            pre = presets[x]
            print("preset " + str(pre.id) + " freq: " + str(pre.frequency))
            testLabel = QtGui.QLabel(str(pre.frequency))
            testLabel.setStyleSheet('color: #fff')
            testLabel.setAlignment(QtCore.Qt.AlignCenter)
            testLabel.setFont(font)
            testLabel.freq = pre.frequency;
            testLabel.preID = pre.id
            holdable(testLabel).connect(self.presetChangePressed)
            clickable(testLabel).connect(self.presetSelected)
            self.horizontalLayout.addWidget(testLabel)

    def presetSelected(self, obj):
        print("preset selected: " + str(obj.freq))
        self.currentFrequency = float(obj.freq)
        self.updateRadioFrequency()


    def presetChangePressed(self, obj):
        print("preset change pressed: " + str(obj.freq))
        confirm = Popup(self)
        self.connect(confirm, QtCore.SIGNAL('popupResult'), self.confirmResultCallback)
        confirm.doConfirm("Change Preset?", obj.preID)

    def confirmResultCallback(self, obj):
        args = obj;
        if(args[0] == "OK"):
            self.emit(QtCore.SIGNAL('presetChanged'), [args[1], self.currentFrequency])


    def clearPresets(self):
        for i in reversed(range(self.horizontalLayout.count())): 
            self.horizontalLayout.itemAt(i).widget().setParent(None)

        
    def updateRadioFrequency(self):
        self.frequencyDisplay.display("{0:.1f}".format(self.currentFrequency))
        newFreq = str(self.frequencyDisplay.value())
    
    def isFreqValid(self, freq):
        if(freq >= 88.1 and freq <= 108.1):
            return True
        else:
            return False
    
    
    def doFreqDownReleased(self):
        self.slideDownFrame.setStyleSheet(self.buttonDefaultStyle)
        self.stopTimer()
        
    def doFreqDownPressed(self):
        self.slideDownFrame.setStyleSheet(self.buttonPressedStyle)
        self.scanDirection = "down"
        self.startTimer()        
        
        
    def doFreqUpReleased(self):
        self.slideUpFrame.setStyleSheet(self.buttonDefaultStyle)
        self.stopTimer()
        
    def doFreqUpPressed(self):
        self.slideUpFrame.setStyleSheet(self.buttonPressedStyle)
        self.scanDirection = "up"
        self.startTimer()     
        
    def startTimer(self):
        self.scanInterval = 0.5
        self.processTimer()
        
        # perpetualTimer(self.scanInterval, self.processTimer)
    
    def processTimer(self):        
        if(self.scanDirection != "none"):            
            self.changeFrequency()
            self.scanTimer =  Timer(self.scanInterval,self.processTimer) 
            self.scanInterval = self.scanInterval / 1.5
            if(self.scanInterval < 0.05):
                self.scanInterval = 0.05;
            self.scanTimer.start()
        else:
            self.stopTimer()
        
    def stopTimer(self):
        if(self.scanTimer != None):
            self.scanTimer.cancel()
            self.scanTimer = None
        self.scanDirection = "none"
        
        
    
    def changeFrequency(self):
        
        freq = self.currentFrequency
        if(self.scanDirection == "down"):
            freq = freq - 0.1;
        elif (self.scanDirection =="up"):
            freq = freq + 0.1;
        if(self.isFreqValid(freq)):
            self.currentFrequency = freq
            self.updateRadioFrequency()
        
    
    
        
    
        