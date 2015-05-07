
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time


def clickable(widget):

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

def clickableSender(widget):

    class Filter(QObject):
    
        clicked = pyqtSignal( QWidget)
        
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


def pressable(widget):

    class Filter(QObject):
    
        clicked = pyqtSignal()
        
        def eventFilter(self, obj, event):
        
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        # The developer can opt for .emit(obj) to get the object within the slot.
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
                        # The developer can opt for .emit(obj) to get the object within the slot.
                        return True
            
            return False
    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked