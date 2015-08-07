
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush

    
class DiagnosticWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(DiagnosticWidget, self).__init__(parent)
        
        self.resize(320, 210)
        
        dfont = QtGui.QFont()
        dfont.setPointSize(10)

        self.lblDesc = QtGui.QLabel(self)
        self.lblDesc.setGeometry(QtCore.QRect(5, 10, 310, 30))
        self.lblDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.lblDesc.setStyleSheet('color: #fff')
        self.lblDesc.setFont(dfont)
        self.lblDesc.setText("Diagnostics: press a button\n to view which pin fired")

        font = QtGui.QFont()
        font.setPointSize(70)
        
        self.lblPinDisplay = QtGui.QLabel(self)
        self.lblPinDisplay.setGeometry(QtCore.QRect(5, 70, 310, 120))
        self.lblPinDisplay.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.lblPinDisplay.setStyleSheet('color: #fff')
        self.lblPinDisplay.setFont(font)

        
        self.lblPinDisplay.setText("--")
     
        QtCore.QMetaObject.connectSlotsByName(self)  
        
    
    def updatePinDisplay(self, pinDisplay):
        if(pinDisplay == ""):
            self.lblPinDisplay.setText("--")
        else:
            self.lblPinDisplay.setText(str(pinDisplay))

        