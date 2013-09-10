
from PyQt4 import QtGui, QtCore
import RigUIControls
import math
import sys
import Icons

class RigFaceSetup(QtGui.QMainWindow):
# class RigFaceSetup(QtGui.QMainWindow):
    def __init__(self):
        super(RigFaceSetup, self).__init__()
        self.setWindowTitle("Facial Rig Builder v1.0")
        self.setGeometry(50,50, 600, 600)
        self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.initUI()
       
       
    def initUI(self):   
        self.mainWidget = QtGui.QWidget(self)
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

        self.mainWidget.setLayout(hBox)
        self.setCentralWidget(self.mainWidget)

        #Setup UI Menu Actions
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        viewReflectionLine = QtGui.QAction('&Show Reflection Line', self)  
        viewReflectionLine.setCheckable(True)
        viewReflectionLine.setChecked(True)
        viewReflectionLine.toggled.connect(QtGui.qApp.quit) #Adjust this to add hide Reflection Line Functionality

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(viewReflectionLine)

        self.statusBar()

    def changeValue(self, value):
        self.view.rect.doRotate(value)     


app = QtGui.QApplication([])
app.setStyle('Plastique')
ex = RigFaceSetup()
ex.show()
app.exec_()
