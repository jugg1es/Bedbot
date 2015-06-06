
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

    alarmTimeSectionStyle = "border: 4px solid #444444; border-radius: 20px; padding:5px; color: #fff"
    alarmTypeSectionStyle = "border: 4px solid #444444; border-radius: 20px; padding:5px; color: #fff; font-size:18pt;"
    alarmDetailsSectionStyle = "color: #fff; font-size:13pt;"

    def __init__(self, parent):
        super(AlarmWidget, self).__init__(parent)
        self.resize(320, 210)
        self.connect(self, QtCore.SIGNAL('alarmPresetsLoaded'), self.alarmPresetsLoadedCallback)

    def setCurrentPreset(self, index):
        if(self.alarmSettings != None):
            self.currentPreset = self.alarmSettings[index]
            self.updateTimeDisplay()
            self.configureAlarmStateDisplay()
            
    def updateTimeDisplay(self):
        self.lblHour.setText(self.currentPreset.getHourString())   
        self.lblMinute.setText(self.currentPreset.getMinuteString())  
        
    def cycleSelectedAlarm(self):
        index = self.alarmSettings.index(self.currentPreset)
        if(index == len(self.alarmSettings)-1):
            index = 0
        else:
            index += 1

        self.setCurrentPreset(index)
        self.currentPreset = self.alarmSettings[index]
        

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

        self.btnAlarmDetails.setVisible(False)

        if(self.currentPreset.state == AlarmState.OFF):
            self.btnAlarmStatus.setText("ALARM OFF")
        elif(self.currentPreset.state == AlarmState.RADIO):
            self.btnAlarmStatus.setText("RADIO")
            self.btnAlarmDetails.setVisible(True)
            self.btnAlarmDetails.setText(self.currentPreset.details)
        elif(self.currentPreset.state == AlarmState.INETRADIO):
            self.btnAlarmStatus.setText("INTERNET RADIO")
            self.btnAlarmDetails.setVisible(True)
            self.btnAlarmDetails.setText(self.currentPreset.details)
            
        self.lblAM.setStyleSheet(self.optionsUnselectedStyle)        
        self.lblPM.setStyleSheet(self.optionsUnselectedStyle)
        if(self.currentPreset.getTimeOfDayType() == TimeOfDay.AM):
            self.lblAM.setStyleSheet(self.optionsSelectedStyle)
        elif(self.currentPreset.getTimeOfDayType() == TimeOfDay.PM):
            self.lblPM.setStyleSheet(self.optionsSelectedStyle)
        
    
    def setAlarmState(self):
        self.emit(QtCore.SIGNAL('selectAlarmType'))

    def setAlarmStateCallback(self, state, details="", moduleName=""):
        newState = AlarmState(state)
        self.currentPreset.state = state        
        self.currentPreset.details = details
        self.currentPreset.moduleName = moduleName
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

    def setTestAlarm(self):
        """Sets an alarm in 1 minute for testing purposes"""
        n = datetime.datetime.now()# + datetime.timedelta(minutes=1)
        tod = TimeOfDay.AM
        h = n.hour
        if(h > 12):
            h -= 12
            tod = TimeOfDay.PM
        m = n.minute

        self.currentPreset.setHour(int(h))
        self.currentPreset.setMinute(int(m))
        self.currentPreset.setTimeOfDayType(tod)
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
        timeFont.setPointSize(48)
        timeFont.setStyleStrategy(QtGui.QFont.PreferAntialias)
        timeFont.setStyleHint(QtGui.QFont.SansSerif)
        
        self.label = QtGui.QLabel(":", self)
        self.label.setGeometry(QtCore.QRect(120, 44, 21, 61))
        self.label.setFont(timeFont)
        self.label.setStyleSheet("color: #fff")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.lblHour = QtGui.QLabel(self)

        self.lblHour.setGeometry(QtCore.QRect(30, 42, 90,74))
        self.lblHour.setFont(timeFont)
        self.lblHour.setStyleSheet(self.alarmTimeSectionStyle)
        pressable(self.lblHour).connect(self.setHour)
        self.lblHour.setAlignment(QtCore.Qt.AlignCenter)
        
        self.lblMinute = QtGui.QLabel(self)
        self.lblMinute.setGeometry(QtCore.QRect(140, 42, 90, 74))
        self.lblMinute.setFont(timeFont)
        self.lblMinute.setStyleSheet(self.alarmTimeSectionStyle)
        pressable(self.lblMinute).connect(self.setMinute)
        self.lblMinute.setAlignment(QtCore.Qt.AlignCenter)
        
        
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(250, 50, 41, 61))
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
        self.btnAlarmStatus.setStyleSheet(self.alarmTypeSectionStyle)
        self.btnAlarmStatus.setGeometry(QtCore.QRect((320/2) - (280/2), 120, 280, 40))
        pressable(self.btnAlarmStatus).connect(self.setAlarmState)
        self.btnAlarmStatus.setAlignment(QtCore.Qt.AlignCenter)     
           
        self.btnAlarmDetails = QtGui.QLabel("88.1", self)        
        self.btnAlarmDetails.setStyleSheet(self.alarmDetailsSectionStyle)
        self.btnAlarmDetails.setGeometry(QtCore.QRect((320/2) - (200/2), 160, 200, 30))
        self.btnAlarmDetails.setAlignment(QtCore.Qt.AlignCenter)   
        self.btnAlarmDetails.setVisible(False)
        
        self.setCurrentPreset(0)
        
        
        
        QtCore.QMetaObject.connectSlotsByName(self)       
        
        
    
       
       

    
        