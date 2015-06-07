
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
    
class InternetRadioWidget(QtGui.QWidget):
    stationListingStyle = "font-size:18pt;background-color: #000;color:#fff;padding:5px;"
    stationSelectedListingStyle = "font-size:18pt;background-color: #fff; color:#000;padding:5px;"
    
    stationObjects = []

    currentStation = None

    def __init__(self, parent):
        super(InternetRadioWidget, self).__init__(parent)
        
        self.resize(320, 210)
        font = QtGui.QFont()
        font.setPointSize(35)
        
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 320, 160))
        self.verticalLayoutWidget.setAutoFillBackground(True)
        p = self.verticalLayoutWidget.palette()
        
        p.setColor(self.verticalLayoutWidget.backgroundRole(), Qt.black)
        self.verticalLayoutWidget.setPalette(p)
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(5)
            
        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidget(self.verticalLayoutWidget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(160)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.scroll)
        QtCore.QMetaObject.connectSlotsByName(self)  


    def fillStationList(self, stationList):
        self.stationObjects = []
        
        for i in range(0, len(stationList)):
            sObj = stationList[i]                
            station = QtGui.QLabel(sObj.name)             
            station.setStyleSheet(self.stationListingStyle)
            station.tag = i
            self.verticalLayout.addWidget(station)
            pressableSender(station).connect(self.setStation)
            self.stationObjects.append(station)

    def getCurrentStation(self):
        return self.currentStation

    def setStation(self, obj):
        self.deselectAllStations()
        obj.setStyleSheet(self.stationSelectedListingStyle)
        self.currentStation = obj.tag
        #self.emit(QtCore.SIGNAL('stationSelected'), obj.tag)  
        
       
    def deselectAllStations(self):
        for i in range(len(self.stationObjects)):
            self.stationObjects[i].setStyleSheet(self.stationListingStyle)
        
