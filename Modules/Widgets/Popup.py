
from PyQt4 import QtCore, QtGui, uic
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from clickable import *
from Modules.Widgets.ButtonIndicator import *
from enum import Enum
from perpetualTimer import perpetualTimer


class PopupType(Enum):
    CONFIRM = 0
    OPTIONS=1
    NUMBER=2
    ALARM=3

class Popup(QtGui.QWidget):

    popupStyle = "border: 2px solid #fff;color: #fff;"

    popupContentsStyle = "border: none;background-color:#000;  "

    popupButtonStyle = "QPushButton { font-size:20px;background-color:#000; border: 2px solid #fff;color:#fff; padding: 5px; } QPushButton:pressed { background-color:#fff; color: #000;  }"

    optionListingStyle = "font-size:15pt;background-color: #000;color:#fff;padding:5px;"
    optionSelectedListingStyle = "font-size:15pt;background-color: #fff; color:#000;padding:5px;"

    maxDigits = None

    currentResult = None

    currentType = None


    def __init__(self, parent):
        super(Popup, self).__init__(parent)
        
        self.resize(320, 240)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)

        self.popupFrame = QtGui.QFrame(self)        
        self.popupFrame.setGeometry(QtCore.QRect(0, 0, 320, 240))  
        self.popupFrame.setFrameShape(QtGui.QFrame.Box)
        self.popupFrame.setFrameShadow(QtGui.QFrame.Plain)

        font = QtGui.QFont()
        font.setPointSize(14)
       

        self.onButtonIndicator = ButtonIndicator(self.popupFrame, 30, "green")
        self.onButtonIndicator.setGeometry(QtCore.QRect(10,202,30,30))
        pressableSender(self.onButtonIndicator).connect(self.greenIndicatorPressed)
        self.onButtonIndicator.setVisible(False)

        self.offButtonIndicator = ButtonIndicator(self.popupFrame, 30, "red")
        self.offButtonIndicator.setGeometry(QtCore.QRect(280,202,30,30))
        pressableSender(self.offButtonIndicator).connect(self.redIndicatorPressed)
        self.offButtonIndicator.setVisible(False)

        QtCore.QMetaObject.connectSlotsByName(self)  


    def processPin(self, pinConfig, pin):
        if(pin == pinConfig["ON_BUTTON"]):
            self.greenIndicatorPressed()
        elif(pin == pinConfig["OFF_BUTTON"]):
            self.redIndicatorPressed()

    def greenIndicatorPressed(self):
        sendResult = True
        if(self.currentType == PopupType.NUMBER):     
            try:
                r = int(str(self.currentResult).translate(None, '-'))
            except:
                sendResult = False
                self.numberSelect.setStyleSheet("border: 2px solid #ff0000; color: #eeff00; ")

        if(sendResult):
            self.emit(QtCore.SIGNAL('popupResult'), self.currentResult)
            self.closePopup()


    def redIndicatorPressed(self):
        
        if(hasattr(self, "alarmDisplayTimer") and self.alarmDisplayTimer != None):
            self.alarmDisplayTimer.cancel()

        self.closePopup()


    def alarm(self):
        self.currentType = PopupType.ALARM

        font = QtGui.QFont()
        font.setPointSize(60)
        self.prompt = QtGui.QLabel(self.popupFrame)
        self.prompt.setGeometry(QtCore.QRect((320/2)-(300/2),10,300,180))
        self.prompt.setAlignment(QtCore.Qt.AlignCenter)
        self.prompt.setStyleSheet("border: none; color: #eeff00; ")
        self.prompt.setFont(font)
        self.prompt.setText("WAKE\nUP")        
                
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.red)        
        self.setPalette(p)

        self.show()

    def numberSelect(self, msg, maxDigits):
        self.currentType = PopupType.NUMBER
        self.maxDigits = maxDigits

        self.onButtonIndicator.setVisible(True)
        self.offButtonIndicator.setVisible(True)

        font = QtGui.QFont()
        font.setPointSize(17)

        self.prompt = QtGui.QLabel(self.popupFrame)
        self.prompt.setGeometry(QtCore.QRect(10,0,300,40))
        self.prompt.setAlignment(QtCore.Qt.AlignLeft)
        self.prompt.setStyleSheet("border: none; color: #eeff00; ")
        self.prompt.setFont(font)
        self.prompt.setText(msg)

        numberWidget = QtGui.QWidget(self)
        numberWidget.setGeometry(QtCore.QRect((320/2)-(220/2), 30, 220, 150))
        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)
        numberWidget.setLayout(grid)

        numbers = ['1', '2', '3', 
                   '4', '5', '6', 
                   '7', '8', '9',
                   'CLR', '0']

        positions = [(i,j) for i in range(4) for j in range(3)]

        for position, num in zip(positions, numbers):            
            if num == '':
                continue
            button = QtGui.QPushButton(num)
            button.setFont(font)
            pressableSender(button).connect(self.numberSelected)
            grid.addWidget(button, *position)

        self.numberSelect = QtGui.QLabel(self.popupFrame)
        self.numberSelect.setGeometry(QtCore.QRect((320/2)-(80/2),175,80,40))
        self.numberSelect.setAlignment(QtCore.Qt.AlignCenter)
        self.numberSelect.setStyleSheet("border: 2px solid #000; color: #eeff00; ")
        self.numberSelect.setFont(font)
        self.numberSelect.setText(self.getBlankString())


        self.show()

    def getBlankString(self):
        bs = []
        for x in range(0,self.maxDigits):
            bs.append("-")
        return "".join(bs)

    def numberSelected(self, obj):
        #obj = self.sender()
        if(obj.text() == "CLR"):
            self.currentResult = ""
            self.numberSelect.setText(self.getBlankString())
        else:
            txtlist = list(str(self.numberSelect.text()))
            for x in range(0,self.maxDigits):
                if(txtlist[x] == "-"):
                    txtlist[x] = str(obj.text())
                    self.numberSelect.setText("".join(txtlist) )
                    break
            r = str(self.numberSelect.text()).translate(None, '-')
            self.currentResult = r
                


    def optionSelect(self, msg, options):
        self.currentType = PopupType.OPTIONS
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
        self.emit(QtCore.SIGNAL('popupResult'),obj.tag)
        self.closePopup()

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


    '''
    def doConfirm(self, promptText, tag):
        self.currentType = PopupType.CONFIRM
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
    '''
        
    def buttonCallback(self):
        self.emit(QtCore.SIGNAL('popupResult'), [self.sender().name, self.sender().tag])
        self.closePopup()

    def closePopup(self):
        self.close()
        self = None