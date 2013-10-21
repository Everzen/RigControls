#HAPPY FACE RIG

from PyQt4 import QtGui, QtCore

import math
import sys
import Icons

from RigStore import FaceGVCapture

import RigUIControls as rig

class StatusBarMessageLogger(object):
    """
    Simplified interface for setting styled errors into a status bar.

    Designed to be set up with the status bar of the QMainWindow
    """

    def __init__(self, statusBar, styleData):

        self.statusBar = statusBar

        self.errorWidget = QtGui.QLabel(self.statusBar)
        self.errorWidget.setObjectName("errorToolTip")
        self.errorWidget.setStyleSheet(styleData)
        self.errorWidget.hide()

    def error(self, message):
        "Sets the message into the error widget & shows it"

        self.errorWidget.setText("Error: %s" % message)
        self.errorWidget.show()

        stretch = 1
        self.statusBar.addWidget(self.errorWidget, stretch)

    def clear(self):
        "Hides the error widget to clear the status bar"

        self.errorWidget.hide()


class RigFaceSetup(QtGui.QMainWindow):
    """The main Window for the Entire UI.

    The Window has a central widget that is the main Rig QGraphicsView. 

    Currently there are menus and some selection Toolbars docked above it.

    To the left, right and bottom DockWidgets are created and used to bolt on 
    the main buttons and widgets required. RC click on the UI will bring up a
    context menu to hide these DockWidgets and effectly run the program in a
    more space optimising "Expert Mode" 

    Extra features will be added as further DockWidgets that can layer up in 
    Tabs on the areas that they are allowed to dock.

    """
    def __init__(self, styleData):
        super(RigFaceSetup, self).__init__()

        self.setWindowTitle("Facial Rig Builder v1.0")
        # self.setGeometry(50,50, 600, 600)
        # self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.skinTableWidget = None
        self.styleData = styleData
        self.initUI()

    def initUI(self):   

        self.mainWidget = QtGui.QWidget(self)

        # Setup Style Sheet information
        self.setStyleSheet(self.styleData)

        # Set up itemfactory
        itemTypes = [
                rig.GuideMarker, rig.ConstraintEllipse, rig.ConstraintRect,
                rig.ConstraintLine, rig.SkinningEllipse
                ]
        lookupTable = dict( (Type.name, Type) for Type in itemTypes)
        itemFactory = rig.ItemFactory(lookupTable)

        # The statusBar() call creates the status bar
        self.messageLogger = StatusBarMessageLogger(self.statusBar(), self.styleData)
        self.view = rig.RigGraphicsView(
                self,
                self.messageLogger,
                self.styleData,
                itemFactory
                )
        self.view.setStyleSheet('background-color: #888888') #Adding adjustments to the background of the Graphics View

        # File Dialogue to load background image 
        self.imgFileLineEdit = QtGui.QLineEdit('Image File path...')
        self.imgFileLineEdit.setMinimumWidth(200)
        self.imgFileLineEdit.setReadOnly(True)
        self.imgFileSetButton = QtGui.QPushButton("Image")
        self.imgFileSetButton.pressed.connect(lambda: self.view.loadBackgroundImage())

        self.markerSpawn = rig.DragItemButton("GuideMarker")
        # self.showReflectionLineButton = QtGui.QCheckButton("Toggle Reflection Line")
        self.markerScale = QtGui.QSlider(QtCore.Qt.Horizontal)
        # self.markerScale.setTickPosition(1.0)
        self.markerScale.setRange(80, 200)
        self.markerScale.setValue(100)
        self.markerScale.valueChanged.connect(lambda: self.view.setMarkerScaleSlider(self.markerScale.value()))

        # self.connect(self.markerScale , QtCore.SIGNAL( ' valueChanged ( int ) ' ), self.changeValue)
        
        self.reflectGuides = QtGui.QPushButton("Reflect Markers")
        self.reflectGuides.clicked.connect(self.view.reflectGuides)
        # self.testCheckBox = QtGui.QCheckBox("Check me Out")
        self.selectionButton = QtGui.QPushButton("Test Selection")
        self.addWireGroupButton = QtGui.QPushButton("Add Wire Group")
        self.addWireGroupButton.clicked.connect(lambda:  self.view.addWireGroup())
        self.clearGV = QtGui.QPushButton("CLEAR")
        self.clearGV.clicked.connect(lambda:  self.view.clear())
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
        vButtonBox.addWidget(self.clearGV)
        vButtonBox.addStretch(1)

        hBox.addWidget(self.view)
        # hBox.addLayout(vButtonBox)

        self.mainWidget.setLayout(hBox)

        self.setCentralWidget(self.mainWidget)

        # File Menu
        openFace = QtGui.QAction(QtGui.QIcon('exit.png'), 'Open Face', self)        
        openFace.setShortcut('Ctrl+O')
        openFace.setStatusTip('Open a new face')
        openFace.triggered.connect(lambda: self.openFaceRig())

        saveFace = QtGui.QAction(QtGui.QIcon('exit.png'), 'Save Face', self)        
        saveFace.setShortcut('Ctrl+S')
        saveFace.setStatusTip('Save current face')
        saveFace.triggered.connect(lambda: self.saveFaceRig())

        saveFaceAs = QtGui.QAction(QtGui.QIcon('exit.png'), 'Save Face as...', self)        
        saveFaceAs.setShortcut('Ctrl+Shift+S')
        saveFaceAs.setStatusTip('Save current face to a new file')
        saveFaceAs.triggered.connect(lambda: self.moo())

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        # View Menu
        showMarkers = QtGui.QAction('Show Markers', self)  
        showMarkers.setCheckable(True)
        showMarkers.setChecked(True)
        showMarkers.toggled.connect(lambda: self.view.showItem(showMarkers.isChecked(), rig.GuideMarker)) #Adjust this to add hide Reflection Line Functionality

        showNodes = QtGui.QAction('Show Nodes', self)  
        showNodes.setCheckable(True)
        showNodes.setChecked(True)
        showNodes.toggled.connect(lambda: self.view.showItem(showNodes.isChecked(), rig.Node))

        showCurves = QtGui.QAction('Show Curves', self)  
        showCurves.setCheckable(True)
        showCurves.setChecked(True)
        showCurves.toggled.connect(lambda: self.view.showItem(showCurves.isChecked(), rig.RigCurve))

        showPins = QtGui.QAction('Show Pins', self)  
        showPins.setCheckable(True)
        showPins.setChecked(True)
        showPins.toggled.connect(lambda: self.view.showItem(showPins.isChecked(), rig.ControlPin))


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


        self.spaceToolbar = self.addToolBar('')
        space  = QtGui.QLabel("                         ")
        self.spaceToolbar.addSeparator()
        self.spaceToolbar.addWidget(space)
        self.spaceToolbar.addSeparator()
        self.spaceToolbar.setFloatable(False)
        self.spaceToolbar.setMovable(False)

        self.filtersToolbar = self.addToolBar('Filter Options')
        self.selectionFilters = QtGui.QLabel("   Selection Filters   ")

        self.selMarkers = QtGui.QAction(
                QtGui.QIcon('images/GuideMarker_toolbar_active.png'),
                'Select Guide Markers',
                self
                ) 
        self.selMarkers.setCheckable(True)
        self.selMarkers.setChecked(True)
        self.selMarkers.setStatusTip("Toggle guide marker selection")
        self.selMarkers.toggled.connect(lambda: self.selectMarkers(self.selMarkers.isChecked()))

        self.selNodes = QtGui.QAction(QtGui.QIcon('images/Node_toolbar_active.png'), 'Select Nodes', self)
        self.selNodes.setCheckable(True)
        self.selNodes.setChecked(True)
        self.selNodes.setStatusTip("Toggle node selection")
        self.selNodes.toggled.connect(lambda: self.selectNodes(self.selNodes.isChecked()))

        self.filtersToolbar.addWidget(self.selectionFilters)
        self.filtersToolbar.addAction(self.selMarkers)
        self.filtersToolbar.addAction(self.selNodes)
        self.filtersToolbar.addSeparator()

        #Creation DockWidget
        self.dockCreationWidget = QtGui.QDockWidget(self)
        # self.dockCreationWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        # self.dockCreationWidget.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable )
        self.dockCreationWidget.setWindowTitle("Create")
        self.creationWidget = QtGui.QWidget()
        self.dockCreationWidget.setWidget(self.creationWidget)

        creationBox = QtGui.QVBoxLayout()
        self.creationWidget.setLayout(creationBox)
        # self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockCreationWidget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockCreationWidget)


        self.markerCreate = rig.DragItemButton(rig.GuideMarker.name)
        self.wireGroupCreate = rig.WireGroupButton()
        self.wireGroupCreate.clicked.connect(lambda:  self.view.addWireGroup())

        self.ellipseConstraintCreate = rig.DragItemButton(rig.GuideMarker.name)
        self.createConstraints = QtGui.QLabel("Constraints")
        self.createControls = QtGui.QLabel("   Controls")
        self.createSkinning = QtGui.QLabel("Control Skinning")

        self.ellipseConstraintCreate = rig.DragItemButton(rig.ConstraintEllipse.name)
        self.rectConstraintCreate = rig.DragItemButton(rig.ConstraintRect.name)
        self.lineConstraintCreate = rig.DragItemButton(rig.ConstraintLine.name)

        self.arrowControl_four = rig.DragSuperNodeButton("Arrow_4Point")
        self.arrowControl_side = rig.DragSuperNodeButton("Arrow_sidePoint")
        self.arrowControl_upDown = rig.DragSuperNodeButton("Arrow_upDownPoint")

        self.skinningEllipseCreate = rig.DragItemButton(rig.SkinningEllipse.name)

        creationBox.addWidget(self.markerCreate)
        creationBox.addWidget(self.wireGroupCreate)
        creationBox.addWidget(self.createConstraints)
        creationBox.addWidget(self.ellipseConstraintCreate)
        creationBox.addWidget(self.rectConstraintCreate)
        creationBox.addWidget(self.lineConstraintCreate)
        creationBox.addWidget(self.createControls)
        creationBox.addWidget(self.arrowControl_four)
        creationBox.addWidget(self.arrowControl_upDown)
        creationBox.addWidget(self.createSkinning)
        creationBox.addWidget(self.skinningEllipseCreate)
        creationBox.addStretch(1)

        #Options DockWidget
        self.dockOptionsWidget = QtGui.QDockWidget(self)
        # self.dockOptionsWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dockOptionsWidget.setWindowTitle("Control Options")
        # self.dockOptionsWidget.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable )
        # self.dockOptionsWidget.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.optionsWidget = QtGui.QWidget()
        self.dockOptionsWidget.setWidget(self.optionsWidget)

        self.optionsWidget.setLayout(vButtonBox)
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockOptionsWidget)        
        self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockOptionsWidget)        


        #Skinning DockWidget
        skinBox = QtGui.QHBoxLayout()
        skinBox.addStretch(1)

        #Build the Skinning Table
        self.skinTableWidget = rig.SkinTabW()
        self.skinTableWidget.itemChanged.connect(self.updateSkinData)

        self.dockSkinningWidget = QtGui.QDockWidget(self)
        self.dockSkinningWidget.setWindowTitle("Skinning Values")
        # self.skinningWidget = QtGui.QWidget()
        self.dockSkinningWidget.setWidget(self.skinTableWidget)
        # self.dockSkinningWidget.setWidget(self.skinTableWidget)

        # self.skinningWidget .setLayout(skinBox)
        # self.skinningWidget.setWidget(self.skinTableWidget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockSkinningWidget) 
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockCreationWidget)

    def selectMarkers(self,state):
        """Function to filter the selections possible in the Rig Graphics View 

        This function restricts or allows the selection of GuideMarkers (markers)

        Current draw backs are that this is done by running through the GuideMarkers and
        turning off their "selectable" and "moveable" flags. Currently, any new GuideMarkers
        then created to do not have their flags appropriately set, and so might 
        contradict the icon state.
        """ 
        if state:
            self.selMarkers.setIcon(QtGui.QIcon('images/GuideMarker_toolbar_active.png'))
        else:
            self.selMarkers.setIcon(QtGui.QIcon('images/GuideMarker_toolbar_deactive.png'))
        self.view.selectFilter(state, rig.GuideMarker)

    def selectNodes(self,state):
        """Function to filter the selections possible in the Rig Graphics View 

        This function restricts or allows the selection of Nodes

        Current draw backs are that this is done by running through the nodes and
        turning off their "selectable" and "moveable" flags. Currently, any new nodes
        then created to do not have their flags appropriately set, and so might 
        contradict the icon state.
        """
        if state:
            self.selNodes.setIcon(QtGui.QIcon('images/Node_toolbar_active.png'))
        else:
            self.selNodes.setIcon(QtGui.QIcon('images/Node_toolbar_deactive.png'))
        self.view.selectFilter(state, rig.Node)

    def openFaceRig(self):
        """Function to load in a stored XML file of face Rig Data"""
        xMLStructure = FaceGVCapture(self.view, self.messageLogger)
        xMLStructure.setXMLFile("faceFiles/test.xml")
        xMLStructure.read()

    def saveFaceRig(self):
        """Function to save the entire Rig Graphics View scene out to an XML File"""
        xMLStructure = FaceGVCapture(self.view, self.messageLogger)
        xMLStructure.setXMLFile("faceFiles/test.xml")
        xMLStructure.store()


    def updateSkinData(self, item):
        """Function that simply calls the skinning table to update"""
        self.skinTableWidget.updateSkinning(item)

    def itemTest(self):
        """Random Test funciton to see if things get called"""
        print "moo"


def main():

    stylesheet = 'darkorange.stylesheet'
    try:
        # Read style sheet information
        with open(stylesheet, 'r') as handle:
            styleData = handle.read()
    except IOError:
        sys.stderr.write('Error - Unable to find stylesheet \'%s\'\n' % stylesheet)
        return 1

    app = QtGui.QApplication([])
    app.setStyle('Plastique')
    ex = RigFaceSetup(styleData)
    ex.show()
    app.exec_()

    return 0

if __name__ == "__main__":
    sys.exit(main())

