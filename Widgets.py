
from PySide import QtCore, QtGui
import sys
import os
import posixpath #This is imported for forcing paths to include "/" on windows - for passing paths to css

from ControlItems import *

class WidgetsError(Exception):
    pass

class ItemFactoryError(WidgetsError):
    pass

class ItemFactory(object):
    """Factory for creating various widgets according to the lookup table"""

    def __init__(self, lookupTable):
        self.lookupTable = lookupTable

    def create(self, itemName):
        """Check our lookup table for the constructor and return constructed object.

        Else throw a ItemFactoryError

        """

        try:
            Item = self.lookupTable[str(itemName)]
        except KeyError:
            raise ItemFactoryError("Unable to find contructor for '%s' item" % itemName)

        return Item()


class WireGroupButton(QtGui.QPushButton):
    """Subclassed QPushButton to build a WireGroup from a selection Guide Markers

    Also uses CSS to control the image being displayed under different states
    such as mousePressEvent, mouseMoveEvent and mouseReleaseEvent

    """
    def __init__(self, parent=None):
        super(WireGroupButton, self).__init__(parent)
        # self.setMouseTracking(True)
        self.itemName = "WireGroup"
        self.imageFile = None
        self.imageCSS = None
        self.initUI()

    def initUI(self):
        """Check the images folder to see if there is an appropriate image to load""" 
        self.setStyleSheet(self.validImageFile())
        self.pixmap = QtGui.QPixmap(self.imageFile)

    def leaveEvent(self,event):
        # QtGui.QPushButton.mouseReleaseEvent(self, event)
        self.setDown(False)
        self.setStyleSheet(self.validImageFile())

    def mousePressEvent(self,event):
        self.setDown(True)
        self.setStyleSheet(self.validImageFile(state = "pressed"))
        return QtGui.QPushButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self,event):
        QtGui.QPushButton.mouseReleaseEvent(self, event)
        self.setDown(False)
        self.setStyleSheet(self.validImageFile())
        return QtGui.QPushButton.mouseReleaseEvent(self, event)
    
    def mouseMoveEvent(self, event):
        if self.hitButton(event.pos()):
            self.setDown(True)
            self.setStyleSheet(self.validImageFile(state = "pressed"))
        else:
            self.setDown(False)
            self.setStyleSheet(self.validImageFile())

    def validImageFile(self,state=""):
        imageDir = os.path.dirname(os.path.realpath(__file__))
        CSSimageDir = imageDir.replace("\\", "/") #Convert everything across to / for css files. Apparently this is ugly, but cannot get os.path and posixpath to work
        imageFile = ""
        imageFileCss = ""
        if state == "hover":
            imageFile = CSSimageDir + '/images/' + self.itemName + '_Hover.png'
        elif state == "pressed":
            imageFile = CSSimageDir + '/images/' + self.itemName + '_Pressed.png'
        else:
            imageFile = CSSimageDir + '/images/' + self.itemName + '.png'

        imageFileCss = 'image: url(' + imageFile + ');'
        if os.path.exists(os.path.normpath(imageFile)): #create icon and add to button
            self.imageFile = imageFile
            return imageFileCss
        else:
            print "WARNING : No valid image file has been found"

    def sizeHint(self):
        return self.pixmap.size()



class DragItemButton(QtGui.QPushButton):
    """Subclassed QPushButton to enable dragging in of nearly all control items

    These buttons are used with different input "itemName" in order to build an instance
    of the input class. 

    This button starts a drag event that is then checked and handled by the RigGraphicsView

    Items built this way inclide GuideMarkers, ConstraintItems, SkinningItem

    Also uses CSS to control the image being displayed under different states
    such as mousePressEvent, mouseMoveEvent and mouseReleaseEvent

    """
    def __init__(self, itemName, parent=None):
        super(DragItemButton, self).__init__(parent)
        self.setMouseTracking(True)
        self.itemName = itemName
        self.imageFile = None
        self.imageCSS = None
        self.initUI()

    def initUI(self):
        """Check the images folder to see if there is an appropriate image to load""" 
        self.setStyleSheet(self.validImageFile())
        self.pixmap = QtGui.QPixmap(self.imageFile)

    def leaveEvent(self,event):
        self.setDown(False)
        self.setStyleSheet(self.validImageFile())

    def mousePressEvent(self,event):
        self.setDown(True)
        self.setStyleSheet(self.validImageFile(state = "pressed"))

    def mouseReleaseEvent(self,event):
        self.setDown(False)
        self.setStyleSheet(self.validImageFile())

    def validImageFile(self,state=""):
        imageDir = os.path.dirname(os.path.realpath(__file__))
        CSSimageDir = imageDir.replace("\\", "/") #Convert everything across to / for css files. Apparently this is ugly, but cannot get os.path and posixpath to work
        imageFile = ""
        imageFileCss = ""
        if state == "hover":
            imageFile = CSSimageDir + '/images/' + self.itemName + '_Hover.png'
        elif state == "pressed":
            imageFile = CSSimageDir + '/images/' + self.itemName + '_Pressed.png'
        else:
            imageFile = CSSimageDir + '/images/' + self.itemName + '.png'

        imageFileCss = 'image: url(' + imageFile + ');'
        if os.path.exists(os.path.normpath(imageFile)): #create icon and add to button
            self.imageFile = imageFile
            return imageFileCss
        else:
            print "WARNING : No valid image file has been found"


    def sizeHint(self):
        return self.pixmap.size()


    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton:
            return
        mimeData = QtCore.QMimeData()
        mimeData.setData("text/plain", str(self.itemName))
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        # print "start drag text : " + str(self.itemName)
        dropAction = drag.start(QtCore.Qt.MoveAction)



class DragSuperNodeButton(DragItemButton):
    """Subclassed QPushButton to enable dragging in of SuperNodeGroups 

    It has been subclassed from the the DragItemButton to add extra functionality
    for dealing with different SuperNode draw states (different pointy arrow symbols) 

    This button starts a drag event that is then checked and handled by the RigGraphicsView

    Also uses CSS to control the image being displayed under different states
    such as mousePressEvent, mouseMoveEvent and mouseReleaseEvent

    """
    def __init__(self, form, parent=None):
        self.form = str(form)
        DragItemButton.__init__(self,"SuperNode")
        

    def validImageFile(self,state=""):
        imageDir = os.path.dirname(os.path.realpath(__file__))
        CSSimageDir = imageDir.replace("\\", "/") #Convert everything across to / for css files. Apparently this is ugly, but cannot get os.path and posixpath to work
        imageFile = ""
        imageFileCss = ""
        if state == "hover":
            imageFile = CSSimageDir + '/images/' + self.form + '_Hover.png'
        elif state == "pressed":
            imageFile = CSSimageDir + '/images/' + self.form + '_Pressed.png'
        else:
            imageFile = CSSimageDir + '/images/' + self.form + '.png'

        imageFileCss = 'image: url(' + imageFile + ');'
        if os.path.exists(os.path.normpath(imageFile)): #create icon and add to button
            self.imageFile = imageFile
            return imageFileCss
        else:
            print "WARNING : No valid image file has been found"


    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton:
            return
        mimeData = QtCore.QMimeData()
        mimeData.setData("text/plain", str(self.itemName) + "_" + self.form)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        # print "start drag text : " + str(self.itemName)
        dropAction = drag.start(QtCore.Qt.MoveAction)




