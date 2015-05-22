
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
        self.resize(320, 190)
                
        self.setAutoFillBackground(True)

    def addMenuItem(self, obj):

        menuButton = QSvgWidget(obj.getMenuIcon(), self)
        menuButton.tag = obj
        self.menuItems.append(menuButton)

    def configureMenu(self):
        if(len(self.menuItems) == 0):
            return

        padding = 10
        possibleWidth = self.width() - (padding *2)

        maxPerRow = 3
        if(len(self.menuItems) < maxPerRow):
            maxPerRow = len(self.menuItems)
        
        iconWidth = possibleWidth / maxPerRow
        iconHeight = 80

        xTracker = padding
        yTracker = padding

        for i in range(0,len(self.menuItems)):    
            self.configureMenuItem(self.menuItems[i],iconWidth,xTracker,yTracker)
            xTracker += iconWidth
            if(i > 0 and (i +1) % maxPerRow == 0):
                yTracker += iconHeight
                xTracker = padding

    def configureMenuItem(self, w, iconWidth, xTracker,yTracker):
        iconPosition = xTracker + ((iconWidth / 2 ) - (w.tag.getMenuIconWidth() /2))
        w.setGeometry(QtCore.QRect(iconPosition, yTracker, w.tag.getMenuIconWidth(), w.tag.getMenuIconHeight()))
        pressableSender(w).connect(self.menuButtonClicked)
        pressableSender(w).connect(self.menuButtonClicked)
        
    def setMenuItemSelected(self, m):
        for w in self.menuItems:
            if(w.tag == m):
                self.setIconSelected(w)

    def setIconSelected(self, obj):
        self.deselectAll()
        obj.load(obj.tag.getMenuIconSelected())
        self.currentItem = obj

    def menuButtonClicked(self, sender):
        self.setIconSelected(sender)
        self.t = QTimer()
        self.t.timeout.connect(self.doShowWidget)
        self.t.start(500)
        
    def doShowWidget(self):
        self.t.stop()
        self.emit(QtCore.SIGNAL('showWidget'), self.currentItem.tag)


    def deselectAll(self):
        for w in self.menuItems:
            w.load(w.tag.getMenuIcon())

        
       
        
        