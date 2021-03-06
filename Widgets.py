
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
        print "Item Name is : " + self.itemName
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
        self.clear()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(self.headers)
        self.setRowCount(0)
        self.resizeColumnsToContents()
        if self.superNode:
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



class SceneLinkServoTabW(QtGui.QTableWidget):
    """Class to subclass QTableWidget to give us control over how we handle
    the links from the Happy face nodes to the 3d scene Nodes

    Consider how the table data should be updated. Possible only when SuperNodes Or WireGroups are created/deleted

    """
    def __init__(self, styleData, parent = None):
        super(SceneLinkServoTabW, self).__init__(parent)
        self.dataProcessor = None
        self.styleData = styleData
        self.setStyleSheet(self.styleData)

        self.headers = []
        self.headers.append("  Node ID  ")
        self.headers.append("  Group  ")
        self.headers.append("  Attribute Curve Node ")
        # self.headers.append("  Flip OutPut  ")
        self.headers.append("  Scene Link Node  ")
        self.headers.append("  Scene Link Attribute  ")
        self.headers.append("  Servo Channel ")
        self.headers.append("  Servo Curve Node ")

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
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(self.headers)

        if not self.dataProcessor:
            print "ERROR: No data processor was found, so links cannot be forged to scene nodes"
            return 0
        else:
            count = len(self.dataProcessor.collectActiveServoDataConnectors())
            self.setRowCount(count)
            self.blockSignals(True) #Disable updating while populating, to stop signals being emitted.
            for index, servoData in enumerate(self.dataProcessor.collectActiveServoDataConnectors()):
                #Initialising everything as empty strings. If we are an additional Servo Channel, then we do not need to fill out any of the initial info!  
                nodeIdData = QtGui.QTableWidgetItem("")
                nodeIdData.setFlags(QtCore.Qt.ItemIsSelectable)               
                groupData = QtGui.QTableWidgetItem("")
                groupData.setFlags(QtCore.Qt.ItemIsSelectable)
                attrCurveNodeData = QtGui.QTableWidgetItem("")
                attrCurveNodeData.setFlags(QtCore.Qt.ItemIsSelectable)       
                sceneNodeLinkData = QtGui.QTableWidgetItem("")
                sceneNodeLinkData.setFlags(QtCore.Qt.ItemIsSelectable)        
                nodeAttrLinkData = QtGui.QTableWidgetItem("")
                nodeAttrLinkData.setFlags(QtCore.Qt.ItemIsSelectable)        

                if servoData.getIndex() == 0: #We have the first main servoDataChannel, so populate then entire row of information
                    nodeIdData = QtGui.QTableWidgetItem(str(servoData.getAttributeServoConnector().getControllerAttrName()))
                    nodeIdData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled) 
                    groupData = QtGui.QTableWidgetItem(str(servoData.getAttributeServoConnector().getHostName()))
                    groupData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    attrCurveNodeData = QtGui.QTableWidgetItem(str(servoData.getAttributeServoConnector().getControllerAttrCurveName()))
                    attrCurveNodeData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)      
                    sceneNodeLinkData = QtGui.QTableWidgetItem(str(servoData.getAttributeServoConnector().getSceneNode()))
                    sceneNodeLinkData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    nodeAttrLinkData = QtGui.QTableWidgetItem(str(servoData.getAttributeServoConnector().getSceneNodeAttr()))
                    nodeAttrLinkData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                servoChannelData = QtGui.QTableWidgetItem(str(servoData.getServoChannel()))
                servoChannelData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                servoCurveNodeData = QtGui.QTableWidgetItem(str(servoData.getServoCurveName()))
                servoCurveNodeData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                servoMinAngleData = QtGui.QTableWidgetItem(str(servoData.getServoMinAngle()))
                servoMinAngleData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                servoMaxAngleData = QtGui.QTableWidgetItem(str(servoData.getServoMaxAngle()))
                servoMaxAngleData.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

                self.setItem(index,0,nodeIdData)
                self.setItem(index,1,groupData)
                self.setItem(index,2,attrCurveNodeData) 
                # self.setItem(index,3,flipOutPutData)
                self.setItem(index,3,sceneNodeLinkData)
                self.setItem(index,4,nodeAttrLinkData)
                self.setItem(index,5,servoChannelData)
                self.setItem(index,6,servoCurveNodeData)


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
        """Event to highlight the correct Node that is being interacted with in the graphics"""
        nodeItem = self.indexAt(mouseEvent.pos())
        servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
        if nodeItem.row() == -1:
            self.clearSelection()
        else:  
            # for sDC in servoDataConnectors: print "MY Node for att is : " + str(sDC.getAttributeServoConnector().getNode())
            for sDC in servoDataConnectors: sDC.getAttributeServoConnector().getNode().setHighlighted(False) #Turn off all highlighting when the mouse is clicked
            currAttConnector = servoDataConnectors[nodeItem.row()].getAttributeServoConnector()
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
        # if index.column() == 4:
        #     self.flipContextMenu(event)
        if index.column() == 2:
            self.attributeCurveContextMenu(event)         
        elif index.column() == 3:
            self.sceneNodeContextMenu(event)  
        elif index.column() == 4:
            self.sceneNodeAttrContextMenu(event)        
        elif index.column() == 5:
            self.servoChannelContextMenu(event)
        elif index.column() == 6:
            self.servoCurveContextMenu(event)

    def attributeCurveContextMenu(self,event):
        """Function for Context menu to directly select an Attribute AnimCurve"""
        menu = QtGui.QMenu()
        servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
        index = self.indexAt(event.pos())
        menu.addAction("Select AnimCurve")

        currServoDataConnector = servoDataConnectors[self.itemFromIndex(index).row()]
        
        action = menu.exec_(event.globalPos())
        if action: #Check that the menu has been hit at all
            if action.text() == "Select AnimCurve":
                currServoDataConnector.getAttributeServoConnector().selectControllerAttrCurveNode()

    def servoCurveContextMenu(self,event):
        """Function for Context menu to directly select an Servo AnimCurve"""
        menu = QtGui.QMenu()
        servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
        index = self.indexAt(event.pos())
        menu.addAction("Select AnimCurve")

        currServoDataConnector = servoDataConnectors[self.itemFromIndex(index).row()]
        
        action = menu.exec_(event.globalPos())
        if action: #Check that the menu has been hit at all
            if action.text() == "Select AnimCurve":
                currServoDataConnector.selectServoCurveNode()

    # def flipContextMenu(self,event):
    #     menu = QtGui.QMenu()
    #     attConnectors = self.dataProcessor.getActiveAttributeConnectors()
    #     index = self.indexAt(event.pos())
    #     if self.itemFromIndex(index).text() == "True":
    #         menu.addAction('False')
    #     elif self.itemFromIndex(index).text() == "False":
    #         menu.addAction('True')
    #     action = menu.exec_(event.globalPos())
    #     if action: #Check that the menu has been hit at all
    #         if action.text() == 'False': 
    #             self.itemFromIndex(index).setText('False')
    #             attConnectors[self.itemFromIndex(index).row()].setFlipped(False)
    #         elif action.text() == 'True': 
    #             self.itemFromIndex(index).setText('True')
    #             attConnectors[self.itemFromIndex(index).row()].setFlipped(True)

    def servoChannelContextMenu(self,event):
        """Function for Context menu to directly choose a servo channel"""
        menu = QtGui.QMenu()
        servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
        index = self.indexAt(event.pos())
        for i in xrange(0,25):
            menu.addAction(str(i))
        menu.addAction("None")
        menu.addSeparator()
        menu.addAction("Add Servo Channel")

        #Now check if there are multiple servoDataChannels, by checking the ID of the servo. If there are, then we can give the option to remove it
        currServoDataConnector = servoDataConnectors[self.itemFromIndex(index).row()]
        if currServoDataConnector.getIndex() > 0: #We have an additional servoDataChannel, so give the option to remove it! 
            menu.addAction("Remove Servo Channel")

        action = menu.exec_(event.globalPos())
        if action: #Check that the menu has been hit at all
            for i in xrange(0,25):
                if action.text() == str(i): 
                    self.itemFromIndex(index).setText(str(i))
                    currServoDataConnector = servoDataConnectors[self.itemFromIndex(index).row()]
                    currServoDataConnector.setServoChannel(i)
                    self.dataProcessor.checkUniqueServoChannels(currServoDataConnector, i)

            if action.text() == "None": 
                self.itemFromIndex(index).setText("None")
                servoDataConnectors[self.itemFromIndex(index).row()].setServoChannel(None)
            elif action.text() == "Add Servo Channel":
                currServoDataConnector = servoDataConnectors[self.itemFromIndex(index).row()]
                currAttConnector = currServoDataConnector.getAttributeServoConnector()
                currAttConnector.addServoDataConnector()
                self.dataProcessor.manageAttributeConnections() #Run a check through all the attribute Connections to make sure that the extra channel is in place
            elif action.text() =="Remove Servo Channel": #Find the attributeServoConnector, then remove the dataServoConnector of the appropriate Index
                currIndex = currServoDataConnector.getIndex()
                currServoDataConnector.getAttributeServoConnector().removeServoDataConnector(currIndex)
                self.dataProcessor.manageAttributeConnections() #Run a check through all the attribute Connections to make sure that the extra channel is in place
            
            # self.dataProcessor.setupServoMinMaxAngles() #If an action then run through servo min and Max angles
            self.populate() #If an action was taken then repopulate the DataTable, because servoChannels may well have been adjusted

    def sceneNodeContextMenu(self,event):
        """Function to setup a RC menu for a list of specified filtered nodes"""
        menu = QtGui.QMenu()
        servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
        index = self.indexAt(event.pos())
        currServoConnector = servoDataConnectors[self.itemFromIndex(index).row()]
        currAttConnector = currServoConnector.getAttributeServoConnector()

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
                    currAttConnector.setSceneNode(str(node))
                    currAttConnector.setSceneNodeAttr(None) 

            if action.text() == "Wire to selected scene Node":
                selObject = self.dataProcessor.returnSelectedObject()
                if selObject: #Set the scene Node to the Object, and reset the attribute to None, so it can be chosen manually
                    currAttConnector.setSceneNode(selObject)
                    currAttConnector.setSceneNodeAttr(None) 
                else: #Object does not exist, so reset to None
                    currAttConnector.setSceneNode(None)
                    currAttConnector.setSceneNodeAttr(None) 
            elif action.text() == "Detach Connection": #reset Node and Node Attribute
                    currAttConnector.setSceneNode(None)
                    currAttConnector.setSceneNodeAttr(None) 
        self.populate() #The AttributeConnectors have been updated throughout, but no text change. Calling Populate, will then update the entire Table so text is correct.

    def sceneNodeAttrContextMenu(self,event):
        """Function to setup a RC menu for a list of specified filtered nodes"""
        print "This runs"
        menu = QtGui.QMenu()
        servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
        index = self.indexAt(event.pos())
        currServoConnector = servoDataConnectors[self.itemFromIndex(index).row()]
        currAttConnector = currServoConnector.getAttributeServoConnector()

        if not self.dataProcessor.objExists(currAttConnector.getSceneNode()): #The registered scene Node Does not exist so reset it to None, set Attribute to None too. 
            currAttConnector.setSceneNode(None)
            currAttConnector.setSceneNodeAttr(None)
        else:
            menu.addAction("Detach Node and Attribute") 
            menu.addSeparator()
            # print "This item is : " + str(self.item(self.itemFromIndex(index).row(),5).text())
            # linkAttrs = self.dataProcessor.listLinkAttrs(self.item(self.itemFromIndex(index).row(),5).text()) #List all linkable attributes
            linkAttrs = self.dataProcessor.listLinkAttrs(currAttConnector.getSceneNode()) #List all linkable attributes
            for att in linkAttrs: #Loop through list and add approriate actions
                menu.addAction(att)    

            action = menu.exec_(event.globalPos())
            if action: #Check that the menu has been hit at all
                for att in linkAttrs:
                    if action.text() == str(att): 
                        currAttConnector.setSceneNodeAttr(str(att))
                        self.dataProcessor.checkSceneNodeLinks(currAttConnector) #Check all the other attributeConnectors to see if they have teh same node & attribute setup.
                if action.text() == "Detach Node and Attribute":
                    currAttConnector.setSceneNode(None)                
                    currAttConnector.setSceneNodeAttr(None) 
        self.populate() #The AttributeConnectors have been updated throughout, but no text change. Calling Populate, will then update the entire Table so text is correct.


    # def updateSceneLinkOutputData(self, item):
    #     """Function to see which tableWidgetItem has been changed and take the appropriate action to update the correct attribute Connector"""
    #     servoDataConnectors = self.dataProcessor.getActiveServoDataConnectors()
    #     currAttConnector = servoDataConnectors[item.row()].getAttributeServoConnector()
    #     isNumber = self.checkDigit(item.text())
    #     newValue = 1 #Arbitart initialisation
    #     if isNumber: newValue = float(item.text())
    #     if item.column() == 8:
    #         if isNumber: 
    #             item.setText(newValue)
    #         else: 
    #             item.setText("0")
    #     elif item.column() == 9:
    #         newValue = self.checkDigit(item.text())
    #         if newValue != "None": 
    #             item.setText(self.checkDigit(item.text()))
    #         else: 
    #             item.setText(self.checkDigit("180"))
    #     elif item.column() == 2:
    #         if  isNumber: 
    #             currAttConnector.setMinScale(newValue)  
    #         else: 
    #             currAttConnector.setMinScale(1.0)            
    #     elif item.column() == 3:
    #         if  isNumber: 
    #             currAttConnector.setMaxScale(newValue)    
    #         else: 
    #             currAttConnector.setMaxScale(1.0) 
    #     self.populate() #The AttributeConnectors have been updated throughout, but no text change. Calling Populate, will then update the entire Table so text is correct.


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
