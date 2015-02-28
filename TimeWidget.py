
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from perpetualTimer import perpetualTimer

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
    

    
class TimeWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(TimeWidget, self).__init__(parent)
        
        self.resize(320, 210)
        font = QtGui.QFont()
        font.setPointSize(85)
        
        self.lblTimeDisplay = QtGui.QLabel(self)
        self.lblTimeDisplay.setGeometry(QtCore.QRect(5, 50, 310, 120))
        self.lblTimeDisplay.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.lblTimeDisplay.setStyleSheet('color: #fff')
        self.lblTimeDisplay.setFont(font)
     
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)  
        
    
    def retranslateUi(self, Form):
        #self.label.setText(_translate("Form", ":", None))
        self.updateCurrentTime()
        
    
        
    
        
        
    def updateCurrentTime(self):
        display = time.strftime("%I:%M").lstrip('0')
        self.lblTimeDisplay.setText(display)
        #self.lblHour.setText(_translate("Form", time.strftime("%I"), None))
        #self.lblMinute.setText(_translate("Form", time.strftime("%M"), None))
        