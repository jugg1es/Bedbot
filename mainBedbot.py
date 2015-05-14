from PyQt4 import  QtGui, uic, QtCore
import time
from threading import Timer,Thread,Event
from PyQt4.Qt import QBrush
from Widgets.TimeWidget import *
from Widgets.MenuWidget import *
from BedbotWidget import BedbotWidget
import logging
import os
import pkgutil
import importlib 
import inspect
import glob

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

        loadedModules = []

        path = "Modules"
        modules = pkgutil.iter_modules(path=[path])
        for loader, mod_name, ispkg in modules:
            # Ensure that module isn't already loaded
            print(mod_name)
            if mod_name not in sys.modules:
                # Import module
                loaded_mod = __import__(path+"."+mod_name, fromlist=[mod_name])
                # Load class from imported module
                # class_name = mod_name
                loaded_class = getattr(loaded_mod, mod_name)
                loadedModules.append(loaded_class())

        self.primary_widget = BedbotWidget(self,loadedModules)
        self.setCentralWidget(self.primary_widget)

    def closeEvent(self, *args, **kwargs):
        self.primary_widget.doClose()
        
        
    def gotoNextMenuItem(self):
        self.primary_widget.contextButtonPressed()


        
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
    
    
