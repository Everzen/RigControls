
from PyQt4 import QtGui, QtCore
import RigUIControls
import math
import sys
import Icons

class RigFaceSetup(QtGui.QWidget):
# class RigFaceSetup(QtGui.QMainWindow):
    def __init__(self):
        super(RigFaceSetup, self).__init__()
        self.setWindowTitle("LED Light Line Colour Picker")
        self.setGeometry(50,50, 600, 600)
        self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.initUI()
       
       
    def initUI(self):   
        #Setup Style Sheet information
        # f=open('css/darkorange.stylesheet', 'r')
        f=open('darkorange.stylesheet', 'r')
        self.styleData = f.read()
        f.close()
        # print str(self.styleData)

        self.setStyleSheet(self.styleData)
        self.view = RigUIControls.RigGraphicsView(self.ColourPickerCircle)
        self.view.setStyleSheet('background-color: #888888') #Adding adjustments to the background of the Graphics View
        self.markerSpawn = RigUIControls.DragItemButton("GuideMarker")
        # self.showReflectionLineButton = QtGui.QCheckButton("Toggle Reflection Line")

        self.reflectGuides = QtGui.QPushButton("Reflect Markers")
        self.reflectGuides.clicked.connect(self.view.reflectGuides)
        self.testCheckBox = QtGui.QCheckBox("Check me Out")

        hBox = QtGui.QHBoxLayout()
        vButtonBox = QtGui.QVBoxLayout()
        vButtonBox.addWidget(self.markerSpawn)
        vButtonBox.addWidget(self.reflectGuides)
        vButtonBox.addWidget(self.testCheckBox)
        vButtonBox.addStretch(1)

        hBox.addWidget(self.view)
        hBox.addLayout(vButtonBox)

        self.setLayout(hBox)

    def changeValue(self, value):
        self.view.rect.doRotate(value)     


app = QtGui.QApplication([])
app.setStyle('Plastique')
ex = RigFaceSetup()
ex.show()
app.exec_()
