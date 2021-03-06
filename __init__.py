#HAPPY FACE RIG

#Import what is needed for launching within the Maya Window
import maya.OpenMayaUI as omui
from PySide import QtGui, QtCore
from shiboken import wrapInstance #Converts pointers to Python Objects

import math
import sys
import Icons
import os

from RigStore import FaceGVCapture
from Widgets import ControlScale, DragItemButton, SkinTabW, SceneLinkServoTabW
from dataProcessor import DataProcessor, DataServoProcessor, DataBundle, DataServoBundle
from expressionCapture import ExpressionCaptureProcessor, ExpressionFaceState, ExpressionItemState



import RigUIControls as rig

from mayaData import MayaData
from MaestroServo import MaestroSerialServo
#################################################################################################
#Function to return Mayas main Window QtWidget so we can parent our UI to it.

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

#################################################################################################



#################################################################################################

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
    def __init__(self, styleData, dataProcessor, expressionCaptureProcessor, parent = None):
        super(RigFaceSetup, self).__init__(parent)

        self.setWindowTitle("Facial Rig Builder v1.0")
        # self.setFocusPolicy(QtCore.Qt.StrongFocus) #Test what this does for bringing focus to the window to try and stop maya shortcuts! 
        # self.setGeometry(50,50, 600, 600)
        # self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.faceSaveFile = None
        self.skinTableWidget = None
        self.styleData = styleData
        self.dataProcessor = dataProcessor
        self.dataProcessor.setWindow(self) #Ensure that the processor is aware of the window Widget
        self.expressionCaptureProcessor = expressionCaptureProcessor #Record the expressionCaptureProcessor
        imagePath = os.path.dirname(os.path.realpath(__file__))
        self.imagePath = imagePath.replace("\\", "/") #Convert everything across to / for css files. Apparently this is ugly, but cannot get os.path and posixpath to work
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

        self.controlScale = ControlScale() #A control scale is setup early and passed to the rigView - the appropriate Slider is added later

        self.view = rig.RigGraphicsView(
                self,
                self.messageLogger,
                self.styleData,
                self.dataProcessor,
                self.expressionCaptureProcessor,
                itemFactory,
                self.controlScale
                )
        self.view.setStyleSheet('background-color: #888888') #Adding adjustments to the background of the Graphics View

        hBox = QtGui.QHBoxLayout()
        hBox.addWidget(self.view)

        self.mainWidget.setLayout(hBox)
        self.setCentralWidget(self.mainWidget)
        # self.setCentralWidget(self.mainWidget)


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
        saveFaceAs.triggered.connect(lambda: self.saveFaceAsRig())

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

        self.reflectGuideMarkers = QtGui.QAction("Reflect Markers",self)
        self.reflectGuideMarkers.triggered.connect(self.view.reflectGuides)
        self.reflectGuideMarkers.setStatusTip('Reflect Guide Markers about the Reflection Line')

        self.reflectControlItems = QtGui.QAction("Reflect Control Items",self)
        self.reflectControlItems.triggered.connect(self.view.reflectControlItems)
        self.reflectControlItems.setStatusTip('Reflect Control Items about the Reflection Line')

        self.clearFace = QtGui.QAction("Clear All",self)
        self.clearFace.triggered.connect(lambda:  self.clearHappyFace())  
        self.clearFace.setStatusTip('Clears all Items from the Face Rig')

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

        actionMenu = menubar.addMenu('&Action')
        actionMenu.addAction(self.reflectGuideMarkers)
        actionMenu.addAction(self.reflectControlItems)
        actionMenu.addSeparator()
        actionMenu.addAction(self.clearFace)


        self.createDataSceneControl = QtGui.QAction("Create " + self.dataProcessor.getAppName() +" Control",self)
        self.createDataSceneControl.triggered.connect(self.createSceneControl)
        self.createDataSceneControl.setStatusTip('Create a Locator with attributes representing all the control movements on the face setup')

        dataMenu = menubar.addMenu('&Data')
        dataMenu.addAction(self.createDataSceneControl)
        # dataMenu.addSeparator()
        # dataMenu.addAction(self.clearFace)

        self.quickToolbar = self.addToolBar('Quick Tools')
        space  = QtGui.QLabel("                          ")
        self.selectionFilters = QtGui.QLabel("   Selection Filters   ")

        self.selMarkers = QtGui.QAction(
                QtGui.QIcon(self.imagePath + '/images/GuideMarker_toolbar_active.png'),
                'Select Guide Markers',
                self
                ) 
        self.selMarkers.setCheckable(True)
        self.selMarkers.setChecked(True)
        self.selMarkers.setStatusTip("Toggle guide marker selection")
        self.selMarkers.toggled.connect(lambda: self.selectMarkers(self.selMarkers.isChecked()))

        self.selNodes = QtGui.QAction(QtGui.QIcon(self.imagePath + '/images/Node_toolbar_active.png'), 'Select Nodes', self)
        self.selNodes.setCheckable(True)
        self.selNodes.setChecked(True)
        self.selNodes.setStatusTip("Toggle node selection")
        self.selNodes.toggled.connect(lambda: self.selectNodes(self.selNodes.isChecked()))

        self.controlScaleLbl = QtGui.QLabel("   Control Scale  ")
        self.controlScaleSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        # self.controlScaleSlider.setTickPosition(1.0)
        self.controlScaleSlider.setRange(80, 200)
        self.controlScaleSlider.setValue(100)
        self.controlScaleSlider.valueChanged.connect(lambda: self.controlScale.update())
        self.controlScale.setSlider(self.controlScaleSlider)
        self.controlScale.setScene(self.view.scene())


        self.scaleSameItems = QtGui.QCheckBox("Scale Matching Items")
        self.scaleSameItems.clicked.connect(lambda: self.controlScale.setScaleSameItems(self.scaleSameItems.isChecked()))

        # File Dialogue to load background image 
        self.imgFileLineEdit = QtGui.QLineEdit('Image File path...')
        self.imgFileLineEdit.setMinimumWidth(200)
        self.imgFileLineEdit.setReadOnly(True)
        self.imgFileSetButton = QtGui.QPushButton("Set Background Image")
        self.imgFileSetButton.pressed.connect(lambda: self.view.loadBackgroundImage())

        self.quickToolbar.addWidget(space)
        self.quickToolbar.addWidget(self.selectionFilters)
        self.quickToolbar.addAction(self.selMarkers)
        self.quickToolbar.addAction(self.selNodes)
        self.quickToolbar.addWidget(self.controlScaleLbl)
        self.quickToolbar.addWidget(self.controlScaleSlider)
        self.quickToolbar.addWidget(self.scaleSameItems)
        self.quickToolbar.addWidget(self.imgFileLineEdit)
        self.quickToolbar.addWidget(self.imgFileSetButton)

        self.quickToolbar.addSeparator()

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


        self.markerCreate = DragItemButton(rig.GuideMarker.name)
        self.wireGroupCreate = rig.WireGroupButton()
        self.wireGroupCreate.clicked.connect(lambda:  self.view.addWireGroup())

        self.ellipseConstraintCreate = rig.DragItemButton(rig.GuideMarker.name)
        self.createConstraints = QtGui.QLabel("Constraints")
        self.createControls = QtGui.QLabel("   Controls")
        self.createSkinning = QtGui.QLabel("Control Skinning")
        self.createExpression = QtGui.QLabel("Expression State")

        self.ellipseConstraintCreate = rig.DragItemButton(rig.ConstraintEllipse.name)
        self.rectConstraintCreate = rig.DragItemButton(rig.ConstraintRect.name)
        self.lineConstraintCreate = rig.DragItemButton(rig.ConstraintLine.name)

        self.arrowControl_four = rig.DragSuperNodeButton("Arrow_4Point")
        self.arrowControl_side = rig.DragSuperNodeButton("Arrow_sidePoint")
        self.arrowControl_upDown = rig.DragSuperNodeButton("Arrow_upDownPoint")

        self.skinningEllipseCreate = rig.DragItemButton(rig.SkinningEllipse.name)

        self.expressionCreate = rig.DragItemButton(rig.ExpressionStateNode.name)


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
        creationBox.addWidget(self.createExpression)
        creationBox.addWidget(self.expressionCreate)
        creationBox.addStretch(1)

        #Skinning DockWidget
        # skinBox = QtGui.QHBoxLayout()
        # skinBox.addStretch(1)



        self.dockDataTablesWidget = QtGui.QDockWidget(self)
        self.dockDataTablesWidget.setWindowTitle("Data Tables")
        # self.skinningWidget = QtGui.QWidget()
        self.dataTabsWidget = QtGui.QTabWidget()
        
        tabSkinning = QtGui.QWidget()
        layoutSkinning = QtGui.QVBoxLayout(tabSkinning)
        self.dataTabsWidget.addTab(tabSkinning, "Skinning Values")
        #Build the Skinning Table
        self.skinTableWidget = SkinTabW()
        self.skinTableWidget.itemChanged.connect(self.updateSkinData)
        layoutSkinning.addWidget(self.skinTableWidget)


        tabNodeLinks = QtGui.QWidget()
        layoutNodeLinks = QtGui.QVBoxLayout(tabNodeLinks)
        self.dataTabsWidget.addTab(tabNodeLinks, "Node and Servo Links")
        #Build the Skinning Table
        self.nodeLinksTableWidget = SceneLinkServoTabW(self.styleData) #Replace this when the correct data table is actually written! 
        # self.nodeLinksTableWidget.itemChanged.connect(self.updateSceneLinkOutputData) #Function called to see which Table item has been changed, and adjust the appropriate output
        self.nodeLinksTableWidget.setDataProcessor(self.dataProcessor)
        self.nodeLinksTableWidget.populate()
        self.updateNodeLinksButton = QtGui.QPushButton("Update")
        self.updateNodeLinksButton.pressed.connect(lambda: self.nodeLinksTableWidget.populate()) 

        layoutNodeLinks.addWidget(self.nodeLinksTableWidget)
        layoutNodeLinks.addWidget(self.updateNodeLinksButton)

        self.dockDataTablesWidget.setWidget(self.dataTabsWidget) #Now set the Tab Widget to be the main Widget for this bottom Dock
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockDataTablesWidget) 
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
            self.selMarkers.setIcon(QtGui.QIcon(self.imagePath + '/images/GuideMarker_toolbar_active.png'))
        else:
            self.selMarkers.setIcon(QtGui.QIcon(self.imagePath + '/images/GuideMarker_toolbar_deactive.png'))
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
            self.selNodes.setIcon(QtGui.QIcon(self.imagePath + '/images/Node_toolbar_active.png'))
        else:
            self.selNodes.setIcon(QtGui.QIcon(self.imagePath + '/images/Node_toolbar_deactive.png'))
        self.view.selectFilter(state, rig.Node)

    def openFaceRig(self):
        """Function to load in a stored XML file of face Rig Data"""
        xMLStructure = FaceGVCapture(self.view, self.messageLogger, self.dataProcessor, self.expressionCaptureProcessor)
        faceFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open Happy Face File', 'faceFiles', filter = "Face XML files (*.xml)")[0]
        if faceFileName != "": # A Valid File has been selected from the File Diaglogue
            self.faceSaveFile = faceFileName
            xMLStructure.setXMLFile(faceFileName)
            xMLStructure.read()
        self.nodeLinksTableWidget.populate() #Redraw the nodelink data Table, so that all the data is updated to the new loaded faceRig
        self.skinTableWidget.populate() ##Redraw the skin data Table, so that all the data is updated to the new loaded faceRig

    def saveFaceRig(self):
        """Function to save the entire Rig Graphics View scene out to an XML File"""
        xMLStructure = FaceGVCapture(self.view, self.messageLogger, self.dataProcessor, self.expressionCaptureProcessor)
        isValidSaveFile = False
        if self.faceSaveFile: # Check a Face File has been set and exists
            if os.path.isfile(self.faceSaveFile): isValidSaveFile = True

        if isValidSaveFile:  
            xMLStructure.setXMLFile(self.faceSaveFile)
            xMLStructure.store()
        else:
            self.faceSaveFile = QtGui.QFileDialog.getSaveFileName(self, 'Save Happy Face File', 'faceFiles', filter = "Face XML files (*.xml)")[0]
            if self.faceSaveFile != "": 
                xMLStructure.setXMLFile(self.faceSaveFile)
                xMLStructure.store()

    def saveFaceAsRig(self):
        """Function to save the entire Rig Graphics View scene out to an XML File"""
        xMLStructure = FaceGVCapture(self.view, self.messageLogger, self.dataProcessor,self.expressionCaptureProcessor)
        faceFileName = QtGui.QFileDialog.getSaveFileName(self, 'Save Happy Face File As...', 'faceFiles', filter = "Face XML files (*.xml)")[0]
        if faceFileName != "": 
            self.faceSaveFile = faceFileName
            xMLStructure.setXMLFile(self.faceSaveFile)
            xMLStructure.store()

    def updateSkinData(self, item):
        """Function that simply calls the skinning table to update"""
        self.skinTableWidget.updateSkinning(item)

    def updateSceneLinkOutputData(self, item):
        """Function that simply calls the skinning table to update"""
        self.nodeLinksTableWidget.updateSceneLinkOutputData(item)

    def itemTest(self):
        """Random Test funciton to see if things get called"""
        print "moo"

    def createSceneControl(self):
        """Check to see if there is a scene Controller, and if there is not, then build one"""
        #Check to see if there is an established controller already setup
        sceneControllerName, ok = QtGui.QInputDialog.getText(
                self, self.dataProcessor.getAppName() + ' Scene Controller Name',
                'Please Enter a unique Scene Contoller Name:'
                )
        while not self.dataProcessor.isSceneControllerNameUnique(sceneControllerName):
            sceneControllerName, ok = QtGui.QInputDialog.getText(
                    self, self.dataProcessor.getAppName() + ' Scene Controller Name',
                    'Sadly that name already exists in the current Scene. Please Enter a unique Scene Contoller Name:'
                    )
        if ok:
            print "Name is : " + str(sceneControllerName) + " " + str(self.dataProcessor.getSceneControl())
            if self.dataProcessor.getSceneControl() != None and self.dataProcessor.sceneControllerExists() :
                reply = QtGui.QMessageBox.question(self, "Scene Controller Conflict", 'There already seems to be a controller in place called : ' + self.dataProcessor.getSceneControl() + '. Do you want to override it with a new controller?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.dataProcessor.createSceneControl(sceneControllerName)
                    self.dataProcessor.setSceneControl(sceneControllerName)
            else:
                self.dataProcessor.createSceneControl(sceneControllerName)
                self.dataProcessor.setSceneControl(sceneControllerName)

    def clearHappyFace(self):
        """A Function to clear the face from the RigGraphicsView, but also reset the dataTables"""
        self.view.clear(query = True)
        self.nodeLinksTableWidget.populate() #Redraw the nodelink data Table, so that all the data cleared out
        self.skinTableWidget.setSuperNode(None) #Redraw the skin data Table, so that all the data is cleared out
        self.skinTableWidget.populate()
        self.expressionCaptureProcessor.clearAll() #Make sure that all the expressions are cleared out along with faceSnapShot


    def closeEvent(self, event):
        """Function to close down the Window and clean up connections such as any Servo based connections"""
        if type(self.dataProcessor) == DataServoProcessor: #We have a servo processor, so shut down any serial ports
            self.dataProcessor.getServoAppData().close()
        print "Happy Face is shutting down..... "

# def main():

#     stylesheet = 'darkorange.stylesheet'
#     try:
#         # Read style sheet information
#         with open(stylesheet, 'r') as handle:
#             styleData = handle.read()
#     except IOError:
#         sys.stderr.write('Error - Unable to find stylesheet \'%s\'\n' % stylesheet)
#         return 1

#     app = QtGui.QApplication([])
#     app.setStyle('Plastique')
#     ex = RigFaceSetup(styleData)
#     ex.show()
#     app.exec_()

#     return 0

# if __name__ == "__main__":
#     sys.exit(main())

def main():
    # stylesheet = 'darkorange.stylesheet'
    stylesheet = (os.path.dirname(os.path.realpath(__file__))) + '/darkorange.stylesheet'
    try:
        # Read style sheet information
        with open(stylesheet, 'r') as handle:
            styleData = handle.read()
    except IOError:
        sys.stderr.write('Error - Unable to find stylesheet \'%s\'\n' % stylesheet)
        return 1

    #Create DataProcessor for the rig and use the DataBundle Class to determine how it will behave.
    # rigProcessor = DataProcessor(MayaData()) 
    rigProcessor = DataServoProcessor(MayaData(),MaestroSerialServo()) #Setup the data processor for working Maya and the Pololu Maestro Server information 
    expressionCaptureProcessor = ExpressionCaptureProcessor()
    happyFaceUI = RigFaceSetup(styleData, rigProcessor,expressionCaptureProcessor, parent = maya_main_window())
    # happyFaceUI = RigFaceSetup(styleData)
    # happyFaceUI.setWindowFlags(QtCore.Qt.Tool)
    happyFaceUI.show()
    return 0

# if __name__ == "__main__":
#     print "launching......"
#     launch()


#     stylesheet = 'darkorange.stylesheet'
#     try:
#         # Read style sheet information
#         with open(stylesheet, 'r') as handle:
#             styleData = handle.read()
#     except IOError:
#         sys.stderr.write('Error - Unable to find stylesheet \'%s\'\n' % stylesheet)
#         return 1




print "launching Happy Face......"

main()