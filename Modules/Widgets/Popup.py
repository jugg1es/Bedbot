
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush

    
class Popup(QtGui.QWidget):

    popupStyle = "border: 2px solid #fff;color: #fff;"

    popupContentsStyle = "border: none; "

    popupButtonStyle = "QPushButton { font-size:20px;background-color:#000; border: 2px solid #fff;color:#fff; padding: 5px; } QPushButton:pressed { background-color:#fff; color: #000;  }"

    def __init__(self, parent):
        super(Popup, self).__init__(parent)
        
        self.resize(320, 210)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)

        self.popupFrame = QtGui.QFrame(self)        
        self.popupFrame.setGeometry(QtCore.QRect(5, 0, 310, 190))  
        self.popupFrame.setFrameShape(QtGui.QFrame.Box)
        self.popupFrame.setFrameShadow(QtGui.QFrame.Plain)
        self.popupFrame.setStyleSheet(self.popupStyle)

        QtCore.QMetaObject.connectSlotsByName(self)  

    def doConfirm(self, promptText, tag):

        font = QtGui.QFont()
        font.setPointSize(20)

        self.prompt = QtGui.QLabel(self.popupFrame)
        self.prompt.setGeometry(QtCore.QRect(10,10,300,80))
        self.prompt.setAlignment(QtCore.Qt.AlignCenter)
        self.prompt.setStyleSheet(self.popupContentsStyle)
        self.prompt.setFont(font)
        self.prompt.setText(promptText)

        self.horizontalLayoutWidget = QtGui.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 100, 300, 80))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setAlignment(self.horizontalLayoutWidget, QtCore.Qt.AlignCenter)
        #self.horizontalLayout.setMargin(20)


        self.btnOK = QtGui.QPushButton("OK", self.horizontalLayoutWidget)
        self.btnOK.name = "OK"
        self.btnOK.tag = tag
        self.btnOK.setStyleSheet(self.popupButtonStyle)
        self.btnOK.clicked.connect(self.buttonCallback)
        self.horizontalLayout.addWidget(self.btnOK)

        self.btnCancel = QtGui.QPushButton("Cancel", self.horizontalLayoutWidget)
        self.btnCancel.tag = tag
        self.btnCancel.name = "CANCEL"
        self.btnCancel.setStyleSheet(self.popupButtonStyle)
        self.btnCancel.clicked.connect(self.buttonCallback)
        self.horizontalLayout.addWidget(self.btnCancel)


        self.show()
        
    def buttonCallback(self):
        self.emit(QtCore.SIGNAL('popupResult'), [self.sender().name, self.sender().tag])
        self.close()
    