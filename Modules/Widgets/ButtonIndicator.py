
from PyQt4 import QtCore, QtGui, uic
import time

class ButtonIndicator(QtGui.QWidget):

    diameter = 30
    buttonColor = "white"
    penWidth = 3

    fullDiameter = None

    def __init__(self, parent=None,  diameter=30, color="white"):
        QtGui.QWidget.__init__(self, parent)

        self.setAutoFillBackground(True)
        
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)

        self.diameter = diameter - ((self.penWidth *2) +1)
        self.fullDiameter = diameter
        self.buttonColor = color
        self.setGeometry(0, 0, self.diameter , self.diameter )

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setRenderHint(QtGui.QPainter.Antialiasing)

        paint.setBrush(QtCore.Qt.black)
        paint.drawRect(event.rect())

        radx = self.diameter / 2
        rady = self.diameter / 2

        cx = self.fullDiameter / 2
        cy = self.fullDiameter / 2

        pen = QtGui.QPen()

        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(self.penWidth);
        if(self.buttonColor == "white"):
            pen.setBrush(QtCore.Qt.white)
        elif(self.buttonColor == "red"):
            pen.setBrush(QtCore.Qt.red)
        elif(self.buttonColor == "blue"):
            pen.setBrush(QtCore.Qt.blue)
        elif(self.buttonColor == "green"):
            pen.setBrush(QtCore.Qt.green)

        paint.setPen(pen)

        center = QtCore.QPoint(cx, cy)
        paint.drawEllipse(center, radx, rady)

       
        paint.end()