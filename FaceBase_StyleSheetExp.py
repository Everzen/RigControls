
import sip
sip.setapi('QVariant',2)

from PyQt4 import QtGui, QtCore
import RigUIControls
import math
import sys

# class RigFaceSetup(QtGui.QWidget):
# # class RigFaceSetup(QtGui.QMainWindow):
#     def __init__(self):
#         super(RigFaceSetup, self).__init__()
#         self.setWindowTitle("LED Light Line Colour Picker")
#         self.setGeometry(50,50, 600, 600)
#         self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
#         self.initUI()
       
       
    # def initUI(self):   
    #     #Setup Style Sheet information
    #     f=open('css/darkorange.stylesheet', 'r')
    #     self.styleData = f.read()
    #     f.close()
    #     print str(self.styleData)

    #     self.setStyleSheet(self.styleData)
    #     self.view = RigUIControls.RigGraphicsView(self.ColourPickerCircle)
    #     self.markerSpawn = RigUIControls.dragItemButton("GuideMarker")
    #     self.testButton = QtGui.QPushButton("Test\nTest\nTest")

    #     hBox = QtGui.QHBoxLayout()
    #     vButtonBox = QtGui.QVBoxLayout()
    #     vButtonBox.addWidget(self.markerSpawn)
    #     vButtonBox.addWidget(self.testButton)
    #     vButtonBox.addStretch(1)

    #     hBox.addWidget(self.view)
    #     hBox.addLayout(vButtonBox)

    #     self.setLayout(hBox)

#     def changeValue(self, value):
#         self.view.rect.doRotate(value)     


class RigFaceSetup(QtGui.QMainWindow):
    def __init__(self):
        super(RigFaceSetup, self).__init__()
        f=open('darkorange.stylesheet', 'r')
        self.styleData = ''
        self.styleData = f.read()
        f.close()
        self.setWindow()

    def setWindow(self):   
        #Setup Style Sheet information

        print str(self.styleData)
        centralWidget = QtGui.QWidget()
        self.testButton = QtGui.QPushButton("Test\nTest\nTest")
        # self.testButton.setStyleSheet(pushCss)

        hBox = QtGui.QGridLayout()
        centralWidget.setLayout(hBox)
        self.setCentralWidget(centralWidget)
        hBox.addWidget(self.testButton)
        self.setStyleSheet(self.styleData)
        # self.view = RigUIControls.RigGraphicsView(self.ColourPickerCircle)
        # self.markerSpawn = RigUIControls.dragItemButton("GuideMarker")
        # self.addWidget(self.testButton)

        # hBox = QtGui.QHBoxLayout()
        # vButtonBox = QtGui.QVBoxLayout()
        # vButtonBox.addWidget(self.markerSpawn)
        # vButtonBox.addWidget(self.testButton)
        # vButtonBox.addStretch(1)

        # hBox.addWidget(self.view)
        # hBox.addLayout(vButtonBox)

        # self.setLayout(hBox)

app = QtGui.QApplication([])
app.setStyle('Plastique')
ex = RigFaceSetup()
ex.show()
app.exec_()
