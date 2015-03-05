
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from TimeWidget import TimeWidget
from MenuWidget import MenuWidget
from clickable import *
from RadioWidget import RadioWidget
from AlarmWidget import AlarmWidget
from perpetualTimer import perpetualTimer
from alarmSetting import *
from Radio import *
from Buzz import *
from ButtonManager import *
from MotorManager import *
from PlaybackWidget import *
from PandoraWidget import *
from Pandora import *

class PrimaryWidget(QtGui.QWidget):
    
    currentWidget = None    
    clockUpdateTimer = None
    
    snoozeButtonOnStyle = "font-size:20px; background-color:yellow; border: 0px solid #fff; color:#000;"
    snoozeButtonStyle = "font-size:20px; background-color:#000; border: 0px solid #fff; color:#fff;"
    
    radioONButtonPin = 20
    radioOFFButtonPin = 21
    snoozeButtonPin = 22
    screenToggleButtonPin = 23
    
    def __init__(self, parent):
        super(PrimaryWidget, self).__init__(parent)
        self.resize(320, 240)      
        
        self.menu_widget = MenuWidget(self)
        self.menu_widget .setGeometry(QtCore.QRect(0, 85, 320, 70))  
        self.menu_widget.setVisible(False)
        
        self.menu_widget.showAlarm.connect(self.showAlarmWidget)
        self.menu_widget.showPlayback.connect(self.showPlaybackWidget)
        self.menu_widget.showClock.connect(self.showTimeWidget)
        
        
        self.showMenuButton = QtGui.QPushButton("MENU", self)        
        self.showMenuButton.setGeometry(QtCore.QRect(0, 210, 90, 30))
        self.showMenuButton.setStyleSheet("font-size:20px;border: 0px solid #fff; color:#fff;")
        self.showMenuButton.clicked.connect(self.userShowMenuTouched)
        
        
        self.offButton = QtGui.QPushButton("OFF", self)        
        self.offButton.setGeometry(QtCore.QRect(115, 210, 90, 30))
        self.offButton.setVisible(False)
        self.offButton.setStyleSheet("font-size:20px; background-color:red; border: 0px solid #fff; color:#000;")
        self.offButton.clicked.connect(self.userOffTouched)
        
        
        self.snoozeButton = QtGui.QPushButton("SNOOZE", self)        
        self.snoozeButton.setGeometry(QtCore.QRect(230, 210, 90, 30))
        self.snoozeButton.setVisible(False)
        self.snoozeButton.setStyleSheet(self.snoozeButtonOnStyle)
        self.snoozeButton.clicked.connect(self.userSnoozeTouched)
        
        self.playback_widget = PlaybackWidget(self)
        self.playback_widget.setGeometry(QtCore.QRect(0, 0, 320, 35)) 
        self.playback_widget.setVisible(False)
        self.connect(self.playback_widget, QtCore.SIGNAL('changePlayback'), self.playbackTypeChanged)
        
        self.radio_widget = RadioWidget(self)       
        self.radio_widget.setGeometry(QtCore.QRect(0, 35, 320, 175)) 
        self.radio_widget.setVisible(False)
        #self.connect(self.radio_widget, QtCore.SIGNAL('startRadio'), self.startRadioReceived)
        #self.connect(self.radio_widget, QtCore.SIGNAL('stopRadio'), self.stopRadioReceived)
        self.connect(self.radio_widget, QtCore.SIGNAL('changeFrequency'), self.radioFrequencyReceived)
        
        self.pandora_widget = PandoraWidget(self)       
        self.pandora_widget.setGeometry(QtCore.QRect(0, 35, 320, 175)) 
        self.pandora_widget.setVisible(False)
        
        self.connect(self.pandora_widget, QtCore.SIGNAL('setPandoraStation'), self.pandoraStationReceived)
        self.connect(self.pandora_widget, QtCore.SIGNAL('pandoraStop'), self.pandoraStopReceived)
        #self.connect(self.radio_widget, QtCore.SIGNAL('startRadio'), self.startRadioReceived)
        #self.connect(self.radio_widget, QtCore.SIGNAL('stopRadio'), self.stopRadioReceived)
        #self.connect(self.radio_widget, QtCore.SIGNAL('changeFrequency'), self.radioFrequencyReceived)
        
        
        
        self.time_widget = TimeWidget(self)       
        self.time_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))          
        self.time_widget.setVisible(False)   
        
        self.alarm_widget = AlarmWidget(self)       
        self.alarm_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))   
        self.alarm_widget.setVisible(False)    
        
        self.radioManager = Radio()
        self.buzzManager = Buzz(13)
        self.pandoraManager = Pandora()   
        self.connect(self.pandoraManager, QtCore.SIGNAL('pandoraInitialized'), self.pandoraInitializedReceived)
        self.connect(self.pandoraManager, QtCore.SIGNAL('pandoraSongChange'), self.pandoraSongChange)
        
                
        self.motorManager = MotorManager(13,19)
        
        self.startClockTimer() 
        
        self.menuTimer = None
        self.clockDisplayTimer = None
        self.connect(self, QtCore.SIGNAL('updateAlarmButtons'), self.updateAlarmButtonState)
        
        
        #self.initializePhysicalButtons()
        
        self.toggleScreenButton = ButtonManager(21)
        self.connect(self.toggleScreenButton, QtCore.SIGNAL('buttonPressed'), self.toggleScreenButtonPushed)
        
        QtCore.QMetaObject.connectSlotsByName(self)    
    
    
    def pandoraSongChange(self, artist,song):
        if(self.pandoraManager.isInitialized()):
            self.pandora_widget.setSongDisplay(artist, song)
        
    def pandoraInitializedReceived(self):
        if(self.pandoraManager.isInitialized()):
            self.pandora_widget.setStationList(self.pandoraManager.stationList)
        
    def pandoraStopReceived(self):
        self.pandoraManager.stopPandora()
        
        
    def pandoraStationReceived(self, name):
        self.pandoraManager.setStation(name)
        
        
    def playbackTypeChanged(self, newType):
        self.showPlaybackWidget()
    
    def initializePhysicalButtons(self):
        self.radioOnButton = ButtonManager(self.radioONButtonPin)
        self.connect(self.radioOnButton, QtCore.SIGNAL('buttonPressed'), self.radioButtonONPushed)
        
        self.radioOffButton = ButtonManager(self.radioOFFButtonPin)
        self.connect(self.radioOffButton, QtCore.SIGNAL('buttonPressed'), self.radioButtonOFFPushed)
        
        self.alarmSnoozeButton = ButtonManager(self.snoozeButtonPin)
        self.connect(self.alarmSnoozeButton, QtCore.SIGNAL('buttonPressed'), self.snoozeButtonPushed)        
        
        self.toggleScreenButton = ButtonManager(self.screenToggleButtonPin)
        self.connect(self.toggleScreenButton, QtCore.SIGNAL('buttonPressed'), self.toggleScreenButtonPushed)
        
        
    def startRadioReceived(self):
        #self.radioManager.startRadio()
        print("clicked")
        
    def stopRadioReceived(self):
        print("clicked")
        #self.radioManager.stopRadio()
        
    def radioFrequencyReceived(self, newFreq):
        self.radioManager.setFrequency(newFreq)
        
    def radioButtonONPushed(self):
        print("radio ON pushed")    
        
        print("clicked")
        #self.radioManager.startRadio()
        
    def radioButtonOFFPushed(self):
        print("radio OFF pushed")  
        self.radioManager.stopRadio()  
        
    def snoozeButtonPushed(self):
        print("SNOOZE pushed")  
        self.userSnoozeTouched()
        
    def toggleScreenButtonPushed(self):
        print("SCREEN TOGGLED")          
        self.motorManager.positionToggled()
    
    def startClockTimer(self):
        self.clockUpdateTimer = perpetualTimer(1, self.processClockTime)
        self.clockUpdateTimer.start()
        
    def stopClockTimer(self):
        self.clockUpdateTimer.cancel()        
        
    def showPlaybackWidget(self):
        self.hideAllWidgets()
        
        self.currentWidget = self.playback_widget
        
        self.radio_widget.setVisible(False)
        self.pandora_widget.setVisible(False)
        if(self.playback_widget.currentPlaybackType == PlaybackType.RADIO):
            self.radio_widget.setVisible(True)
        elif(self.playback_widget.currentPlaybackType == PlaybackType.PANDORA):
            self.pandora_widget.setVisible(True)
            
        self.playback_widget.setVisible(True)
        
    def showAlarmWidget(self):
        self.hideAllWidgets()
        self.currentWidget = self.alarm_widget
        self.alarm_widget.setVisible(True)
            
    def showTimeWidget(self):
        self.hideAllWidgets()        
        self.currentWidget = self.time_widget
        self.time_widget.setVisible(True) 
                    
    def hideAllWidgets(self):
        
        self.autoCloseMenu()
        if(hasattr(self, "time_widget") == True):
            self.time_widget.setVisible(False)
            
        if(hasattr(self, "radio_widget") == True):
            self.radio_widget.setVisible(False)
            
        if(hasattr(self, "playback_widget") == True):
            self.playback_widget.setVisible(False)
            
        if(hasattr(self, "pandora_widget") == True):
            self.pandora_widget.setVisible(False)
            
        if(hasattr(self, "alarm_widget") == True):
            self.alarm_widget.setVisible(False)
            
  
    def autoSwitchToClock(self):
        self.showTimeWidget()
        
    def processClockTime(self):
        self.time_widget.updateCurrentTime()   
        activeAlarms = self.alarm_widget.checkAlarms()
        if(len(activeAlarms) > 0):
            for x in range(len(activeAlarms)):
                alarm = activeAlarms[x]
                if(alarm not in self.alarmsTurnedOff  and alarm not in self.alarmsCurrentlyOn and alarm not in self.alarmsSnoozing):
                    self.startAlarm(alarm)
        else:
            self.alarmsTurnedOff = []
        
        if(len(self.alarmsCurrentlyOn) > 0):
            for x in range(len(self.alarmsCurrentlyOn)):
                alarm = self.alarmsCurrentlyOn[x]
                timeSince = alarm.getTimeSinceStart()
                if(timeSince != None):
                    if(timeSince.total_seconds() >= (self.alarmLengthMin * 60)):
                        self.turnAlarmOff(alarm)
                        
        if(len(self.alarmsSnoozing) > 0):
            for x in range(len(self.alarmsSnoozing)):
                alarm = self.alarmsSnoozing[x]
                timeSince = alarm.getTimeSinceSnooze()
                if(timeSince != None):
                    if(timeSince.total_seconds() > (self.alarmSnoozeTime * 60)):
                        self.startAlarm(alarm)
            
            
    alarmSnoozeTime = 15   
    alarmsTurnedOff = []
    alarmsSnoozing = []
    alarmsCurrentlyOn = []
    alarmLengthMin = 60
    
    
    def updateAlarmButtonState(self):
        if(len(self.alarmsCurrentlyOn) > 0):
            self.snoozeButton.setVisible(True)   
            self.snoozeButton.setStyleSheet(self.snoozeButtonOnStyle)  
            self.offButton.setVisible(True)
        elif(len(self.alarmsSnoozing) > 0):
            self.snoozeButton.setStyleSheet(self.snoozeButtonStyle)  
            self.snoozeButton.setVisible(True)        
            self.offButton.setVisible(True)
        else:
            self.snoozeButton.setVisible(False)        
            self.offButton.setVisible(False)
        
    def startAlarm(self, alarm):        
        self.alarmsCurrentlyOn.append(alarm)     
        
        if(alarm in self.alarmsSnoozing):
            self.alarmsSnoozing.remove(alarm)
                
        if(alarm.state == AlarmState.BUZZ):
            self.buzzManager.startBuzzer()
        elif(alarm.state == AlarmState.RADIO):
            self.radioManager.startRadio()
            
        self.emit(QtCore.SIGNAL('updateAlarmButtons'))       
        alarm.setStartTime(datetime.datetime.now())
        
        
            
    def userOffTouched(self):
        for x in range(len(self.alarmsCurrentlyOn)):
            alarm = self.alarmsCurrentlyOn[x]
            self.turnAlarmOff(alarm)
        for x in range(len(self.alarmsSnoozing)):
            alarm = self.alarmsSnoozing[x]
            self.turnAlarmOff(alarm)
        
    def turnAlarmOff(self, alarm):
        if(alarm.state == AlarmState.BUZZ):
            self.buzzManager.stopBuzzer()
        elif(alarm.state == AlarmState.RADIO):
            self.radioManager.stopRadio()
        
        if(alarm in self.alarmsCurrentlyOn ):
            self.alarmsCurrentlyOn.remove(alarm)
        if(alarm in self.alarmsSnoozing):
            self.alarmsSnoozing.remove(alarm)
        alarm.setStartTime(None)
        alarm.setSnoozeTime(None)
        self.alarmsTurnedOff.append(alarm)
        self.emit(QtCore.SIGNAL('updateAlarmButtons'))       
        
        
    def userSnoozeTouched(self):
        for x in range(len(self.alarmsCurrentlyOn)):
            alarm = self.alarmsCurrentlyOn[x]
            if(alarm.state == AlarmState.BUZZ):
                self.buzzManager.stopBuzzer()
            elif(alarm.state == AlarmState.RADIO):
                self.radioManager.stopRadio()
            self.alarmsSnoozing.append(alarm)        
            alarm.setStartTime(None)        
            alarm.setSnoozeTime(datetime.datetime.now())
        
        self.alarmsCurrentlyOn = []
        self.emit(QtCore.SIGNAL('updateAlarmButtons'))       
            
        
    def userShowMenuTouched(self):
        
        if(self.menu_widget.isVisible()):
            self.menu_widget.setVisible(False)
            self.currentWidget.setVisible(True)
        else:
            if(self.menuTimer == None):
                self.menuTimer = QTimer()
                #self.menuTimer.timeout.connect(self.autoCloseMenu)
                #self.menuTimer.start(5000)
           
            self.hideAllWidgets()
            self.menu_widget.setVisible(True)
    
    def autoCloseMenu(self):
        self.menu_widget.setVisible(False)  
        
        
    def doClose(self):
        self.pandoraManager.dispose()
        try:
            self.radioOnButton.dispose()
        except Exception:
            print("Problem disposing of radioon button")
            
        try:
            self.radioOffButton.dispose()
        except Exception:
            print("Problem disposing of radiooff button")
        try:
            self.snoozeButton.dispose()
        except Exception:
            print("Problem disposing of snooze button")
            
        try:
            self.toggleScreenButton.dispose()
        except Exception:
            print("Problem disposing of togglescreen")
            
            
        try:
            self.motorManager.dispose()
        except Exception:
            print("Problem disposing of motor manager")
            
        self.stopClockTimer()
        self.buzzManager.stopBuzzer()
        self.radioManager.stopRadio()
        