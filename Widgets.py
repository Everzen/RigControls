
from PyQt4 import QtCore, QtGui
import sys
import os

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
        imageFile = ""
        imageFileCss = ""
        if state == "hover":
            imageFile = 'images/' + self.itemName + '_Hover.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'
        elif state == "pressed":
            imageFile = 'images/' + self.itemName + '_Pressed.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'
        else:
            imageFile = 'images/' + self.itemName + '.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'

        if os.path.exists(imageFile): #create icon and add to button
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
        imageFile = ""
        imageFileCss = ""
        if state == "hover":
            imageFile = 'images/' + self.itemName + '_Hover.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'
        elif state == "pressed":
            imageFile = 'images/' + self.itemName + '_Pressed.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'
        else:
            imageFile = 'images/' + self.itemName + '.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'

        if os.path.exists(imageFile): #create icon and add to button
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
        imageFile = ""
        imageFileCss = ""
        if state == "hover":
            imageFile = 'images/' + self.form + '_Hover.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'
        elif state == "pressed":
            imageFile = 'images/' + self.form + '_Pressed.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'
        else:
            imageFile = 'images/' + self.form + '.png'
            imageFileCss = 'image: url(:/' + imageFile + ');'

        if os.path.exists(imageFile): #create icon and add to button
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
        self.headers = QtCore.QStringList()
        self.headers.append(QtCore.QString("  Super Node Controller  "))
        self.headers.append(QtCore.QString("  Node Wire Group  "))
        self.headers.append(QtCore.QString("  Node Index  "))
        self.headers.append(QtCore.QString("  Skin Value  "))
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
            self.setRowCount(len(self.superNode.getSkinnedPins()))
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
                for rigCurve in homeNode.rigCurveList:
                    rigCurve().buildCurve() 