class SkinTabW(QtGui.QTableWidget):
    """Class to subclass QTableWidget to give us control over how we handle
    the skinning data on a SuperNode

    If a SuperNode is selected then the populate() method is called in this 
    class to fill the contents of the UI bottom docking Skinning Table

    """
    def __init__(self, parent = None):
        super(SkinTabW, self).__init__(parent)
        self.superNode = None

        self.headers = []
        self.headers.append("  Super Node Controller  ")
        self.headers.append("  Node Wire Group  ")
        self.headers.append("  Node Index  ")
        self.headers.append("  Skin Value  ")
        self.populate()

    def getSuperNode(self):
        return self.superNode

    def setSuperNode(self, superNode):
        self.superNode = superNode
        self.populate()

    def populate(self):
        if self.superNode:
            self.clear()
            self.setColumnCount(4)
            self.setHorizontalHeaderLabels(self.headers)
            self.setRowCount(len(self.superNode.getSkinnedPins()))
            self.blockSignals(True) #Disable updating while populating, to stop signals being emitted.
            for index, skinPin in enumerate(self.superNode.getSkinnedPins()):
                superNodeNameitem = QtGui.QTableWidgetItem(self.superNode.getName())
                superNodeNameitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                wireGroupNameitem = QtGui.QTableWidgetItem(skinPin.getWireGroupName())
                wireGroupNameitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                pinIndexItem = QtGui.QTableWidgetItem(str(skinPin.getPinIndex()))
                pinIndexItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                skinValueItem = QtGui.QTableWidgetItem(str(skinPin.getSkinValue()))

                self.setItem(index,0,superNodeNameitem)
                self.setItem(index,1,wireGroupNameitem)
                self.setItem(index,2,pinIndexItem)
                self.setItem(index,3,skinValueItem)
            self.blockSignals(False) #Disable updating while populating, to stop signals being emitted.
            self.resizeColumnsToContents()
            self.resizeRowsToContents()

    def mousePressEvent(self, mouseEvent):
        # print "Node"
        if self.superNode:
            mItem = self.indexAt(mouseEvent.pos())
            if mItem.row() == -1:
                self.clearSelection()
                for skinPin in self.superNode.getSkinnedPins() : skinPin.getPin().getNode().setHighlighted(False)
                # self.selectRow(mItem.row())
        return QtGui.QAbstractItemView.mousePressEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        # print "Release"
        # print "Sel No " + str(self.selectionModel().selection().indexes())
        if self.superNode:
            for skinPin in self.superNode.getSkinnedPins() : skinPin.getPin().getNode().setHighlighted(False) #Turn off all Highlighting
            for mItem in self.selectionModel().selection().indexes():
                if mItem.row() >= 0 :
                    self.superNode.getSkinnedPins()[mItem.row()].getPin().getNode().setHighlighted(True)
        mItem = self.indexAt(mouseEvent.pos())
        # if mItem.row() == -1 : print "missed"
        return QtGui.QAbstractItemView.mouseReleaseEvent(self, mouseEvent)

    def updateSkinning(self, item): #Need to add restriction of value to input to 0 - 1 and also to only allow float values
        if item.column() == 3: #Tryiong to check if the table is fully formed
            self.superNode.getSkinnedPins()[item.row()].setSkinValue(float(item.text()))
            self.superNode.getSkinnedPins()[item.row()].update()
            homeNode = self.superNode.getSkinnedPins()[item.row()].getPin().getNode()
            if homeNode:  #Hacky way of updating the curves when the pin is sent home! Maybe wrap into a neat function
                homeNode.dirtyCurve()



