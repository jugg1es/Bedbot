
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush

    
class DiagnosticWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(DiagnosticWidget, self).__init__(parent)
        
        self.resize(320, 210)
        font = QtGui.QFont()
        font.setPointSize(85)
        
        self.lblPinDisplay = QtGui.QLabel(self)
        self.lblPinDisplay.setGeometry(QtCore.QRect(5, 50, 310, 120))
        self.lblPinDisplay.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.lblPinDisplay.setStyleSheet('color: #fff')
        self.lblPinDisplay.setFont(font)
     
        QtCore.QMetaObject.connectSlotsByName(self)  
        
    
    def updatePinDisplay(self, pinDisplay):
        if(pinDisplay == ""):
            self.lblPinDisplay.setText("--")
        else:
            self.lblPinDisplay.setText(str(pinDisplay))

        