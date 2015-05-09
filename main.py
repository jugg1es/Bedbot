'''
Created on Jan 4, 2015

@author: Proca
'''

from PyQt4 import  QtGui, uic, QtCore
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from Widgets.TimeWidget import *
from Widgets.MenuWidget import *
from PrimaryWidget import PrimaryWidget
import logging
import os

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
    


'''
Pressing the escape key will properly dispose and exit

pressing the right arrow key will scan through menu options


'''
class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        
        
        screen_rect = app.desktop().screenGeometry()
        if(screen_rect.width() == 320):
            self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        
        
        
        
        self.resize(320,240)
        self.move(0,0)
        
        self.setAutoFillBackground(True)
        
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)
        
        self.primary_widget = PrimaryWidget(self)
        self.setCentralWidget(self.primary_widget)
        
        self.primary_widget.showTimeWidget()
        
        
        
    
    
    def closeEvent(self, *args, **kwargs):
        self.primary_widget.doClose()
        
        
    def gotoNextMenuItem(self):
        self.primary_widget.gotoNextMenuItem()

        
class MyApplication(QtGui.QApplication):    
    def __init__(self, args):
        super(MyApplication, self).__init__(args)
        
  
    def setMainWindow(self, win):
        self.w = win
        
    def notify(self, receiver, event):
        if(event.type() == QtCore.QEvent.KeyPress):
            if (event.key() == QtCore.Qt.Key_Escape):
                self.w.close()
            elif(event.key() == QtCore.Qt.Key_Right):
                self.w.gotoNextMenuItem()
                
        return super(MyApplication, self).notify(receiver, event)
  
if __name__ == '__main__':
    import sys
    
    #sets the current directory as the working directory
    launchDir = str(os.path.dirname(os.path.realpath(__file__)));
    os.chdir(launchDir)
    print("Setting working directory to:" + launchDir)
    
    
    app = MyApplication(sys.argv)
    
    
    logging.basicConfig(filename='bedbot.log', level=logging.INFO)
    
    win = MainWindow()
    app.setMainWindow(win)
    win.show()
    
        
    
    sys.exit(app.exec_())
    
    