class SceneLinkTabW(QtGui.QTableWidget):
    """Class to subclass QTableWidget to give us control over how we handle
    the links from the Happy face nodes to the 3d scene Nodes

    Consider how the table data should be updated. Possible only when SuperNodes Or WireGroups are created/deleted

    """
    def __init__(self, styleData, parent = None):
        super(SceneLinkTabW, self).__init__(parent)
        self.dataProcessor = None
        self.styleData = styleData
        self.setStyleSheet(self.styleData)

        self.headers = []
        self.headers.append("  Node ID  ")
        # self.headers.append("  Direction  ")
        self.headers.append("  Group  ")
        self.headers.append("  Scale Minimum  ")
        self.headers.append("  Scale Maximum  ")
        self.headers.append("  Flip OutPut  ")
        self.headers.append("  Scene Link Node  ")
        self.headers.append("  Scene Link Attribute  ")
        self.headers.append("  Servo Channel ")
        self.headers.append("  Servo Min Angle ")
        self.headers.append("  Servo Max Angle ")

        self.nodeSubString = "hFCtrl" #Initialise the string filter as hFCtrl

        # self.populate()

    def getDataProcessor(self):
        return self.dataProcessor

    def setDataProcessor(self, dataProcessor):
        self.dataProcessor = dataProcessor

    def getNodeSubString(self):
        return self.nodeSubString

    def setNodeSubString(self, nodeSubString):
        self.nodeSubString = str(nodeSubString)

    def populate(self):
        """Function to take all the dataProcessor info and write it out in table form"""
        self.clear()
        self.setColumnCount(10)
        self.setHorizontalHeaderLabels(self.headers)

        if not self.dataProcessor:
            print "ERROR: No data processor was found, so links cannot be forged to scene nodes"
            return 0
        else:
            count = len(self.dataProcessor.collectActiveAttributeConnectors())
            self.setRowCount(count)
            self.blockSignals(True) #Disable updating while populating, to stop signals being emitted.
            for index, att in enumerate(self.dataProcessor.collectActiveAttributeConnectors()):
                nodeIdData = QtGui.QTableWidgetItem(str(att.getControllerAttrName()))
                nodeIdData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                # directionData = QtGui.QTableWidgetItem("x")
                # directionData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                groupData = QtGui.QTableWidgetItem(str(att.getHostName()))
                groupData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                minScaleData = QtGui.QTableWidgetItem(str(att.getMinScale()))
                minScaleData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                maxScaleData = QtGui.QTableWidgetItem(str(att.getMaxScale()))
                maxScaleData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                flipOutPutData = QtGui.QTableWidgetItem(str(att.isFlipped()))
                flipOutPutData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)        
                sceneNodeLinkData = QtGui.QTableWidgetItem(str(att.getSceneNode()))
                print "what is my scene Node : " + str(att.getSceneNode())
                sceneNodeLinkData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                nodeAttrLinkData = QtGui.QTableWidgetItem(str(att.getSceneNodeAttr()))
                print "what is my scene Attr : " + str(att.getSceneNodeAttr())
                nodeAttrLinkData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                servoChannelData = QtGui.QTableWidgetItem(str(att.getServoChannel()))
                servoChannelData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                servoMinAngleData = QtGui.QTableWidgetItem(str(att.getServoMinAngle()))
                servoMinAngleData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                servoMaxAngleData = QtGui.QTableWidgetItem(str(att.getServoMaxAngle()))
                servoMaxAngleData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

                self.setItem(index,0,nodeIdData)
                # self.setItem(index,1,directionData)
                self.setItem(index,1,groupData)
                self.setItem(index,2,minScaleData)
                self.setItem(index,3,maxScaleData)
                self.setItem(index,4,flipOutPutData)
                self.setItem(index,5,sceneNodeLinkData)
                self.setItem(index,6,nodeAttrLinkData)
                self.setItem(index,7,servoChannelData)
                self.setItem(index,8,servoMinAngleData)
                self.setItem(index,9,servoMaxAngleData)

            self.blockSignals(False) #Enable updating while populating, to allow signals to be emitted.
            self.resizeColumnsToContents()
            self.resizeRowsToContents()

    def checkDigit(self, newValue):
        """Function to check that we are putting in valid numbers for our outputs in the SceneLinkTabW"""
        try:
            float(newValue)
            return True
        except ValueError:
            return False

    def mousePressEvent(self, mouseEvent):
        # print "Node"
        nodeItem = self.indexAt(mouseEvent.pos())
        attConnectors = self.dataProcessor.getActiveAttributeConnectors()
        if nodeItem.row() == -1:
            self.clearSelection()
        else:  
            for att in attConnectors: att.getNode().setHighlighted(False) #Turn off all highlighting when the mouse is clicked
            currAttConnector = attConnectors[nodeItem.row()]
            currAttConnector.getNode().setHighlighted(True) #Highlight just the relevant Node
                # self.selectRow(mItem.row())
        return QtGui.QAbstractItemView.mousePressEvent(self, mouseEvent)

    # def mouseReleaseEvent(self, mouseEvent):
    #     # print "Release"
    #     # print "Sel No " + str(self.selectionModel().selection().indexes())
    #     if self.superNode:
    #         for skinPin in self.superNode.getSkinnedPins() : skinPin.getPin().getNode().setHighlighted(False) #Turn off all Highlighting
    #         for mItem in self.selectionModel().selection().indexes():
    #             if mItem.row() >= 0 :
    #                 self.superNode.getSkinnedPins()[mItem.row()].getPin().getNode().setHighlighted(True)
    #     mItem = self.indexAt(mouseEvent.pos())
    #     # if mItem.row() == -1 : print "missed"
    #     return QtGui.QAbstractItemView.mouseReleaseEvent(self, mouseEvent)

    def contextMenuEvent(self, event):
        """Function to setup the main RC context menus for the SceneLinkTabW"""
        menu = QtGui.QMenu()
        menu.setStyleSheet(self.styleData)
        index = self.indexAt(event.pos())
        if index.column() == 4:
            self.flipContextMenu(event)
        elif index.column() == 5:
            self.sceneNodeContextMenu(event)  
        elif index.column() == 6:
            self.sceneNodeAttrContextMenu(event)        
        elif index.column() == 7:
            self.servoChannelContextMenu(event)

    def flipContextMenu(self,event):
        menu = QtGui.QMenu()
        attConnectors = self.dataProcessor.getActiveAttributeConnectors()
        index = self.indexAt(event.pos())
        if self.itemFromIndex(index).text() == "True":
            menu.addAction('False')
        elif self.itemFromIndex(index).text() == "False":
            menu.addAction('True')
        action = menu.exec_(event.globalPos())
        if action: #Check that the menu has been hit at all
            if action.text() == 'False': 
                self.itemFromIndex(index).setText('False')
                attConnectors[self.itemFromIndex(index).row()].setFlipped(False)
            elif action.text() == 'True': 
                self.itemFromIndex(index).setText('True')
                attConnectors[self.itemFromIndex(index).row()].setFlipped(True)

    def servoChannelContextMenu(self,event):
        """Function for Context menu to directly choose a servo channel"""
        menu = QtGui.QMenu()
        attConnectors = self.dataProcessor.getActiveAttributeConnectors()
        index = self.indexAt(event.pos())
        for i in xrange(0,25):
            menu.addAction(str(i))
        menu.addAction("None")

        action = menu.exec_(event.globalPos())
        if action: #Check that the menu has been hit at all
            for i in xrange(0,25):
                if action.text() == str(i): 
                    self.itemFromIndex(index).setText(str(i))
                    currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                    currAttConnector.setServoChannel(i)
                    self.dataProcessor.checkUniqueServoChannels(currAttConnector, i)

            if action.text() == "None": 
                self.itemFromIndex(index).setText("None")
                attConnectors[self.itemFromIndex(index).row()].setServoChannel(None)
            self.dataProcessor.setupServoMinMaxAngles() #If an action then run through servo min and Max angles
            self.populate() #If an action was taken then repopulate the DataTable, because servoChannels may well have been adjusted

    def sceneNodeContextMenu(self,event):
        """Function to setup a RC menu for a list of specified filtered nodes"""
        menu = QtGui.QMenu()
        attConnectors = self.dataProcessor.getActiveAttributeConnectors()
        index = self.indexAt(event.pos())
        filteredSceneNodes = self.dataProcessor.returnFilteredObjects(self.nodeSubString) #Return all selected Nodes with specified substring
        
        menu.addAction("Wire to selected scene Node")
        menu.addAction("Detach Connection")
        menu.addSeparator()

        for node in filteredSceneNodes:
            menu.addAction(node)
        action = menu.exec_(event.globalPos())
        if action: #Check that the menu has been hit at all
            for node in filteredSceneNodes:
                if action.text() == str(node): 
                    currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                    currAttConnector.setSceneNode(str(node))
                    currAttConnector.setSceneNodeAttr(None) 

            if action.text() == "Wire to selected scene Node":
                selObject = self.dataProcessor.returnSelectedObject()
                if selObject: #Set the scene Node to the Object, and reset the attribute to None, so it can be chosen manually
                    currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                    currAttConnector.setSceneNode(selObject)
                    currAttConnector.setSceneNodeAttr(None) 
                else: #Object does not exist, so reset to None
                    currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                    currAttConnector.setSceneNode(None)
                    currAttConnector.setSceneNodeAttr(None) 
            elif action.text() == "Detach Connection": #reset Node and Node Attribute
                    currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                    currAttConnector.setSceneNode(None)
                    currAttConnector.setSceneNodeAttr(None) 
        self.populate() #The AttributeConnectors have been updated throughout, but no text change. Calling Populate, will then update the entire Table so text is correct.

    def sceneNodeAttrContextMenu(self,event):
        """Function to setup a RC menu for a list of specified filtered nodes"""
        menu = QtGui.QMenu()
        attConnectors = self.dataProcessor.getActiveAttributeConnectors()
        index = self.indexAt(event.pos())
        currAttConnector = attConnectors[self.itemFromIndex(index).row()]

        if not self.dataProcessor.objExists(currAttConnector.getSceneNode()): #The registered scene Node Does not exist so reset it to None, set Attribute to None too. 
            currAttConnector.setSceneNode(None)
            currAttConnector.setSceneNodeAttr(None)
        else:
            menu.addAction("Detach Node and Attribute") 
            menu.addSeparator()
            # print "This item is : " + str(self.item(self.itemFromIndex(index).row(),5).text())
            linkAttrs = self.dataProcessor.listLinkAttrs(self.item(self.itemFromIndex(index).row(),5).text()) #List all linkable attributes
            for att in linkAttrs: #Loop through list and add approriate actions
                menu.addAction(att)    
            
            action = menu.exec_(event.globalPos())
            if action: #Check that the menu has been hit at all
                for att in linkAttrs:
                    if action.text() == str(att): 
                        currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                        currAttConnector.setSceneNodeAttr(str(att))
                        self.dataProcessor.checkSceneNodeLinks(currAttConnector) #Check all the other attributeConnectors to see if they have teh same node & attribute setup.
                if action.text() == "Detach Node and Attribute":
                    currAttConnector = attConnectors[self.itemFromIndex(index).row()]
                    currAttConnector.setSceneNode(None)                
                    currAttConnector.setSceneNodeAttr(None) 
        self.populate() #The AttributeConnectors have been updated throughout, but no text change. Calling Populate, will then update the entire Table so text is correct.


    def updateSceneLinkOutputData(self, item):
        """Function to see which tableWidgetItem has been changed and take the appropriate action to update the correct attribute Connector"""
        attConnectors = self.dataProcessor.getActiveAttributeConnectors()
        currAttConnector = attConnectors[item.row()]
        isNumber = self.checkDigit(item.text())
        newValue = 1 #Arbitart initialisation
        if isNumber: newValue = float(item.text())
        if item.column() == 8:
            if isNumber: 
                item.setText(newValue)
            else: 
                item.setText("0")
        elif item.column() == 9:
            newValue = self.checkDigit(item.text())
            if newValue != "None": 
                item.setText(self.checkDigit(item.text()))
            else: 
                item.setText(self.checkDigit("180"))
        elif item.column() == 2:
            if  isNumber: 
                currAttConnector.setMinScale(newValue)  
            else: 
                currAttConnector.setMinScale(1.0)            
        elif item.column() == 3:
            if  isNumber: 
                currAttConnector.setMaxScale(newValue)    
            else: 
                currAttConnector.setMaxScale(1.0) 
        self.populate() #The AttributeConnectors have been updated throughout, but no text change. Calling Populate, will then update the entire Table so text is correct.


