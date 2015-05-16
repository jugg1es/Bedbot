
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from threading import Timer,Thread,Event
import sys
from PyQt4.QtGui import *
from PyQt4.Qt import QBrush
from clickable import *
from PyQt4 import QtSvg
from PyQt4.QtSvg import QSvgWidget

class DynamicMenu(QtGui.QWidget):
    
    menuItems =[]
    currentItem = None

    def __init__(self, parent):
        super(DynamicMenu, self).__init__(parent)
        self.resize(320, 70)
                
        self.setAutoFillBackground(True)

    def addMenuItem(self, obj):

        menuButton = QSvgWidget(obj.getMenuIcon(), self)
        menuButton.tag = obj
        self.menuItems.append(menuButton)

    def configureMenu(self):
        horizPadding = 10
        possibleWidth = self.width() - (horizPadding *2)

        if(len(self.menuItems) == 0):
            return
        iconWidth = possibleWidth / len(self.menuItems)
        xTracker = horizPadding

        for i in range(0,len(self.menuItems)):
            xTracker = self.configureMenuItem(i,iconWidth,xTracker)

    def configureMenuItem(self, order, iconWidth, xTracker):
        for w in self.menuItems:
            if(w.tag.menuOrder == order):
                iconPosition = xTracker + ((iconWidth / 2 ) - (w.tag.getMenuIconWidth() /2))
                w.setGeometry(QtCore.QRect(iconPosition, 0, w.tag.getMenuIconWidth(), w.tag.getMenuIconHeight()))
                clickableSender(w).connect(self.menuButtonClicked)
                xTracker += iconWidth
        return xTracker

    def menuButtonClicked(self, sender):
        self.deselectAll()
        sender.load(sender.tag.getMenuIconSelected())
        self.currentItem = sender
        self.t = QTimer()
        self.t.timeout.connect(self.doShowWidget)
        self.t.start(500)
        
    def doShowWidget(self):
        self.t.stop()
        self.emit(QtCore.SIGNAL('showWidget'), self.currentItem.tag)


    def deselectAll(self):
        for w in self.menuItems:
            w.load(w.tag.getMenuIcon())

        
       
        
        