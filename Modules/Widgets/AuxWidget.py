
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

    
class AuxWidget(QtGui.QWidget):
    
       
    
    def __init__(self, parent):
        super(AuxWidget, self).__init__(parent)
        self.resize(320, 160)
                
        font = QtGui.QFont()
        font.setPointSize(35)
        
        self.auxDisplay = QtGui.QLabel(self)
        self.auxDisplay.setGeometry(QtCore.QRect(0, 10, 320, 50))
        self.auxDisplay.setAlignment(QtCore.Qt.AlignHCenter )
        self.auxDisplay.setStyleSheet('color: #fff')
        self.auxDisplay.setWordWrap(True)
        self.auxDisplay.setFont(font)       
        self.auxDisplay.setText("AUX INPUT")
        
               
       
        
        QtCore.QMetaObject.connectSlotsByName(self)       
        