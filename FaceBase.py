
from PyQt4 import QtGui, QtCore
import RigUIControls
import math
import sys

class RigFaceSetup(QtGui.QWidget):
    def __init__(self):
        super(RigFaceSetup, self).__init__()
        self.setWindowTitle("LED Light Line Colour Picker")
        self.setGeometry(50,50, 600, 600)
        self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.iP = str(sys.argv[1])
        self.port = str(sys.argv[2])
        self.initUI()
       
       
    def initUI(self):   
        vbox = QtGui.QVBoxLayout()
        self.view = RigUIControls.RigGraphicsView(self.iP, self.port, self.ColourPickerCircle)

        vbox.addWidget(self.view)
        self.setLayout(vbox)
        
    
    def changeValue(self, value):
        self.view.rect.doRotate(value)     


app = QtGui.QApplication([])
ex = RigFaceSetup()
ex.show()
app.exec_()
