
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from clickable import *
from Widgets.MenuWidget import *
from Widgets.PlaybackWidget import *
from Widgets.TimeWidget import *
from Widgets.AlarmWidget import *
from Widgets.RadioWidget import *
from Widgets.PandoraWidget import *
from Widgets.AuxWidget import *
from Widgets.PlaybackWidget import PlaybackType
from perpetualTimer import perpetualTimer
from alarmSetting import *
from Controllers.Radio import *
from Controllers.ButtonManager import *
from Controllers.MotorManager import *
from Controllers.Buzz import *
from Controllers.Pandora import *
from Controllers.DigiSwitch import *
from Controllers.OLEDController import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget


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

class PrimaryWidget(QtGui.QWidget):
    
    shouldInitializeButtonsAndSensors = False
    
    currentWidget = None    
    clockUpdateTimer = None
    
    snoozeButtonOnStyle = "font-size:20px; background-color:yellow; border: 0px solid #fff; color:#000;"
    snoozeButtonStyle = "font-size:20px; background-color:#000; border: 0px solid #fff; color:#fff;"
    
    radioONButtonPin = 5
    radioOFFButtonPin = 6
    snoozeButtonPin = 12
    screenToggleButtonPin = 22
    amplifierControlPin = 27
    audioToggleOne = 4
    audioToggleTwo = 17
    screenPowerPin = 27
    
    
    buzzerPin = 16
    
    def __init__(self, parent):
        super(PrimaryWidget, self).__init__(parent)
        self.resize(320, 240)      
        
        self.oled = OLEDController()
        
        self.screenPower = DigiSwitch(self.screenPowerPin)
        self.amplifier = DigiSwitch(self.amplifierControlPin)
        
        self.menu_widget = MenuWidget(self)
        self.menu_widget.setGeometry(QtCore.QRect(0, 85, 320, 70))  
        self.menu_widget.setVisible(False)
        
        self.menu_widget.showAlarm.connect(self.showAlarmWidget)
        self.menu_widget.showPlayback.connect(self.showPlaybackWidget)
        self.menu_widget.showClock.connect(self.showTimeWidget)
        
        
        self.showMenuButton = QtGui.QPushButton("MENU", self)        
        self.showMenuButton.setGeometry(QtCore.QRect(0, 210, 90, 30))
        self.showMenuButton.setStyleSheet("font-size:20px;border: 0px solid #fff; color:#fff;")
        self.showMenuButton.clicked.connect(self.userShowMenuTouched)
        
        
        
        
        self.playStatus = QtGui.QPushButton("", self)        
        self.playStatus.setGeometry(QtCore.QRect(115, 210, 90, 30))
        self.playStatus.setVisible(False)
        self.playStatus.clicked.connect(self.playStatusTouched)
        
        self.audioOnIcon = QSvgWidget("icons/volume-low.svg", self)
        self.audioOnIcon.setGeometry(QtCore.QRect(260, 210, 25, 25))        
        self.audioOnIcon.setVisible(False)
        
        self.alarmOnIcon = QSvgWidget("icons/bellSnooze.svg", self)
        self.alarmOnIcon.setGeometry(QtCore.QRect(260, 210, 25, 25))        
        self.alarmOnIcon.setVisible(False)
        
        
        
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
        
        self.aux_widget = AuxWidget(self)
        self.aux_widget.setGeometry(QtCore.QRect(0, 35, 320, 175)) 
        self.aux_widget.setVisible(False)
        
        
        self.time_widget = TimeWidget(self)       
        self.time_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))          
        self.time_widget.setVisible(False)   
        
        self.alarm_widget = AlarmWidget(self)       
        self.alarm_widget.setGeometry(QtCore.QRect(0, 0, 320, 210))   
        self.alarm_widget.setVisible(False)    
        
        self.radioManager = Radio()
        self.buzzManager = Buzz(self.buzzerPin)
        self.pandoraManager = Pandora()   
        self.connect(self.pandoraManager, QtCore.SIGNAL('pandoraInitialized'), self.pandoraInitializedReceived)
        self.connect(self.pandoraManager, QtCore.SIGNAL('pandoraSongChange'), self.pandoraSongChange)
        
                
        self.motorManager = MotorManager()
        self.connect(self.motorManager, QtCore.SIGNAL('turnScreenOn'), self.turnScreenOn)
        self.connect(self.motorManager, QtCore.SIGNAL('turnScreenOff'), self.turnScreenOff)
        
        self.startClockTimer() 
        
        self.menuTimer = None
        self.clockDisplayTimer = None
        
        
        self.initializePhysicalButtons()

        self.updatePlayStatusDisplay()
        
        self.oled.start()
        QtCore.QMetaObject.connectSlotsByName(self)    
    
    
    
    def turnScreenOn(self):
        self.screenPower.turnOn()
        
    def turnScreenOff(self):
        self.screenPower.turnOff()
        
    def turnSoundOn(self):
        self.amplifier.turnOn()
        
    def turnSoundOff(self):
        if(self.radioManager.radioOn):
            self.radioManager.stopRadio()
        if(self.pandoraManager.pandoraOn):
            self.pandoraManager.stopPandora()
            
        self.amplifier.turnOff()
    
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
        self.updatePlayStatusDisplay()
        self.showPlaybackWidget()
        
    def updatePlayStatusDisplay(self):
        self.audioOnIcon.setVisible(False)
        self.alarmOnIcon.setVisible(False)
        self.playStatus.setVisible(False)
        
        if(self.amplifier.isPowerOn):   
            self.playStatus.setVisible(True)
            if(self.playback_widget.currentPlaybackType == PlaybackType.AUX):
                self.playStatus.setText("AUX")
            elif(self.playback_widget.currentPlaybackType == PlaybackType.PANDORA):
                self.playStatus.setText("PANDORA")
            elif(self.playback_widget.currentPlaybackType == PlaybackType.RADIO):
                self.playStatus.setText("RADIO")
                
            if(self.isAlarmOn()):            
                self.playStatus.setStyleSheet("font-size:20px; border: 0px solid #fff; color:#ff0000;")
                self.alarmOnIcon.setVisible(True)
            else:
                self.playStatus.setStyleSheet("font-size:20px; border: 0px solid #fff; color:#faff00;")
                self.audioOnIcon.setVisible(True)
    
    def initializePhysicalButtons(self):
        if(self.shouldInitializeButtonsAndSensors):
            self.radioOnButton = ButtonManager(self.radioONButtonPin)
            self.connect(self.radioOnButton, QtCore.SIGNAL('buttonPressed'), self.radioButtonONPushed)
            
            self.radioOffButton = ButtonManager(self.radioOFFButtonPin)
            self.connect(self.radioOffButton, QtCore.SIGNAL('buttonPressed'), self.radioButtonOFFPushed)
            
            self.alarmSnoozeButton = ButtonManager(self.snoozeButtonPin)
            self.connect(self.alarmSnoozeButton, QtCore.SIGNAL('buttonPressed'), self.userSnoozeTouched)        
            
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
        self.showPlaybackWidget()
        self.turnSoundOn()
        if(self.playback_widget.currentPlaybackType == PlaybackType.RADIO):
            self.radioManager.startRadio()
       
        
    def radioButtonOFFPushed(self):
        self.userOffTouched()
        
    def toggleScreenButtonPushed(self):  
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
        elif(self.playback_widget.currentPlaybackType == PlaybackType.AUX):
            self.aux_widget.setVisible(True)
            
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
            
        if(hasattr(self, "aux_widget") == True):
            self.aux_widget.setVisible(False)
            
  
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
    
            
    def startAlarm(self, alarm):        
        self.alarmsCurrentlyOn.append(alarm)     
        
        if(alarm in self.alarmsSnoozing):
            self.alarmsSnoozing.remove(alarm)
                
        if(alarm.state == AlarmState.BUZZ):
            self.buzzManager.startBuzzer()
        elif(alarm.state == AlarmState.RADIO):
            self.radioManager.startRadio()
               
        alarm.setStartTime(datetime.datetime.now())
        
    def playStatusTouched(self):
        self.showPlaybackWidget()
            
    def userOffTouched(self):
        for x in range(len(self.alarmsCurrentlyOn)):
            alarm = self.alarmsCurrentlyOn[x]
            self.turnAlarmOff(alarm)
        for x in range(len(self.alarmsSnoozing)):
            alarm = self.alarmsSnoozing[x]
            self.turnAlarmOff(alarm)        
        self.turnSoundOff()
        
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
        self.turnSoundOff()  
            
    def isAlarmOn(self):
        if(len(self.alarmsCurrentlyOn) > 0):
            return True
        return False
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
        self.oled.cancel()
        self.screenPower.dispose()
        self.pandoraManager.dispose()
        self.amplifier.dispose()
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
        
