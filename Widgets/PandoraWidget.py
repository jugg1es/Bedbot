
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


class PandoraWidget(QtGui.QWidget):
    
    
    buttonDefaultStyle = "border: 2px solid #000;"
    buttonPressedStyle = "border: 2px solid #fff;"
    
    selectedStation = None
    
    stationsDisplayed = None
    
    stationListingStyle = "font-size:12pt;background-color: #000;color:#fff;padding:2px;"
    stationSelectedListingStyle = "font-size:12pt;background-color: #fff; color:#000;padding:2px;"
    
    
    stations = []
    stationList = None
    
    def __init__(self, parent):
        super(PandoraWidget, self).__init__(parent)
        self.resize(320, 175)
        
        font = QtGui.QFont()
        font.setPointSize(15)
        
        self.lblChannelDisplay = QtGui.QLabel(self)
        self.lblChannelDisplay.setGeometry(QtCore.QRect(0, 10, 320, 30))
        #self.lblChannelDisplay.setAlignment(QtCore.Qt.AlignHCenter )
        self.lblChannelDisplay.setStyleSheet('color: #fff')
        self.lblChannelDisplay.setWordWrap(True)
        self.lblChannelDisplay.setFont(font)       
        self.lblChannelDisplay.setText("Tap to Set Channel")
        clickable(self.lblChannelDisplay).connect(self.toggleStationDisplay)
        
        
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lblArtistSongDisplay = QtGui.QLabel(self)
        self.lblArtistSongDisplay.setGeometry(QtCore.QRect(0, 40, 320, 50))
        #self.lblChannelDisplay.setAlignment(QtCore.Qt.AlignHCenter )
        self.lblArtistSongDisplay.setStyleSheet('color: #fff')
        self.lblArtistSongDisplay.setWordWrap(True)
        self.lblArtistSongDisplay.setFont(font)   
        
        
        
        self.btnStop = QSvgWidget("icons/stop.svg", self)
        pressableSender(self.btnStop).connect(self.stopPressed) 
        self.btnStop.setGeometry(QtCore.QRect(20, 120, 35, 35))      
        
        
        
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 320, 160))
        self.verticalLayoutWidget.setAutoFillBackground(True)
        p = self.verticalLayoutWidget.palette()
        p.setColor(self.verticalLayoutWidget.backgroundRole(), Qt.black)
        self.verticalLayoutWidget.setPalette(p)
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
            
        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidget(self.verticalLayoutWidget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(160)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.scroll)
        
        #self.verticalLayoutWidget.setVisible(False)
       
        self.toggleStationDisplay()
       
       
        QtCore.QMetaObject.connectSlotsByName(self)       
        
    def stopPressed(self):
        self.emit(QtCore.SIGNAL('pandoraStop'))  
        
    def setSongDisplay(self, artistName, songName):
        self.lblArtistSongDisplay.setText(artistName + " - " + songName)
        
    def setStationList(self, stationList):
        self.stationList = stationList
        self.fillStationList()
        
    def fillStationList(self):
        if(self.stationList != None and len(self.stations) == 0):
            for i in range(0, len(self.stationList)):
                stationName = self.stationList[i]
                station = QtGui.QLabel(stationName)             
                station.setStyleSheet(self.stationListingStyle)
                station.name = i
                self.verticalLayout.addWidget(station)
                pressableSender(station).connect(self.setStation)
                self.stations.append(station)
                
        
    def toggleStationDisplay(self):
        if(self.stationsDisplayed == None):
            self.stationsDisplayed = False
        else:
            self.stationsDisplayed = not self.stationsDisplayed
            
        self.scroll.setVisible(self.stationsDisplayed)
        
    def setStation(self, obj):
        self.deselectAllStations()
        obj.setStyleSheet(self.stationSelectedListingStyle)
        self.toggleStationDisplay()
        self.lblChannelDisplay.setText(obj.text())
        self.emit(QtCore.SIGNAL('setPandoraStation'), obj.text())  
        
        
    def deselectAllStations(self):
        for i in range(len(self.stations)):
            self.stations[i].setStyleSheet(self.stationListingStyle)
    
   
        
    
    
    
        