
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from clickable import *

    
class Popup(QtGui.QWidget):

    popupStyle = "border: 2px solid #fff;color: #fff;"

    popupContentsStyle = "border: none; "

    popupButtonStyle = "QPushButton { font-size:20px;background-color:#000; border: 2px solid #fff;color:#fff; padding: 5px; } QPushButton:pressed { background-color:#fff; color: #000;  }"

    optionListingStyle = "font-size:15pt;background-color: #000;color:#fff;padding:5px;"
    optionSelectedListingStyle = "font-size:15pt;background-color: #fff; color:#000;padding:5px;"


    maxDigits = None

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

    def numberSelect(self, msg, maxDigits):
        self.maxDigits = maxDigits

        font = QtGui.QFont()
        font.setPointSize(18)

        self.prompt = QtGui.QLabel(self.popupFrame)
        self.prompt.setGeometry(QtCore.QRect(10,0,300,40))
        self.prompt.setAlignment(QtCore.Qt.AlignLeft)
        self.prompt.setStyleSheet("border: none; color: #eeff00; ")
        self.prompt.setFont(font)
        self.prompt.setText(msg)

        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect((320/2)-(220/2), 30, 220, 100))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setAlignment(self.verticalLayoutWidget, QtCore.Qt.AlignCenter)
        self.verticalLayout.setMargin(0)

        buttonHeight = 30
       
        numberTracker = 1

        for x in range(0,3):
            
            horizontalLayoutWidget = QtGui.QWidget()
            horizontalLayout = QtGui.QHBoxLayout(horizontalLayoutWidget)
            horizontalLayout.setAlignment(horizontalLayoutWidget, QtCore.Qt.AlignHCenter)
            self.verticalLayout.addWidget(horizontalLayoutWidget)
            horizontalLayout.setMargin(0)
            for y in range(numberTracker, (numberTracker + 3)):
                opt = QtGui.QLabel( str(y))             
                opt.setStyleSheet("border: 2px solid #fff;color: #fff; font-size: 13pt; ")
                opt.setAlignment(QtCore.Qt.AlignCenter)
                opt.setGeometry(QtCore.QRect(0, 0, 30, buttonHeight))
                opt.tag = y
                pressableSender(opt).connect(self.numberSelected)
                horizontalLayout.addWidget(opt)
            numberTracker = numberTracker + 3

        horizontalLayoutWidget = QtGui.QWidget()
        horizontalLayout = QtGui.QHBoxLayout(horizontalLayoutWidget)
        horizontalLayout.setAlignment(horizontalLayoutWidget, QtCore.Qt.AlignHCenter)
        self.verticalLayout.addWidget(horizontalLayoutWidget)
        horizontalLayout.setMargin(0)

        deleteButton = QtGui.QLabel("CLR")             
        deleteButton.setStyleSheet("border: 2px solid #fff;color: #fff; font-size: 13pt;")
        deleteButton.setAlignment(QtCore.Qt.AlignCenter)
        deleteButton.setGeometry(QtCore.QRect(0, 0, 30, buttonHeight))
        deleteButton.tag = "CLR"
        pressableSender(deleteButton).connect(self.numberSelected)
        horizontalLayout.addWidget(deleteButton)

        opt = QtGui.QLabel("0")             
        opt.setStyleSheet("border: 2px solid #fff;color: #fff; font-size: 13pt;")
        opt.setAlignment(QtCore.Qt.AlignCenter)
        opt.setGeometry(QtCore.QRect(0, 0, 30, buttonHeight))
        opt.tag = "0"
        pressableSender(opt).connect(self.numberSelected)
        horizontalLayout.addWidget(opt)

        okButton = QtGui.QLabel("OK")             
        okButton.setStyleSheet("border: 2px solid #fff;color: #fff; font-size: 13pt;")
        okButton.setAlignment(QtCore.Qt.AlignCenter)
        okButton.setGeometry(QtCore.QRect(0, 0, 30, buttonHeight))
        okButton.tag = "OK"
        pressableSender(okButton).connect(self.numberSelected)
        horizontalLayout.addWidget(okButton)

        self.numberSelect = QtGui.QLabel(self.popupFrame)
        self.numberSelect.setGeometry(QtCore.QRect(10,140,300,40))
        self.numberSelect.setAlignment(QtCore.Qt.AlignCenter)
        self.numberSelect.setStyleSheet("border: none; color: #eeff00; ")
        self.numberSelect.setFont(font)
        self.numberSelect.setText("")

        self.show()

    def numberSelected(self, obj):
        if(obj.tag == "OK"):
            txt = self.numberSelect.text()
            self.emit(QtCore.SIGNAL('popupResult'), None,txt)
            self.close()
        elif(obj.tag == "CLR"):
            self.numberSelect.setText("")
        else:
            txt = self.numberSelect.text()
            if(len(txt) < self.maxDigits):
                self.numberSelect.setText(txt + str(obj.tag))


    def optionSelect(self, msg, options):
        font = QtGui.QFont()
        font.setPointSize(18)

        self.prompt = QtGui.QLabel(self.popupFrame)
        self.prompt.setGeometry(QtCore.QRect(10,0,300,40))
        self.prompt.setAlignment(QtCore.Qt.AlignLeft)
        self.prompt.setStyleSheet("border: none; color: #eeff00; ")
        self.prompt.setFont(font)
        self.prompt.setText(msg)

        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 60, 300, 110))
        self.verticalLayoutWidget.setAutoFillBackground(True)
        p = self.verticalLayoutWidget.palette()
        
        p.setColor(self.verticalLayoutWidget.backgroundRole(), QtCore.Qt.black)
        self.verticalLayoutWidget.setPalette(p)
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(5)
            
        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidget(self.verticalLayoutWidget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(140)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.scroll)

        for x in options:
            opt = QtGui.QLabel(x)             
            opt.setStyleSheet(self.optionListingStyle)
            opt.tag = x
            pressableSender(opt).connect(self.optionSelected)
            self.verticalLayout.addWidget(opt)

        self.show()

    def optionSelected(self, obj):
        self.emit(QtCore.SIGNAL('popupResult'), None, obj.tag)
        self.close()

    def doWait(self, msg):
        font = QtGui.QFont()
        font.setPointSize(20)

        self.prompt = QtGui.QLabel(self.popupFrame)
        self.prompt.setGeometry(QtCore.QRect(10,10,300,80))
        self.prompt.setAlignment(QtCore.Qt.AlignCenter)
        self.prompt.setStyleSheet(self.popupContentsStyle)
        self.prompt.setFont(font)
        self.prompt.setText(msg)

        self.horizontalLayoutWidget = QtGui.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 100, 300, 80))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setAlignment(self.horizontalLayoutWidget, QtCore.Qt.AlignCenter)
        #self.horizontalLayout.setMargin(20)


        self.btnCancel = QtGui.QPushButton("CANCEL", self.horizontalLayoutWidget)
        self.btnCancel.name = "CANCEL"
        self.btnCancel.tag = "CANCEL"
        self.btnCancel.setStyleSheet(self.popupButtonStyle)
        self.btnCancel.clicked.connect(self.buttonCallback)
        self.horizontalLayout.addWidget(self.btnCancel)


        self.show()



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
    