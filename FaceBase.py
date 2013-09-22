#HAPPY FACE

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
        # self.setGeometry(50,50, 600, 600)
        # self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
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
        self.view = RigUIControls.RigGraphicsView()
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
        self.markerScale.setRange(60, 200)
        self.markerScale.setValue(100)
        self.markerScale.valueChanged.connect(lambda: self.view.setMarkerScale(self.markerScale.value()))

        # self.connect(self.markerScale , QtCore.SIGNAL( ' valueChanged ( int ) ' ), self.changeValue)
        
        self.reflectGuides = QtGui.QPushButton("Reflect Markers")
        self.reflectGuides.clicked.connect(self.view.reflectGuides)
        # self.testCheckBox = QtGui.QCheckBox("Check me Out")
        self.selectionButton = QtGui.QPushButton("Test Selection")
        self.addWireGroupButton = QtGui.QPushButton("Add Wire Group")
        self.addWireGroupButton.clicked.connect(lambda:  self.view.addWireGroup())
        # self.selectionButton.pressed.connect(lambda: self.view.printSelection()) #Adjust this to add hide Reflection Line Functionality


        hBox = QtGui.QHBoxLayout()
        vButtonBox = QtGui.QVBoxLayout()
        hImageBox = QtGui.QHBoxLayout()
        hImageBox.addWidget(self.imgFileLineEdit)
        hImageBox.addWidget(self.imgFileSetButton)

        vButtonBox.addLayout(hImageBox)
        vButtonBox.addWidget(self.markerSpawn)
        vButtonBox.addWidget(self.markerScale)
        vButtonBox.addWidget(self.reflectGuides)
        # vButtonBox.addWidget(self.testCheckBox)
        vButtonBox.addWidget(self.selectionButton)
        vButtonBox.addWidget(self.addWireGroupButton)
        vButtonBox.addStretch(1)

        hBox.addWidget(self.view)
        hBox.addLayout(vButtonBox)

        self.mainWidget.setLayout(hBox)
        self.setCentralWidget(self.mainWidget)

        #File Menu

        openFace = QtGui.QAction(QtGui.QIcon('exit.png'), 'Open Face', self)        
        openFace.setShortcut('Ctrl+O')
        openFace.setStatusTip('Exit application')
        openFace.triggered.connect(lambda: self.moo())

        saveFace = QtGui.QAction(QtGui.QIcon('exit.png'), 'Save Face', self)        
        saveFace.setShortcut('Ctrl+S')
        saveFace.setStatusTip('Exit application')
        saveFace.triggered.connect(lambda: self.moo())

        saveFaceAs = QtGui.QAction(QtGui.QIcon('exit.png'), 'Save Face as...', self)        
        saveFaceAs.setShortcut('Ctrl+Shift+S')
        saveFaceAs.setStatusTip('Exit application')
        saveFaceAs.triggered.connect(lambda: self.moo())

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        #View Menu

        showMarkers = QtGui.QAction('Show Markers', self)  
        showMarkers.setCheckable(True)
        showMarkers.setChecked(True)
        showMarkers.toggled.connect(lambda: self.view.showItem(showMarkers.isChecked(), RigUIControls.GuideMarker)) #Adjust this to add hide Reflection Line Functionality

        showNodes = QtGui.QAction('Show Nodes', self)  
        showNodes.setCheckable(True)
        showNodes.setChecked(True)
        showNodes.toggled.connect(lambda: self.view.showItem(showNodes.isChecked(), RigUIControls.Node)) 

        showCurves = QtGui.QAction('Show Curves', self)  
        showCurves.setCheckable(True)
        showCurves.setChecked(True)
        showCurves.toggled.connect(lambda: self.view.showItem(showCurves.isChecked(), RigUIControls.RigCurve)) 

        showPins = QtGui.QAction('Show Pins', self)  
        showPins.setCheckable(True)
        showPins.setChecked(True)
        showPins.toggled.connect(lambda: self.view.showItem(showPins.isChecked(), RigUIControls.ControlPin)) 


        viewReflectionLine = QtGui.QAction('&Show Reflection Line', self)  
        viewReflectionLine.setCheckable(True)
        viewReflectionLine.setChecked(True)
        viewReflectionLine.toggled.connect(lambda: self.view.setShowReflectionLine(viewReflectionLine.isChecked()))

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFace)
        fileMenu.addAction(saveFace)
        fileMenu.addAction(saveFaceAs)
        fileMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(showMarkers)
        viewMenu.addAction(showNodes)
        viewMenu.addAction(showCurves)
        viewMenu.addAction(showPins)
        viewMenu.addSeparator()
        viewMenu.addAction(viewReflectionLine)

        self.toolbar = self.addToolBar('Key Options')
        
        # self.selectionFilters = QtGui.QAction(QtGui.QIcon('images/SelectionFilters_toolbar.png'),'Selection Filters', self) 
        # self.selectionFilters.setEnabled(False)
        self.selectionFilters = QtGui.QLabel("   Selection Filters   ")


        self.selMarkers = QtGui.QAction(QtGui.QIcon('images/GuideMarker_toolbar_active.png'), 'Select Markers', self) 
        self.selMarkers.setCheckable(True)
        self.selMarkers.setChecked(True)
        self.selMarkers.toggled.connect(lambda: self.selectMarkers(self.selMarkers.isChecked()))

        self.selNodes = QtGui.QAction(QtGui.QIcon('images/Node_toolbar_active.png'), 'Select Markers', self) 
        self.selNodes.setCheckable(True)
        self.selNodes.setChecked(True)
        self.selNodes.toggled.connect(lambda: self.selectNodes(self.selNodes.isChecked()))

        self.toolbar.addWidget(self.selectionFilters)
        self.toolbar.addAction(self.selMarkers)
        self.toolbar.addAction(self.selNodes)
        self.toolbar.addSeparator()

        self.statusBar()

    def moo(self):
        print "mr Moo"

    def selectMarkers(self,state):
        if state:
            self.selMarkers.setIcon(QtGui.QIcon('images/GuideMarker_toolbar_active.png'))
        else:
            self.selMarkers.setIcon(QtGui.QIcon('images/GuideMarker_toolbar_deactive.png'))
        self.view.selectFilter(state, RigUIControls.GuideMarker)

    def selectNodes(self,state):
        if state:
            self.selNodes.setIcon(QtGui.QIcon('images/Node_toolbar_active.png'))
        else:
            self.selNodes.setIcon(QtGui.QIcon('images/Node_toolbar_deactive.png'))
        self.view.selectFilter(state, RigUIControls.Node)

app = QtGui.QApplication([])
app.setStyle('Plastique')
ex = RigFaceSetup()
ex.show()
app.exec_()
