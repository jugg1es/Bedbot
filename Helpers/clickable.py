
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import datetime
from threading import Timer,Thread,Event

def clickable(widget, holdTime=1):
    class Filter(QObject):    
        clicked = pyqtSignal(QWidget)      
        timer = None
        sender = None
        timeoutReached = False

        def holdTimerCallback(self):
            print("callback")
            self.timer.cancel()
            self.timeoutReached = True

        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        self.sender = obj
                        self.timer = Timer(holdTime,self.holdTimerCallback)
                        self.timer.start()                        

                elif event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):                        
                        if(self.timeoutReached == False):
                            self.timer.cancel()
                            self.clicked.emit(self.sender)

            return False    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked




def holdable(widget, holdTime=1):
    class Filter(QObject):    
        clicked = pyqtSignal(QWidget)      
        timer = None
        sender = None
        def holdTimerCallback(self):
            print("callback")
            self.timer.cancel()
            self.clicked.emit(self.sender)

        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        self.sender = obj
                        self.timer = Timer(holdTime,self.holdTimerCallback)
                        self.timer.start()                        

                elif event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.timer.cancel()

            return False    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked


def releaseable(widget):
    class Filter(QObject):    
        clicked = pyqtSignal()        
        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True            
            return False
    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

def releaseableSender(widget):
    class Filter(QObject):    
        clicked = pyqtSignal(QWidget)        
        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit(obj)
                        return True            
            return False    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

def pressable(widget):
    class Filter(QObject):    
        clicked = pyqtSignal()        
        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True            
            return False    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

def pressableSender(widget):
    class Filter(QObject):    
        clicked = pyqtSignal(QWidget)        
        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit(obj)
                        return True            
            return False    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked