
from PyQt4 import QtCore, QtGui
import sys
import os

#######Project python imports################################################
from ControlItems import *



#################################UI CLASSES & FUNCTIONS & PROMOTED WIDGETS##################################################################################

def buildGuideItem(itemName):
    """A function to build the correct Rig Graphics Item from an input string"""
    itemstring = str(itemName) + "()"
    # print itemstring 
    item = eval(itemstring)
    return item


class WireGroupButton(QtGui.QPushButton):
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

