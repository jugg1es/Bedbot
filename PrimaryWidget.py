
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
from Widgets.InternetRadioWidget import *
from Widgets.PlaybackWidget import PlaybackType
from perpetualTimer import perpetualTimer
from Objects.alarmSetting import *
from Controllers.Radio import *
from Controllers.ButtonManager import *
from Controllers.MotorManager import *
from Controllers.Buzz import *
from Controllers.Pandora import *
from Controllers.DigiSwitch import *
from Controllers.OLEDController import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget
import logging
from Controllers.ScreenManager import *
from Controllers.InternetRadioService import *


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
    
    shouldInitializeButtonsAndSensors = True
    
    currentWidget = None    
    clockUpdateTimer = None
    
    useOLED = True
    
    snoozeButtonOnStyle = "font-size:20px; background-color:yellow; border: 0px solid #fff; color:#000;"
    snoozeButtonStyle = "font-size:20px; background-color:#000; border: 0px solid #fff; color:#fff;"
    
    audioOnButtonPin = 5
    audioOffButtonPin = 6
    contextButtonPin = 12
    screenToggleButtonPin = 22
    buttonPowerPin = 27
    audioToggleOne = 4
    audioToggleTwo = 17
    currentWidgetIndex = 2
    
    pandoraEnabled = False
    
    isSoundOn = False
    
    buzzerPin = 16
    
    def __init__(self, parent):
        super(PrimaryWidget, self).__init__(parent)

        self.resize(320, 240)      
        
        if(self.useOLED):
            self.oled = OLEDController()
            
            
        self.internet_radio = InternetRadioService()
        self.connect(self.internet_radio, QtCore.SIGNAL('internetRadioPlay'), self.internetRadioOn)
        self.connect(self.internet_radio, QtCore.SIGNAL('internetRadioStop'), self.internetRadioOff)
        
        self.screen_manager = ScreenManager()
        self.screen_manager.initialize()
        
        self.buttonPowerSwitch = DigiSwitch(self.buttonPowerPin)
        
        self.menu_widget = MenuWidget(self)
        self.menu_widget.setGeometry(QtCore.QRect(0, 85, 320, 70))  
        self.menu_widget.setVisible(False)
        
        
        self.connect(self.menu_widget, QtCore.SIGNAL('showAlarm'), self.showAlarmWidget)
        self.connect(self.menu_widget, QtCore.SIGNAL('showPlayback'), self.showPlaybackWidget)
        self.connect(self.menu_widget, QtCore.SIGNAL('showClock'), self.showTimeWidget)
        '''
        self.menu_widget.showAlarm.connect(self.showAlarmWidget)
        self.menu_widget.showPlayback.connect(self.showPlaybackWidget)
        self.menu_widget.showClock.connect(self.showTimeWidget)
        '''
        
        
        
        self.showMenuButton = QtGui.QPushButton("MENU", self)        
        self.showMenuButton.setGeometry(QtCore.QRect(0, 210, 90, 30))
        self.showMenuButton.setStyleSheet("font-size:20px;border: 0px solid #fff; color:#fff;")    
        clickable(self.showMenuButton).connect(self.userShowMenuPressed)    
        #self.showMenuButton.clicked.connect(self.userShowMenuTouched)
        
        
        
        
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
        
        
        self.internet_radio_widget = InternetRadioWidget(self,self.internet_radio)
        self.internet_radio_widget.setGeometry(QtCore.QRect(0, 35, 320, 175)) 
        self.internet_radio_widget.setVisible(False)
        
        
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
        
        
        #self.buzzManager = Buzz(self.buzzerPin)
        
        #self.pandoraManager = Pandora()   
        #self.connect(self.pandoraManager, QtCore.SIGNAL('pandoraInitialized'), self.pandoraInitializedReceived)
        #self.connect(self.pandoraManager, QtCore.SIGNAL('pandoraSongChange'), self.pandoraSongChange)
        
                
        self.motorManager = MotorManager()
        self.connect(self.motorManager, QtCore.SIGNAL('turnScreenOn'), self.screenButtonOn)
        self.connect(self.motorManager, QtCore.SIGNAL('turnScreenOff'), self.screenButtonOff)
        self.motorManager.initialize()
        
        self.startClockTimer() 
        
        self.menuTimer = None
        self.clockDisplayTimer = None
        
        
        self.initializePhysicalButtons()

        self.updatePlayStatusDisplay()
        
        if(self.useOLED):
            self.oled.start()
            
            
        QtCore.QMetaObject.connectSlotsByName(self)    
    
    def userShowMenuPressed(self):
        self.hideAllWidgets()
        self.menu_widget.setVisible(True)
        self.menuTimer = QTimer()
        self.menuTimer.timeout.connect(self.autoHideMenu)
        self.menuTimer.start(10000)
    
    def killMenuTimer(self):
        if(self.menuTimer != None and self.menuTimer.isActive()):            
            self.menuTimer.stop()
        
    def autoHideMenu(self):
        self.menuTimer.stop()
        self.showTimeWidget()   
    
    def gotoNextMenuItem(self):
        self.currentWidgetIndex += 1
        
        if(self.currentWidgetIndex > 2):
            self.currentWidgetIndex = 0
        self.showCurrentMenuItem()
            
    def showCurrentMenuItem(self):
        self.hideAllWidgets()
        self.menu_widget.setVisible(True)
        if(self.currentWidgetIndex == 0):
            self.menu_widget.alarmButtonClicked()
        elif(self.currentWidgetIndex == 1):
            self.menu_widget.playbackButtonClicked()
        elif(self.currentWidgetIndex == 2):
            self.menu_widget.clockButtonClicked()
            
    def internetRadioOn(self):
        print("interet radio turned on")
        self.isSoundOn = True
        self.updatePlayStatusDisplay()
        
    def internetRadioOff(self):
        print("interet radio turned off")
        self.isSoundOn = False
        self.updatePlayStatusDisplay()
        
        
    def screenButtonOn(self):
        print("turn screen on")
        self.buttonPowerSwitch.turnOn()
        self.screen_manager.turnOn()
        
    def screenButtonOff(self):
        print("turn screen off")
        self.buttonPowerSwitch.turnOff()
        self.screen_manager.turnOff()
        self.turnSoundOff()
        
    def turnSoundOff(self):
        
        self.isSoundOn = False
        if(self.radioManager.radioOn):
            self.radioManager.stopRadio()
        if(hasattr(self, "pandoraManager") == True):
            if(self.pandoraManager.pandoraOn):
                self.pandoraManager.stopPandora()
        if(self.internet_radio.isPlaying):
            self.internet_radio.stop()
            
        self.currentWidgetIndex = 2
        self.showCurrentMenuItem()
    
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
        logging.info('playbackTypeChanged')
        self.updatePlayStatusDisplay()
        self.showPlaybackWidget()
        
    def updatePlayStatusDisplay(self):
        self.audioOnIcon.setVisible(False)
        self.alarmOnIcon.setVisible(False)
        self.playStatus.setVisible(False)
        
        if(self.isSoundOn):            
            self.playStatus.setVisible(True)
            
            if(self.playback_widget.currentPlaybackType == PlaybackType.AUX):
                self.playStatus.setText("AUX")
            elif(self.playback_widget.currentPlaybackType == PlaybackType.PANDORA):
                self.playStatus.setText("PANDORA")
            elif(self.playback_widget.currentPlaybackType == PlaybackType.RADIO):
                self.playStatus.setText("RADIO")
            elif(self.playback_widget.currentPlaybackType == PlaybackType.WWWSTREAM):
                self.playStatus.setText("STREAM")
            elif(self.playback_widget.currentPlaybackType == PlaybackType.NONE):
                self.playStatus.setText("")
                self.playStatus.setVisible(False)
        '''  
        if(self.isAlarmOn()):            
            self.playStatus.setStyleSheet("font-size:20px; border: 0px solid #fff; color:#ff0000;")
            self.alarmOnIcon.setVisible(True)
        else:
            self.playStatus.setStyleSheet("font-size:20px; border: 0px solid #fff; color:#faff00;")
            self.audioOnIcon.setVisible(True)
            '''
    
    def initializePhysicalButtons(self):
        if(self.shouldInitializeButtonsAndSensors):
            
            self.audioOnButton = ButtonManager(self.audioOnButtonPin)
            self.connect(self.audioOnButton, QtCore.SIGNAL('buttonPressed'), self.audioButtonOnPushed)
            
            self.audioOffButton = ButtonManager(self.audioOffButtonPin)
            self.connect(self.audioOffButton, QtCore.SIGNAL('buttonPressed'), self.audioButtonOffPressed)
            
            self.toggleScreenButton = ButtonManager(self.screenToggleButtonPin)
            self.connect(self.toggleScreenButton, QtCore.SIGNAL('buttonPressed'), self.toggleScreenButtonPushed)
            
            self.contextButton = ButtonManager(self.contextButtonPin)
            self.connect(self.contextButton, QtCore.SIGNAL('buttonPressed'), self.contextButtonTouched)        
        
    def startRadioReceived(self):
        #self.radioManager.startRadio()
        print("clicked")
        
    def stopRadioReceived(self):
        print("clicked")
        #self.radioManager.stopRadio()
        
    def radioFrequencyReceived(self, newFreq):
        self.radioManager.setFrequency(newFreq)
        
    def audioButtonOnPushed(self):
        logging.info('audioButtonOnPushed')
        print("radio ON pushed")       
        self.showPlaybackWidget()
        if(self.playback_widget.currentPlaybackType == PlaybackType.RADIO):
            self.radioManager.startRadio()
       
        
    def audioButtonOffPressed(self):
        self.userOffTouched()
        
    def toggleScreenButtonPushed(self):  
        print("screen toggled")
        self.motorManager.positionToggled()
    
    def startClockTimer(self):
        self.clockUpdateTimer = perpetualTimer(1, self.processClockTime)
        self.clockUpdateTimer.start()
        
    def stopClockTimer(self):
        self.clockUpdateTimer.cancel()        
        
    def showPlaybackWidget(self):
        self.currentWidgetIndex = 1
        self.hideAllWidgets()
        logging.info('showPlaybackWidget')
        self.currentWidget = self.playback_widget
        
        self.radio_widget.setVisible(False)
        self.pandora_widget.setVisible(False)
        if(self.playback_widget.currentPlaybackType == PlaybackType.NONE or self.playback_widget.currentPlaybackType == PlaybackType.RADIO):
            self.radio_widget.setVisible(True)
        elif(self.playback_widget.currentPlaybackType == PlaybackType.PANDORA):
            self.pandora_widget.setVisible(True)
        elif(self.playback_widget.currentPlaybackType == PlaybackType.AUX):
            self.aux_widget.setVisible(True)
        elif(self.playback_widget.currentPlaybackType == PlaybackType.WWWSTREAM):
            self.internet_radio_widget.setVisible(True)
            
        self.playback_widget.setVisible(True)
        
    def showAlarmWidget(self):
        self.currentWidgetIndex = 0
        self.hideAllWidgets()
        self.currentWidget = self.alarm_widget
        self.alarm_widget.setVisible(True)
            
    def showTimeWidget(self):
        self.currentWidgetIndex = 2
        self.hideAllWidgets()        
        self.currentWidget = self.time_widget
        self.time_widget.setVisible(True) 
                    
    def hideAllWidgets(self):
        self.killMenuTimer()
        self.menu_widget.setVisible(False)
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
            
        if(hasattr(self, "internet_radio_widget") == True):
            self.internet_radio_widget.setVisible(False)
            
  
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
        
        logging.info('playStatusTouched')
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
        
    def contextButtonTouched(self):
        
        if(self.isAlarmOn()):
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
        else:
            self.gotoNextMenuItem()
        
            
    def isAlarmOn(self):
        if(len(self.alarmsCurrentlyOn) > 0):
            return True
        return False

        
    def doClose(self):
        if(self.useOLED):
            self.oled.cancel()
        
        try:
            self.internet_radio.dispose()
        except Exception:
            print("Problem disposing of internet radio service button")
            
            
        #self.pandoraManager.dispose()
        try:
            self.buttonPowerSwitch.dispose()
        except Exception:
            print("Problem disposing of buttonPowerSwitch button")
        
        try:
            self.audioOnButton.dispose()
        except Exception:
            print("Problem disposing of radioon button")
            
        try:
            self.audioOffButton.dispose()
        except Exception:
            print("Problem disposing of radiooff button")
            
        try:
            self.contextButton.dispose()
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
        try:
            self.stopClockTimer()
        except Exception:
            print("Problem disposing of clock timer ")
            
        try:
            self.buzzManager.stopBuzzer()
        except Exception:
            print("Problem disposing of buzzManager ")
        
        try:
            self.radioManager.stopRadio()
        except Exception:
            print("Problem disposing of buzzManager ")
        
        
        
