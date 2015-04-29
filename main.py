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

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
    



class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.resize(320,240)
        self.move(0,0)
        
        self.setAutoFillBackground(True)
        
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)
        
        self.primary_widget = PrimaryWidget(self)
        self.setCentralWidget(self.primary_widget)
        
        self.primary_widget.showTimeWidget()
        
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    
    
    def closeEvent(self, *args, **kwargs):
        self.primary_widget.doClose()
        #self.comm.stopServer()

        
class MyApplication(QtGui.QApplication):    
    def __init__(self, args):
        super(MyApplication, self).__init__(args)
  
    def setMainWindow(self, win):
        self.w = win
        
    def notify(self, receiver, event):
        if(event.type() == QtCore.QEvent.KeyPress):
            if (event.key() == QtCore.Qt.Key_Escape):
                self.w.close()
        return super(MyApplication, self).notify(receiver, event)
  
if __name__ == '__main__':
    import sys
    
    app = MyApplication(sys.argv)
    
    logging.basicConfig(filename='bedbot.log', level=logging.INFO)
    logging.info('--- Launched ---')
    
    win = MainWindow()
    app.setMainWindow(win)
    win.show()
    
        
    
    sys.exit(app.exec_())
    
    