class ControlScale():
    def __init__(self):
        self.controlSlider = None
        self.minimum = 0
        self.maximum = 200
        self.currentScale = 100
        self.controlList = []
        self.scaleSameItems = False
        self.scene = None
        # This attribute can be set to false, so we can adjust the sliders postion without changing the scale of the whole selection
        self.isLive = True


    def setSlider(self, controlSlider):
        self.controlSlider = controlSlider

    def setScene(self, scene):
        self.scene = scene

    def getControlList(self):
        return self.controlList

    def setControlList(self, controlList):
        """A Method that takes a selection list and makes sure that we only have one type of control selected

        If more than one type of control is selected, or is no Controls are selected, then the slider deactivates. 
        Otherwise it activates
        """
        validControlList = True
        if len(controlList) != 0: # Check we have at least one Item
            leaderControlType = type(controlList[0])
            # Check the type is one of the key Control Items that we would want to scale
            if leaderControlType == GuideMarker or leaderControlType == Node or leaderControlType == SuperNode:
                for control in controlList:
                    if type(control) != leaderControlType: validControlList = False
            else: validControlList = False # If the controlType is not one of the above then we do not have a valid list
        else: validControlList = False

        if validControlList:
            self.isLive = False # set to Falso so the slider position adjustment does not cause a scale change in the selection
            self.controlList = controlList
            self.minimum = self.controlList[0].getMinimumScale()*100
            self.currentScale = self.controlList[0].getScale()*100
            self.controlSlider.setRange(self.minimum, self.maximum)
            self.controlSlider.setValue(self.currentScale)
            self.isLive = True
        
        self.controlSlider.setEnabled(validControlList) # Set the enabled state of the slider depending on whether we have a Valid List

    def getScaleSameItems(self):
        return self.scaleSameItems

    def setScaleSameItems(self, isSameItems):
        self.scaleSameItems = isSameItems

    def update(self):
        if self.isLive:
            if len(self.controlList) != 0:
                if self.scaleSameItems: # We have a control and need to scale all items in the scene that are of the same type
                    for control in self.scene.items():
                        if type(control) == type(self.controlList[0]):
                            control.setScale(float(self.controlSlider.value())/100.0)
                            control.update()
                else: # We have a control and we need to only scale the controls selected. 
                    for control in self.controlList:
                        control.setScale(float(self.controlSlider.value())/100.0)
                        control.update()
