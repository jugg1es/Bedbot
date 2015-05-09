
from PyQt4 import QtCore, QtGui, uic
import datetime
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from configparser import SafeConfigParser
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
from Objects.alarmSetting import *
from Objects.alarmConfig import *
    

    
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
    
    def doAlarmSnooze(self):
        print("snooze")
        
    def checkAlarms(self):
        currentTime = datetime.datetime.now()
        activeAlarms = []
        for x in range(0, 3):
            current = self.alarmSettings[x]
            #alarmTime = datetime.datetime.strftime("%H")
            if(current.state != AlarmState.OFF and current.timeSetting.strftime("%I:%M %p") == currentTime.strftime("%I:%M %p")):
                activeAlarms.append(current)
        return activeAlarms
        
        
    def initializeAlarmPresets(self):        
        if(self.alarmSettings == None):
            self.configManager = alarmConfig(self.settingsFilename)
            self.alarmSettings = self.configManager.loadSettings()
    
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
        self.lblOnRadio.setStyleSheet(self.optionsUnselectedStyle)
        self.lblOnBuzzer.setStyleSheet(self.optionsUnselectedStyle)
        
        if(self.pandoraEnabled):
            self.lblOnPandora.setStyleSheet(self.optionsUnselectedStyle)
        self.lblOff.setStyleSheet(self.optionsUnselectedStyle)
        if(self.currentPreset.state == AlarmState.OFF):
            self.lblOff.setStyleSheet(self.optionsSelectedStyle)
        elif(self.currentPreset.state == AlarmState.BUZZ):
            self.lblOnBuzzer.setStyleSheet(self.optionsSelectedStyle)
        elif(self.pandoraEnabled == True and self.currentPreset.state == AlarmState.PANDORA):
            self.lblOnPandora.setStyleSheet(self.optionsSelectedStyle)
        else:
            self.lblOnRadio.setStyleSheet(self.optionsSelectedStyle)
            
        self.lblAM.setStyleSheet(self.optionsUnselectedStyle)        
        self.lblPM.setStyleSheet(self.optionsUnselectedStyle)
        if(self.currentPreset.getTimeOfDayType() == TimeOfDay.AM):
            self.lblAM.setStyleSheet(self.optionsSelectedStyle)
        elif(self.currentPreset.getTimeOfDayType() == TimeOfDay.PM):
            self.lblPM.setStyleSheet(self.optionsSelectedStyle)
        
    
    def setAlarmState(self, obj):
        newState = AlarmState(obj.name)
        self.currentPreset.state = newState        
        self.configManager.saveSettings(self.alarmSettings)
        self.configureAlarmStateDisplay()
        
    def setTimeOfDay(self, obj):
        newTOD = TimeOfDay(obj.name)
        self.currentPreset.setTimeOfDayType(newTOD)
        self.configManager.saveSettings(self.alarmSettings)
        self.updateTimeDisplay()
        self.configureAlarmStateDisplay()
        
        
    scanInterval = 0.5
    scanDirection = Direction.NONE
    scanTarget= ScanTarget.NONE
    scanTimer = None
    
    
    def changeHour(self, obj):
        self.scanDirection = Direction(obj.name)
        self.scanTarget = ScanTarget.HOUR
        self.startTimer()
                
    def changeMinute(self, obj):
        self.scanDirection = Direction(obj.name)
        self.scanTarget = ScanTarget.MINUTE
        self.startTimer()
        
    def changeReleased(self, obj):
        self.stopTimer()
        
    def startTimer(self):
        self.scanInterval = 0.5
        self.processTimer()
        
    def processTimer(self):
        if(self.scanDirection != Direction.NONE):            
            self.changeTime()
            th =  Timer(self.scanInterval,self.processTimer) 
            self.scanInterval = self.scanInterval / 1.5
            if(self.scanInterval < 0.05):
                self.scanInterval = 0.05;
            th.start()
            
    def changeTime(self):        
        if(self.scanTarget == ScanTarget.HOUR):
            self.currentPreset.changeHour(self.scanDirection)
        elif(self.scanTarget == ScanTarget.MINUTE):
            self.currentPreset.changeMinute(self.scanDirection)
        self.updateTimeDisplay()        
            
    def stopTimer(self):        
        self.scanDirection = Direction.NONE
        self.scanTarget = ScanTarget.NONE        
        self.configureAlarmStateDisplay()
        self.configManager.saveSettings(self.alarmSettings)

    def __init__(self, parent):
        super(AlarmWidget, self).__init__(parent)
        self.resize(320, 210)
        
        
        self.initializeAlarmPresets()
        for i in range(len(self.alarmSettings)):
            setting = self.alarmSettings[i]
            print(setting.getDisplayTimeString())
        
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
        self.label.setGeometry(QtCore.QRect(85, 90, 21, 61))
        self.label.setFont(timeFont)
        self.label.setStyleSheet("color: #fff")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.lblHour = QtGui.QLabel(self)
        self.lblHour.setGeometry(QtCore.QRect(5, 90, 81, 61))
        self.lblHour.setFont(timeFont)
        self.lblHour.setStyleSheet("color: #fff")
        self.lblHour.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        
        self.lblMinute = QtGui.QLabel(self)
        self.lblMinute.setGeometry(QtCore.QRect(105, 90, 81, 61))
        self.lblMinute.setFont(timeFont)
        self.lblMinute.setStyleSheet("color: #fff")
        self.lblMinute.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        
        
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(190, 90, 41, 61))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        
        self.lblAM = QtGui.QLabel("AM", self.verticalLayoutWidget)             
        self.lblAM.name = TimeOfDay.AM        
        clickableSender(self.lblAM).connect(self.setTimeOfDay)
        self.lblAM.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.lblAM)
        self.lblPM = QtGui.QLabel("PM", self.verticalLayoutWidget)
        self.lblPM.name = TimeOfDay.PM
        clickableSender(self.lblPM).connect(self.setTimeOfDay)
        self.lblPM.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.lblPM)        
        
        
        self.btnHourUp = QSvgWidget("icons/triangle-up.svg", self)
        self.btnHourUp.name = Direction.UP        
        pressableSender(self.btnHourUp).connect(self.changeHour)
        clickableSender(self.btnHourUp).connect(self.changeReleased) 
        self.btnHourUp.setGeometry(QtCore.QRect(20, 60, 61, 31))           
        
        self.btnHourDown = QSvgWidget("icons/triangle-down.svg", self)
        self.btnHourDown.name = Direction.DOWN
        pressableSender(self.btnHourDown).connect(self.changeHour)
        clickableSender(self.btnHourDown).connect(self.changeReleased) 
        self.btnHourDown.setGeometry(QtCore.QRect(20, 155, 61, 31))
        
        self.btnMinuteUp = QSvgWidget("icons/triangle-up.svg", self)
        self.btnMinuteUp.name = Direction.UP
        pressableSender(self.btnMinuteUp).connect(self.changeMinute) 
        clickableSender(self.btnMinuteUp).connect(self.changeReleased) 
        self.btnMinuteUp.setGeometry(QtCore.QRect(110, 60, 61, 31))
        
        self.btnMinuteDown = QSvgWidget("icons/triangle-down.svg", self)
        self.btnMinuteDown.name = Direction.DOWN
        pressableSender(self.btnMinuteDown).connect(self.changeMinute) 
        clickableSender(self.btnMinuteDown).connect(self.changeReleased) 
        self.btnMinuteDown.setGeometry(QtCore.QRect(110, 155, 61, 31))
        
        self.verticalLayoutWidget_2 = QtGui.QWidget(self)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(235, 50, 80, 151))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        
        
        self.lblOnRadio = QtGui.QLabel("RADIO", self.verticalLayoutWidget_2)  
        self.lblOnRadio.name = AlarmState.RADIO
        clickableSender(self.lblOnRadio).connect(self.setAlarmState)
        self.lblOnRadio.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.lblOnRadio)
        
        if(self.pandoraEnabled):
            self.lblOnPandora = QtGui.QLabel("PANDORA", self.verticalLayoutWidget_2)  
            self.lblOnPandora.name = AlarmState.PANDORA
            clickableSender(self.lblOnPandora).connect(self.setAlarmState)
            self.lblOnPandora.setAlignment(QtCore.Qt.AlignCenter)
            self.verticalLayout_2.addWidget(self.lblOnPandora)
        
        
        
        
        self.lblOnBuzzer = QtGui.QLabel("BUZZ", self.verticalLayoutWidget_2)  
        self.lblOnBuzzer.name = AlarmState.BUZZ
        clickableSender(self.lblOnBuzzer).connect(self.setAlarmState)
        self.lblOnBuzzer.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.lblOnBuzzer)
        
        self.lblOff = QtGui.QLabel("OFF", self.verticalLayoutWidget_2)        
        self.lblOff.name = AlarmState.OFF
        clickableSender(self.lblOff).connect(self.setAlarmState)
        self.lblOff.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.lblOff)
        
        
        
        self.setCurrentPreset(0)
        
        
        
        QtCore.QMetaObject.connectSlotsByName(self)       
        
        
    
       
       

    
        