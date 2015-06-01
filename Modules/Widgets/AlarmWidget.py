
from PyQt4 import QtCore, QtGui, uic
import datetime
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from configparser import SafeConfigParser
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
from Modules.Objects.alarmSetting import *
from Modules.Objects.alarmConfig import *
from Modules.Widgets.Popup import *
import json

    
class AlarmWidget(QtGui.QWidget):
    
    configManager = None
    
    pandoraEnabled = False
    
    alarmSettings = None
    settingsFilename = "alarmConfig.ini"
    
    presetUnselectedStyle = "font-size:20px;background-color:#000; border: 2px solid #000;color:#4c4c4c;"
    presetSelectedStyle = "font-size:20px;border: 2px solid #fff; color:#4c4c4c;"
    presetOnStyle ="color:#fff;"
    currentPreset = None
    
    optionsUnselectedStyle = "font-size:11pt;border: 2px solid #000; color:#fff;"
    optionsSelectedStyle = "font-size:11pt; color:#fff;border: 2px solid #fff;"

    def __init__(self, parent):
        super(AlarmWidget, self).__init__(parent)
        self.resize(320, 210)
        self.connect(self, QtCore.SIGNAL('alarmPresetsLoaded'), self.alarmPresetsLoadedCallback)

    def doAlarmSnooze(self):
        print("snooze")
        
    def checkAlarms(self):
        currentTime = datetime.datetime.now()
        activeAlarms = []
        for x in range(0, 3):
            current = self.alarmSettings[x]
            if(current.state != AlarmState.OFF and current.timeSetting.strftime("%I:%M %p") == currentTime.strftime("%I:%M %p")):
                activeAlarms.append(current)
        return activeAlarms
    
    def setCurrentPreset(self, index):
        if(self.alarmSettings != None):
            self.currentPreset = self.alarmSettings[index]
            self.updateTimeDisplay()
            self.configureAlarmStateDisplay()
            
    def updateTimeDisplay(self):
        self.lblHour.setText(self.currentPreset.getHourString())   
        self.lblMinute.setText(self.currentPreset.getMinuteString())  
        
        
    def setPresetStyle(self, preset, widget):
        widget.setText(preset.getDisplayTimeString())
        if(preset == self.currentPreset):
            if(AlarmState(preset.state) != AlarmState.OFF):
                widget.setStyleSheet(self.presetSelectedStyle + self.presetOnStyle)
            else:
                widget.setStyleSheet(self.presetSelectedStyle)
        else:
            if(AlarmState(preset.state) != AlarmState.OFF):
                widget.setStyleSheet(self.presetUnselectedStyle + self.presetOnStyle)
            else:
                widget.setStyleSheet(self.presetUnselectedStyle)
    
    def loadPresetDisplay(self):
        if(self.alarmSettings != None):
            self.setPresetStyle(self.alarmSettings[0], self.alarmPreset1)
            self.setPresetStyle(self.alarmSettings[1], self.alarmPreset2)
            self.setPresetStyle(self.alarmSettings[2], self.alarmPreset3)
            
    
    def selectPreset(self):
        index = self.sender().name
        self.setCurrentPreset(index)
        self.currentPreset = self.alarmSettings[index]
    
    def configureAlarmStateDisplay(self):
        self.loadPresetDisplay()

        if(self.currentPreset.state == AlarmState.OFF):
            self.btnAlarmStatus.setText("ALARM OFF")
        elif(self.currentPreset.state == AlarmState.RADIO):
            self.btnAlarmStatus.setText("RADIO")
        elif(self.currentPreset.state == AlarmState.INETRADIO):
            self.btnAlarmStatus.setText("INTERNET RADIO")
            
        self.lblAM.setStyleSheet(self.optionsUnselectedStyle)        
        self.lblPM.setStyleSheet(self.optionsUnselectedStyle)
        if(self.currentPreset.getTimeOfDayType() == TimeOfDay.AM):
            self.lblAM.setStyleSheet(self.optionsSelectedStyle)
        elif(self.currentPreset.getTimeOfDayType() == TimeOfDay.PM):
            self.lblPM.setStyleSheet(self.optionsSelectedStyle)
        
    
    def setAlarmState(self):
        self.emit(QtCore.SIGNAL('selectAlarmType'))

    def setAlarmStateCallback(self, state):
        newState = AlarmState(state)
        self.currentPreset.state = state        
        self.configManager.saveSettings(self.alarmSettings)
        self.configureAlarmStateDisplay()
        
    def setTimeOfDay(self, obj):
        newTOD = TimeOfDay(obj.name)
        self.currentPreset.setTimeOfDayType(newTOD)
        self.configManager.saveSettings(self.alarmSettings)
        self.updateTimeDisplay()
        self.configureAlarmStateDisplay()
        



    def alarmPresetsLoadedCallback(self):
        self.initializeControls()
        
    def initializeAlarmPresets(self, parent):     
        parent.configManager = alarmConfig(parent.settingsFilename)
        parent.alarmSettings = parent.configManager.loadSettings()
        for i in range(len(parent.alarmSettings)):
            setting = parent.alarmSettings[i]
            print(setting.getDisplayTimeString())
        parent.emit(QtCore.SIGNAL('alarmPresetsLoaded'), parent)

    def initialize(self):
        t = Thread(target=self.initializeAlarmPresets, args=(self,))
        t.start()


    def setHour(self):
        self.emit(QtCore.SIGNAL('selectTimeHour'))

    def setHourCallback(self, newHour):
        if(int(newHour) >= 1 and int(newHour) <= 12):
            self.currentPreset.setHour(int(newHour))
            self.updateTimeDisplay()  
            self.configureAlarmStateDisplay()
            self.configManager.saveSettings(self.alarmSettings)

    def setMinute(self):
        self.emit(QtCore.SIGNAL('selectTimeMinute'))

    def setMinuteCallback(self, newMinute):
        if(int(newMinute) >= 0 and int(newMinute) < 60):
            self.currentPreset.setMinute(int(newMinute))
            self.updateTimeDisplay()  
            self.configureAlarmStateDisplay()
            self.configManager.saveSettings(self.alarmSettings)

    def initializeControls(self):

       
        self.horizontalLayoutWidget = QtGui.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 321, 41))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        
       
        self.alarmPreset1 = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.alarmPreset1.setStyleSheet(self.presetUnselectedStyle)
        self.alarmPreset1.name = 0
        self.alarmPreset1.clicked.connect(self.selectPreset)
        self.horizontalLayout.addWidget(self.alarmPreset1)
        
        self.alarmPreset2 = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.alarmPreset2.name = 1
        self.alarmPreset2.clicked.connect(self.selectPreset)
        self.alarmPreset2.setStyleSheet(self.presetUnselectedStyle)
        self.horizontalLayout.addWidget(self.alarmPreset2)
        self.alarmPreset3 = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.alarmPreset3.name = 2
        self.alarmPreset3.clicked.connect(self.selectPreset)
        self.alarmPreset3.setStyleSheet(self.presetUnselectedStyle)
        self.horizontalLayout.addWidget(self.alarmPreset3)
        
        
        timeFont = QtGui.QFont()
        timeFont.setPointSize(50)
        timeFont.setStyleStrategy(QtGui.QFont.PreferAntialias)
        timeFont.setStyleHint(QtGui.QFont.SansSerif)
        
        self.label = QtGui.QLabel(":", self)
        self.label.setGeometry(QtCore.QRect(105, 50, 21, 61))
        self.label.setFont(timeFont)
        self.label.setStyleSheet("color: #fff")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.lblHour = QtGui.QLabel(self)
        self.lblHour.setGeometry(QtCore.QRect(25, 60, 81, 61))
        self.lblHour.setFont(timeFont)
        self.lblHour.setStyleSheet("color: #fff")
        pressable(self.lblHour).connect(self.setHour)
        self.lblHour.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        
        self.lblMinute = QtGui.QLabel(self)
        self.lblMinute.setGeometry(QtCore.QRect(125, 60, 81, 61))
        self.lblMinute.setFont(timeFont)
        self.lblMinute.setStyleSheet("color: #fff")
        pressable(self.lblMinute).connect(self.setMinute)
        self.lblMinute.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        
        
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(210, 60, 41, 61))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        
        self.lblAM = QtGui.QLabel("AM", self.verticalLayoutWidget)             
        self.lblAM.name = TimeOfDay.AM        
        pressableSender(self.lblAM).connect(self.setTimeOfDay)
        self.lblAM.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.lblAM)
        self.lblPM = QtGui.QLabel("PM", self.verticalLayoutWidget)
        self.lblPM.name = TimeOfDay.PM
        pressableSender(self.lblPM).connect(self.setTimeOfDay)
        self.lblPM.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.lblPM)        


        self.btnAlarmStatus = QtGui.QLabel("ALARM OFF", self)        
        self.btnAlarmStatus.setStyleSheet("color: #fff; font-size:22pt;")
        xLocation =  (320/2) - (150/2)
        self.btnAlarmStatus.setGeometry(QtCore.QRect((320/2) - (250/2), 130, 250, 60))
        pressable(self.btnAlarmStatus).connect(self.setAlarmState)
        self.btnAlarmStatus.setAlignment(QtCore.Qt.AlignCenter)     
           
        
        
        self.setCurrentPreset(0)
        
        
        
        QtCore.QMetaObject.connectSlotsByName(self)       
        
        
    
       
       

    
        