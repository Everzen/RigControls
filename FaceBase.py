
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
        
        #File Dialogue to load background image 
        self.imgFileLineEdit = QtGui.QLineEdit('Image File path...')
        self.imgFileLineEdit.setMinimumWidth(200)
        self.imgFileLineEdit.setReadOnly(True)
        self.imgFileSetButton = QtGui.QPushButton("Image")
        self.imgFileSetButton.pressed.connect(lambda: self.view.setBackgroundImage())

        self.markerSpawn = RigUIControls.DragItemButton("GuideMarker")
        # self.showReflectionLineButton = QtGui.QCheckButton("Toggle Reflection Line")
        self.markerScale = QtGui.QSlider(QtCore.Qt.Horizontal)
        # self.markerScale.setTickPosition(1.0)
        self.markerScale.setRange(10, 300)
        self.markerScale.setValue(100)
        self.markerScale.valueChanged.connect(lambda: self.view.setMarkerScale(self.markerScale.value()))

        # self.connect(self.markerScale , QtCore.SIGNAL( ' valueChanged ( int ) ' ), self.changeValue)
        
        self.reflectGuides = QtGui.QPushButton("Reflect Markers")
        self.reflectGuides.clicked.connect(self.view.reflectGuides)
        self.testCheckBox = QtGui.QCheckBox("Check me Out")



        hBox = QtGui.QHBoxLayout()
        vButtonBox = QtGui.QVBoxLayout()
        hImageBox = QtGui.QHBoxLayout()
        hImageBox.addWidget(self.imgFileLineEdit)
        hImageBox.addWidget(self.imgFileSetButton)

        vButtonBox.addLayout(hImageBox)
        vButtonBox.addWidget(self.markerSpawn)
        vButtonBox.addWidget(self.markerScale)
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

        viewMarkerIDs = QtGui.QAction('&Show Marker IDs', self)  
        viewMarkerIDs.setCheckable(True)
        viewMarkerIDs.setChecked(True)
        viewMarkerIDs.toggled.connect(lambda: self.view.setShowMarkerID(viewMarkerIDs.isChecked())) #Adjust this to add hide Reflection Line Functionality

        viewReflectionLine = QtGui.QAction('&Show Reflection Line', self)  
        viewReflectionLine.setCheckable(True)
        viewReflectionLine.setChecked(True)
        viewReflectionLine.toggled.connect(lambda: self.view.setShowReflectionLine(viewReflectionLine.isChecked()))

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(viewMarkerIDs)
        viewMenu.addAction(viewReflectionLine)

        self.statusBar()


app = QtGui.QApplication([])
app.setStyle('Plastique')
ex = RigFaceSetup()
ex.show()
app.exec_()
