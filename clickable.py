
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import datetime

def clickable(widget):
    class Filter(QObject):    
        clicked = pyqtSignal(QWidget)        
        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        obj.clickedTime = datetime.datetime.now()
                        #return True     
                elif event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        if(obj.clickedTime):
                            diff = datetime.datetime.now() - obj.clickedTime
                            obj.clickedTime = None
                            if(diff.total_seconds() < 1):                                
                                self.clicked.emit(obj)
                                return True           
            return False    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

def holdable(widget):
    class Filter(QObject):    
        clicked = pyqtSignal(QWidget)        
        def eventFilter(self, obj, event):        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        obj.heldDown = datetime.datetime.now()
                        #return True     
                elif event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        if(obj.heldDown):
                            diff = datetime.datetime.now() - obj.heldDown
                            obj.heldDown = None
                            if(diff.total_seconds() >= 1):                                
                                self.clicked.emit(obj)
                                return True           
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