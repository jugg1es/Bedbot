
from PyQt4 import QtCore, QtGui, uic
import time

class ButtonIndicator(QtGui.QWidget):

    diameter = 30
    buttonColor = "#fff"
    penWidth = 3

    fullDiameter = None

    def __init__(self, parent=None,  diameter=30, color="#fff"):
        QtGui.QWidget.__init__(self, parent)
        self.diameter = diameter - (self.penWidth *2)
        self.fullDiameter = diameter
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

        pen.setStyle(QtCore.Qt.SolidLine);
        pen.setWidth(3);
        pen.setBrush(QtCore.Qt.red);

        paint.setPen(pen)

        center = QtCore.QPoint(cx, cy)
        paint.drawEllipse(center, radx, rady)

       
        paint.end()