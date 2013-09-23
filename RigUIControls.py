##############LEDLIGHTLines############################################
import sys
import weakref
import math
from PyQt4 import QtCore, QtGui
import numpy as np
import socket #for sending out UPD signals
import os
import FileControl
import xml.etree.ElementTree as xml

#######STANDARD LIBRARY FUNCTIONS THAT SHOULD PROBABLY BE IN A MAIN LIBRARY SOMEWHERE##############################


def norm(vec):
    """function to normalise a vector - creating the unit vector"""
    return vec/np.linalg.norm(vec)

def npVec(vec):
    """Converts a list/QPoint into an np array"""
    vec = np.array([vec.x(),vec.y()])
    # print "This is Vec : " + str(vec)
    return vec

def QPVec(npVec):
    """Converts an np array into a QPoint"""
    return QtCore.QPointF(npVec[0], npVec[1])

#################################RIG CODE#############################################################################

class RigCurveInfo():
    """A Class to capture how the """
    def __init__(self,startNode, endNode, targNode):
        self.startPos = npVec(startNode().pos())
        self.endPos = npVec(endNode().pos())
        self.targPos = npVec(targNode().pos())
        # print "self.startPos : " + str(self.startPos)
        # print "self.endPos : " + str(self.endPos)
        # print "self.targPos : " + str(self.targPos)

        self.dirVec = self.endPos - self.startPos
        # print "dirVec : " + str(self.dirVec)
        self.dirDist = np.linalg.norm(self.dirVec)
        # print "dirDist : " + str(self.dirDist)
        self.perpUnitVec = self.setPerpUnitVec()
        # print "perpUnitVec : " + str(self.perpUnitVec)

        self.targetVec = norm(self.targPos - self.startPos)
        self.targNodeDist = np.linalg.norm(self.targPos - self.endPos)
        self.perpSwing = np.dot(self.perpUnitVec, self.targetVec)
        # self.sideSwing = 1 

    def setPerpUnitVec(self):
        perpVec = np.cross([self.dirVec[0], self.dirVec[1], 1], [0,0,1])
        #Normalised perpendicular vector
        perpVec = np.array([perpVec[0],perpVec[1]]) 
        # print "PerpVec = " + str(perpVec)
        self.PerpUnitVec = norm(perpVec)
        return self.PerpUnitVec

    def getStartPos(self):
        return self.startPos

    def getEndPos(self):
        return self.endPos

    def getTargPos(self):
        return self.targPos

    def getDirVec(self):
        return self.dirVec

    def getDirDist(self):
        return self.dirDist

    def getperpUnitVec(self):
        return self.perpUnitVec 

    def getTargetVec(self):
        return self.targetVec

    def getTargetNodeDist(self):
        return self.targNodeDist

    def getPerpSwing(self):
        return self.perpSwing


#################################UI CLASSES & FUNCTIONS##################################################################################
def buildGuideItem(itemName):
    """A function to build the correct Rig Graphics Item from an input string"""
    itemstring = str(itemName) + "()"
    item = eval(itemstring)
    return item


#################################PROMOTED WIDGETS#############################################################################
class ReflectionLine(QtGui.QGraphicsItem):
    def __init__(self,gViewWidth, gViewHeight):
        super(ReflectionLine, self).__init__()
        self.width = gViewWidth
        self.height = gViewHeight
        self.inset = 10
        self.drawStart = []
        self.drawEnd = []
        # self.visible = True #Use default isVisble method etc
        # self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.adjustable = False
        self.initUI()

    def initUI(self):
        # self.drawStart = [self.width/2, self.inset]
        # self.drawEnd = [self.width/2, self.height - 2*self.inset]
        self.drawStart = [0, -self.height/2 + self.inset]
        self.drawEnd = [0, self.height/2 - self.inset]
        self.setPos(QtCore.QPointF(self.width/2, self.height/2))
        self.restPos = QtCore.QPointF(self.width/2, self.height/2)

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        self.prepareGeometryChange()
        pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawLine(self.drawStart[0],self.drawStart[1],self.drawEnd[0],self.drawEnd[1])
        if self.adjustable:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 0.25, QtCore.Qt.SolidLine))
            adjustRect = QtCore.QRectF(QPVec(self.drawStart) - QtCore.QPointF(5, 0), QPVec(self.drawEnd) + QtCore.QPointF(5, 0))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25)))
            painter.drawRect(adjustRect)

    def setAdjustable(self, state):
        self.adjustable = state
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,state)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,state)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,state)
        self.update()

    def getAdjustable(self):
        return self.adjustable

    def boundingRect(self):
        adjust = 5.0
        return QtCore.QRectF( -adjust, -self.height/2 + self.inset - adjust,
                             2*adjust, self.height - 2*self.inset + 2*adjust)

    # def itemChange(self, change, value):
    #     if change == QtGui.QGraphicsItem.ItemPositionChange:
    #         # print "Item new position :" + str(self.pos().x()) + ", " + str(self.pos().y())
    #         # print "Max Level : " + str(self.maxLevel)
    #         yPos = value.toPointF().y()
    #         # if yPos > self.maxLevel : yPos = self.maxLevel
    #         # elif yPos < self.minLevel : yPos = self.minLevel
    #         vValue = self.getValue(yPos)
    #         # print "VValue %s" % str(vValue)
    #         if vValue:       
    #             self.colourBroadcaster.setValue(vValue)
    #             self.colourBroadcaster.broadcast()
    #             # print "Colour Value is : " + str(self.getValue(yPos))
    #         return QtCore.QPointF(509.75,yPos)
    #     return QtGui.QGraphicsItem.itemChange(self, change, value)


    def remap(self,gViewWidth, gViewHeight):
        self.width = gViewWidth
        self.height = gViewHeight
        self.drawStart = [0, -self.height/2 + self.inset]
        self.drawEnd = [0, self.height/2 - self.inset]
        self.setPos(QtCore.QPointF(self.width/2, self.height/2))
        self.update()
    # def (self):
    #     return self.drawStart[0]


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


    # def enterEvent(self,event):
    #     print("Enter")
    #     self.pixmap = self.validImageFile(state = "hover")
    #     # self.setStyleSheet("background-color:#45b545;")

    def leaveEvent(self,event):
        # self.setStyleSheet("background-color:yellow;")
        # self.pixmap = self.validImageFile()
        self.setDown(False)
        self.setStyleSheet(self.validImageFile())

    def mousePressEvent(self,event):
        # self.setStyleSheet("background-color:yellow;")
        # self.pixmap = self.validImageFile("pressed")
        # self.paintEvent(event)
        self.setDown(True)
        self.setStyleSheet(self.validImageFile(state = "pressed"))


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




#################################RIGGER CONTROL GROUPS#############################################################################

class WireControlGroup():
    def __init__(self, pinQPointList, rigGView):
        #LIST OF ATTRIBUTES
        self.name = ""
        self.colour = QtCore.Qt.black
        self.pinPositions = pinQPointList
        self.pins = []
        self.nodes = []
        self.pinTies = []
        self.curve = None
        self.colour = QtGui.QColor(0,0,0)
        self.scene = rigGView.scene()
        self.initBuild()

    def initBuild(self):
        self.createPins()
        self.createNodes()
        self.createPintTies()
        self.createCurve()

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = str(newName)

    def createPins(self):
        """Initially place the pins according to markers given, and fill out self.pins"""
        self.pins = []
        for index,p in enumerate(self.pinPositions):
            cP = ControlPin(p)   
            cP.setIndex(index)
            cP.setGroupName(self.name)
            self.pins.append(cP)
            self.scene.addItem(cP)

    def createNodes(self):
        self.nodes = []
        for index, p in enumerate(self.pinPositions):
            node = Node(p)
            node.setIndex(index)
            node.setPin(self.pins[index])
            node.setWireGroup(self)
            self.nodes.append(node)
            self.scene.addItem(node)

    def createPintTies(self):
        self.pinTies = []
        if len(self.pins) > 1 and len(self.pins) == len(self.nodes):
            for index, n in enumerate(self.nodes):
                pT = PinTie(n, self.pins[index])
                pT.setIndex(index)
                self.pinTies.append(pT)
                n.setPinTie(pT)
                self.scene.addItem(pT)
        else:
            print "WARNING : NO PIN TIES DRAWN SINCE THERE WERE INSUFFICIENT NODES OR UNEQUAL NODES AND PINS"

    def createCurve(self):
        if len(self.nodes) > 2:
            self.curve = RigCurve(self.colour, self.nodes)
            self.scene.addItem(self.curve)

    def resetNodes(self):
        for node in self.nodes:
            node.goHome()

class ControlPin(QtGui.QGraphicsItem):
    def __init__(self, cPos, control = None):
        super(ControlPin, self).__init__()
        # self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.scale = 1
        self.scaleOffset = 2.5
        self.index = 0 
        self.groupName = 1

        self.setPos(cPos)
        self.setZValue(1) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

    def getIndex(self):
        return self.index

    def setIndex(self,index):
        self.index = index

    def getGroupName(self):
        return str(self.groupName)

    def setGroupName(self, groupName):
        self.groupName = groupName

    def drawWireControl(self, painter):
        wCurve1 = QtGui.QPainterPath()

        locAx = -1.6 * self.scale*self.scaleOffset
        locAy = 2.78 * self.scale*self.scaleOffset

        locBx = -0.556 * self.scale*self.scaleOffset
        locBy = 3.25 * self.scale*self.scaleOffset

        pen = QtGui.QPen(QtCore.Qt.black, 0.25, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        wCurve1 = QtGui.QPainterPath()
        wCurve1.moveTo(QtCore.QPointF(locAx,locAy))
        wCurve1.cubicTo(QtCore.QPointF(locBx,locBy),QtCore.QPointF(-locBx,locBy),QtCore.QPointF(-locAx,locAy))

        wCurve2 = QtGui.QPainterPath()
        wCurve2.moveTo(QtCore.QPointF(locAy,locAx))
        wCurve2.cubicTo(QtCore.QPointF(locBy,locBx),QtCore.QPointF(locBy,-locBx),QtCore.QPointF(locAy,-locAx))
        
        wCurve3 = QtGui.QPainterPath()
        wCurve3.moveTo(QtCore.QPointF(locAx,-locAy))
        wCurve3.cubicTo(QtCore.QPointF(locBx,-locBy),QtCore.QPointF(-locBx,-locBy),QtCore.QPointF(-locAx,-locAy))

        wCurve4 = QtGui.QPainterPath()
        wCurve4.moveTo(QtCore.QPointF(-locAy,locAx))
        wCurve4.cubicTo(QtCore.QPointF(-locBy,locBx),QtCore.QPointF(-locBy,-locBx),QtCore.QPointF(-locAy,-locAx))
        
        # painter.setBrush(self.color)
        painter.strokePath(wCurve1, painter.pen())
        painter.strokePath(wCurve2, painter.pen())
        painter.strokePath(wCurve3, painter.pen())
        painter.strokePath(wCurve4, painter.pen())

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        pen = QtGui.QPen(QtCore.Qt.black, 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        # painter.drawLine(self.scale*self.scaleOffset*-3,self.scale*self.scaleOffset*-3,self.scale*self.scaleOffset*3,self.scale*self.scaleOffset*3)
        # painter.drawLine(self.scale*self.scaleOffset*-3,self.scale*self.scaleOffset*3,self.scale*self.scaleOffset*3,self.scale*self.scaleOffset*-3)
        painter.drawLine(0,self.scale*self.scaleOffset*3.0,0,self.scale*self.scaleOffset*-3.0)
        painter.drawLine(self.scale*self.scaleOffset*-3.0,0,self.scale*self.scaleOffset*3.0,0)

        #Now add wire details if needed
        self.drawWireControl(painter)

    def boundingRect(self):
        adjust = 5
        return QtCore.QRectF(self.scale*self.scaleOffset*(-3 - adjust), self.scale*self.scaleOffset*(-3 - adjust),
                             self.scale*self.scaleOffset*(6 + adjust), self.scale*self.scaleOffset*(6 + adjust))


class PinTie(QtGui.QGraphicsItem):
    def __init__(self, startNode, endNode):
        super(PinTie, self).__init__()
        # self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.thickness = 0.5
        self.index = 0 
        self.groupName = 1
        self.startNode = weakref.ref(startNode)
        self.endNode = weakref.ref(endNode)
        self.startPoint = None
        self.endPoint = None
        self.midPoint = None
        self.drawTie()
        self.setZValue(1) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

    def getIndex(self):
        return self.index

    def setIndex(self,index):
        self.index = index

    def getGroupName(self):
        return str(self.groupName)

    def setGroupName(self, groupName):
        self.groupName = groupName

    def getThickness(self):
        return self.thickness

    def setThickness(self, thickness):
        self.thickness = thickness

    def linePoints(self):
        """Function to calulate the start mid and end points of the line"""
        self.midPoint =  (self.startNode().pos() + self.endNode().pos())/2
        self.startPoint = self.startNode().pos() - self.midPoint 
        self.endPoint = self.endNode().pos() - self.midPoint #+ QtCore.QPointF(20,20)


    def boundingRect(self):
        return self.line.boundingRect()
    # def boundingRect(self):
    #     adjust = 5
    #     return QtCore.QRectF(self.startPoint, self.endPoint)

    def drawTie(self):
        self.line = QtGui.QPainterPath()
        # self.prepareGeometryChange()
        self.linePoints()
        if self.startNode != None and self.endNode != None: 
            self.setPos(self.midPoint)
            self.line.moveTo(self.startPoint)
            self.line.lineTo(self.endPoint) 
            

    def paint(self, painter, option, widget):
        # self.prepareGeometryChange()
        pen = QtGui.QPen(QtGui.QColor(255,255,0), self.thickness, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.strokePath(self.line, painter.pen())



class GuideMarker(QtGui.QGraphicsItem):
    def __init__(self):
        super(GuideMarker, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        ####MARKER IDENTIFIERS####################################
        self.index = None        
        self.active = False
        self.activeIndex = 0
        self.scale = 1.0
        self.colourList = [QtGui.QColor(255,0,0), QtGui.QColor(0,255,0), QtGui.QColor(0,0,255), QtGui.QColor(0,255,255), QtGui.QColor(255,0,255), QtGui.QColor(255,255,0), QtGui.QColor(255,125,0), QtGui.QColor(125,255,0),QtGui.QColor(255,0,125),QtGui.QColor(125,0,255),QtGui.QColor(0,255,125),QtGui.QColor(0,125,255),QtGui.QColor(255,125,125),QtGui.QColor(125,255,125),QtGui.QColor(125,125,255),QtGui.QColor(255,255,125),QtGui.QColor(255,125,255),QtGui.QColor(125,255,255)]
        self.guideColourIndex = 0
        self.setZValue(11) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

        # self.setPos(QtCore.QPointF(50,50))
        # self.move_restrict_rect = QtGui.QGraphicsRectItem(50,50,,410)

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        GuideMarkerRoot = xml.Element('GuideMarker')
        attributes = xml.SubElement(GuideMarkerRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'active', value = str(self.getActive()))
        xml.SubElement(attributes, 'attribute', name = 'activeIndex', value = str(self.getActiveIndex()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'guideColourIndex', value = str(self.getGuideColourIndex()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        # xmlFile = FileControl.XMLMan()
        # xmlFile.setTree(GuideMarkerRoot)
        # xmlFile.setFile("faceFiles/test.xml")
        # xmlFile.save()
        return GuideMarkerRoot

    def read(self, GuideMarkerXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        # GuideMarkerRoot = GuideMarkerXml.getroot()
        for a in GuideMarkerXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'active': self.setActive(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'activeIndex': self.setActiveIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'guideColourIndex': self.setGuideColourIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getShowID(self):
        return self.showID

    def setShowID(self,state):
        self.showID = state

    def getIndex(self):
        return self.index

    def setIndex(self,index):
        self.index = index

    def getActive(self):
        return self.active

    def setActive(self, state):
        self.active = state
        self.update()

    def getActiveIndex(self):
        return self.activeIndex

    def setActiveIndex(self, index):
        self.activeIndex = index
        self.update()

    def getGuideColourIndex(self):
        return self.guideColourIndex

    def setGuideColourIndex(self, index):
        self.guideColourIndex = int(index)

    def boundingRect(self):
        adjust = 5
        numberstretch = 5
        return QtCore.QRectF(self.scale*(-18 - adjust), self.scale*(-18 - adjust),
                             self.scale*(36 + adjust), self.scale*(36 + adjust + numberstretch))

    def drawActive(self, painter):
        """A function to draw an active glow around the marker when activated"""
        if self.active:
            pen = QtGui.QPen(self.colourList[self.guideColourIndex], self.scale*0.5, QtCore.Qt.SolidLine)
            gradient = QtGui.QRadialGradient(0, 0, self.scale*18)
            gradient.setColorAt(0, QtGui.QColor(self.colourList[self.guideColourIndex].red(),0,0,100))
            gradient.setColorAt(1, QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),20))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawEllipse(self.scale*-18, self.scale*-18, self.scale*36, self.scale*36)        

    def drawID(self, painter):
        # print "Marker Index : " + str(self.index)
        # print "Marker guideIndex : " + str(self.guideIndex)
        # print "Marker showID : " + str(self.showID)
        if self.showID and self.index: #Conditions met to disply numbers on corners
            pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            fontsize = 9
            if self.scale < 1.0:
                fontsize = int(9*self.scale)
            painter.setFont(QtGui.QFont('Arial', fontsize))
            if self.guideIndex != 0: 
                print "guide index : " + str(self.guideIndex)
                painter.drawText(self.scale*12,self.scale*-12, str(self.guideIndex)) #Add in the guide Index if it is not 0
            painter.drawText(self.scale*12,self.scale*21,str(self.index))

    def drawActiveIndex(self,painter):
        if self.active: #Conditions met to disply numbers on corners
            pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            fontsize = 9
            if self.scale < 1.0:
                fontsize = int(9*self.scale)
            painter.setFont(QtGui.QFont('Arial', fontsize))
            painter.drawText(self.scale*12,self.scale*21,str(self.activeIndex))

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        self.drawActive(painter)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray, 0))
        painter.drawRect(self.scale*-8, self.scale*-8, self.scale*16, self.scale*16)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0.25, QtCore.Qt.SolidLine))
        painter.drawRect(self.scale*-4, self.scale*-4, self.scale*8, self.scale*8)
        # painter.drawRect(-12.5, -2.75, 25, 5)
        pen = QtGui.QPen(self.colourList[self.guideColourIndex], 0.5, QtCore.Qt.SolidLine)
        if option.state & QtGui.QStyle.State_Sunken or self.isSelected(): # selected
            gradient = QtGui.QRadialGradient(0, 0, self.scale*4)
            gradient.setColorAt(1, QtGui.QColor(self.colourList[self.guideColourIndex].red(),0,0,150))
            gradient.setColorAt(0, QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),20))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(self.scale*-4, self.scale*-4, self.scale*8, self.scale*8)
            pen = QtGui.QPen(self.colourList[self.guideColourIndex], 2*self.scale, QtCore.Qt.SolidLine)

        painter.setPen(pen)
        painter.drawLine(self.scale*-12,self.scale*-12,self.scale*12,self.scale*12)
        painter.drawLine(self.scale*-12,self.scale*12,self.scale*12,self.scale*-12)
        # self.drawID(painter) #Now add in the Marker ID if relevant
        self.drawActiveIndex(painter)


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            pass
            # print "Marker Move pos : " + str(self.scenePos())  
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    # def mouseMoveEvent(self, event):
    #     QtGui.QGraphicsItem.mouseMoveEvent(self, event)



class RigCurve(QtGui.QGraphicsItem):
    def __init__(self, color, controlNodes, parent=None, scene=None):
        super(RigCurve, self).__init__(parent, scene)
        self.selected = False
        self.color = color
        self.nodeList = self.getNodeList(controlNodes)
        self.curveSwing = 0.25
        self.handlescale = 0.3
        self.secondHandleScale = 0.5
        self.addCurveLink()
        self.buildCurve()
        self.setZValue(0) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

    def getNodeList(self, controlNodes):
        """Function to collect and store control nodes as weak references"""
        self.nodeList = []
        if len(controlNodes) < 3: print "WARNING : There are less than 3 Control Nodes" 
        for n in controlNodes: 
            self.nodeList.append(weakref.ref(n))
        return self.nodeList

    def addCurveLink(self):
        for n in self.nodeList:
            n().addRigCurve(self)

    def set_selected(self, selected):
        self.selected = selected

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtCore.Qt.black, 1.2, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.setBrush(self.color)
        painter.strokePath(self.path, painter.pen())

    def buildCurve(self):
        """Function to build section of Bezier"""
        if self.isVisible:
            if len(self.nodeList) >= 3:
                self.path = QtGui.QPainterPath()
                self.prepareGeometryChange()
                #BuildSection
                curveInfo = RigCurveInfo(self.nodeList[0],self.nodeList[1],self.nodeList[2])
                startPoint = curveInfo.getStartPos()
                endPoint = curveInfo.getEndPos()
                targetPoint= curveInfo.getTargPos()
                #Take point at a 1/3 of the way along the line and 2/3 of the way along the line
                cP1 = startPoint + self.handlescale*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()
                cP2 = startPoint + (1-self.handlescale)*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()
                #Now make sure that we assign the new Bezier handles to the end node, but making the far handle proportional to the next segment length
                self.nodeList[0]().setBezierHandles(cP1, 1)
                self.nodeList[1]().setBezierHandles(cP2, 0)
                #Now calculate our endNode second handle - to do this we need to calculate the distance to the next node (endnode to targetnode)
                targNodeDist = np.linalg.norm(targetPoint - endPoint)
                #Now set the next handle of the endpoint to be the same tangent, but scaled in proportion to the length of the endnode -> targetnode segment 
                cPNext = (endPoint - cP2)*self.secondHandleScale*curveInfo.getTargetNodeDist()/curveInfo.getDirDist() + endPoint
                self.nodeList[1]().setBezierHandles(cPNext, 1)
                # print "End Node Handle Test : " + str(self.nodeList[1]().getBezierHandles(0))
                # print "End Node Handle Test : " + str(self.nodeList[1]().getBezierHandles(1))
                # print "CP1 : " + str(cP1)
                # print "CP2 : " + str(cP2)
                #Move the points out along the the perpendicular vector by a 3rd of the magnitude
                self.path.moveTo(QPVec(startPoint))
                self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(endPoint))
                # self.path.cubicTo(QPVec([20,20]),QPVec([40,20]),QPVec([50,50]))
                midNodes = self.nodeList[1:-2]
                for index,node in enumerate(midNodes): #This is setup to give us nodes and indexing
                    curveInfo = RigCurveInfo(node,self.nodeList[index+2],self.nodeList[index+3])
                    startPoint = curveInfo.getStartPos()
                    endPoint = curveInfo.getEndPos()
                    targetPoint= curveInfo.getTargPos()
                    #First Control Point is already resolved!
                    cP1 = node().getBezierHandles(1)
                    cP2 = startPoint + (1-self.handlescale)*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()

                    node().setBezierHandles(cP1, 1)
                    self.nodeList[index+2]().setBezierHandles(cP2, 0)
                    #Now figure out next node hand
                    targNodeDist = np.linalg.norm(targetPoint - endPoint)
                    cPNext = (endPoint - cP2)*self.secondHandleScale*curveInfo.getTargetNodeDist()/curveInfo.getDirDist() + endPoint
                    self.nodeList[index+2]().setBezierHandles(cPNext, 1)
                    self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(endPoint))
                #Now place the final Bezier. To do this we will calculate from the end backwards, then plot the nodes forwards
                curveInfo = RigCurveInfo(self.nodeList[-1],self.nodeList[-2],self.nodeList[-3])
                startPoint = curveInfo.getStartPos()
                endPoint = curveInfo.getEndPos()
                targetPoint= curveInfo.getTargPos()
                cP2 = startPoint + self.handlescale*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()
                #We have cP1 from our previous Node calculations
                cP1 = self.nodeList[-2]().getBezierHandles(1)
                self.nodeList[-1]().setBezierHandles(cP2, 0)
                self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(startPoint))





###Nodes for selection in the Graphics View
class Node(QtGui.QGraphicsItem):
    def __init__(self, nPos, restraintDef=None, moveThreshold=5, operatorClass = None):
        QtGui.QGraphicsItem.__init__(self)
        self.index = 0
        self.rigCurveList = []
        self.bezierHandles = [None, None]
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        # self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.restraintDef = restraintDef
        self.move_restrict_circle = None
        self.operatorClass = operatorClass
        
        self.marker = False
        self.radius = 8
        # self.pin.append(weakref.ref(pin))
        self.pin = None
        self.pinTie = None

        self.wireGroup = None
        # if self.restraintDef:
        #     self.move_restrict_circle = QtGui.QGraphicsEllipseItem(2*self.restraintDef["centerOffset"][0],2*self.restraintDef["centerOffset"][1], 2*self.restraintDef["radius"],2*self.restraintDef["radius"])
        # offsetPos = self.pos() - QPVec(self.restraintDef["center"])
        self.setPos(nPos)
        if self.operatorClass:
            self.operatorClass.setPos([offsetPos.x(),offsetPos.y()]) #Set colourGrabber position
            self.operatorClass.mouseMoveExecute() # Set the initial colour

        self.setZValue(12) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

    def setIndex(self,value):
        self.index = value

    def getIndex(self):
        return self.index

    # def type(self):
    #     return Node.Type

    def addRigCurve(self, rigCurve):
        self.rigCurveList.append(weakref.ref(rigCurve))
        # print "Rig Curve List is : " + str(self.rigCurveList) + " - for Node :" + str(self)

    def setBezierHandles(self, handlePos, handleNo):
        """A function to record the position of the bezier handles associated with this Node"""
        self.bezierHandles[handleNo] = handlePos

    def getBezierHandles(self, handleNo):
        """A function to return the position of the bezier handles associated with this Node"""
        return self.bezierHandles[handleNo]

    def getPin(self):
        return self.pin

    def setPin(self, pin):
        if type(pin) == ControlPin:
            self.pin = pin
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PIN ALLOCATION"

    def getPinTie(self):
        return self.pinTie

    def setPinTie(self, pinTie):
        if type(pinTie) == PinTie:
            self.pinTie = weakref.ref(pinTie)
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PINTIE ALLOCATION"

    def getWireGroup(self):
        if not self.wireGroup: print "WARNING : NO REGISTERED WIRE GROUP ON THE NODE, SO NO GROUP TO RETURN"
        return self.wireGroup

    def setWireGroup(self, wireGroup):
        self.wireGroup = wireGroup

    def resetWireGroup(self):
        if self.wireGroup:
            self.wireGroup.resetNodes()

    def goHome(self):
        """Function to centralise the node back to the pin and update any associated rigCurves and pinTies"""
        if self.pin:
            self.setPos(self.pin.pos())
            if self.pinTie:
                self.pinTie().drawTie()
            for rigCurve in self.rigCurveList:
                rigCurve().buildCurve()
        else:
            print "WARNING : NODE HAS NO ASSOCIATED PIN AND AS SUCH HAS NO HOME TO GO TO :("

    def boundingRect(self):
        adjust = 0.0
        return QtCore.QRectF(-self.radius - adjust, -self.radius - adjust,
                             2*self.radius + adjust, 2*self.radius + adjust)

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        # painter.setPen(QtCore.Qt.NoPen)
        cColour = QtGui.QColor(25,25,50,150)
        if self.isSelected(): cColour = QtGui.QColor(220,220,255,150)
        pen = QtGui.QPen(cColour, 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        # painter.setBrush(QtCore.Qt.lightGray)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
        gradient = QtGui.QRadialGradient(0, 0, self.radius/2)
        if option.state & QtGui.QStyle.State_Sunken: # selected
            cColour = QtGui.QColor(50,255,255,150)
            gradient.setColorAt(0, cColour)
            gradient.setColorAt(0.6, cColour)
            gradient.setColorAt(1, QtGui.QColor(cColour.red(), cColour.green(), cColour.blue(), 20))
        else:
            cColour = QtGui.QColor(QtCore.Qt.blue).lighter(120)
            gradient.setColorAt(0, cColour)
            gradient.setColorAt(0.5, cColour)
            gradient.setColorAt(1, QtGui.QColor(cColour.red(), cColour.green(), cColour.blue(), 20))
        painter.setBrush(QtGui.QBrush(gradient))
        QtGui.QPen(QtCore.Qt.black, 1.2, QtCore.Qt.SolidLine)
        painter.drawEllipse(-self.radius/2, -self.radius/2, self.radius, self.radius)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            if self.pinTie:
                self.pinTie().drawTie()
            for rigCurve in self.rigCurveList:
                rigCurve().buildCurve()
        # print "Item new position :" + str(self.pos().x()) + ", " + str(self.pos().y())
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        # if not self.graph().inhibit_edit:
        self.update()
        # print "Node pressed"
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        # if not self.graph().inhibit_edit:
        self.update()
        # print "Node Pos: " + str(self.pos())
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.restraintDef:
            if self.move_restrict_circle.contains(event.scenePos()):
                QtGui.QGraphicsItem.mouseMoveEvent(self, event)
                if self.operatorClass:
                    pass
                    # nodePos = self.pos() - QPVec(self.restraintDef["center"])
                    # # print "Node Pos " + str(self.index) + ": " + str(nodePos.x()) + "," + str(nodePos.y())
                    # self.operatorClass.setPos(npVec(nodePos))
                    # self.operatorClass.mouseMoveExecute() #Execute our defined operator class through the move event
        else: QtGui.QGraphicsItem.mouseMoveEvent(self, event)


###
class RigGraphicsView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self) 
        self.width = 500
        self.height = 500
        self.size = (0, 0, self.width, self.height)
        self.characterImageFile = None
        # self.restraintDef = restraintDef
        self.setAcceptDrops(True)
        # self.colourBroadCaster = ColourBroadcaster(self.iP,self.port)

        f=open('darkorange.stylesheet', 'r')  #Set up Style Sheet for customising anything within the Graphics View
        self.styleData = f.read()
        f.close()

        policy = QtCore.Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        # self.rubberband = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(self.size[0],self.size[1],self.size[2],self.size[3])
        self.setScene(scene)
        # self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        #
        # self.maxtemp = 300
        # self.maxtime = 160
        self.nodeCount = 0
        self.markerCount = 1
        self.markerGuideCount = 0
        self.showMarkerID = True
        self.markerScale = 1.0
        self.markerActiveList = []
        # self.calc_upper_limits()
        #
        self.scale(1,1)
        self.setMinimumSize(500, 500)
        self.setWindowTitle(self.tr("Elastic Nodes"))
        self.inhibit_edit = False

        # self.setBackgroundImage() #Add the character image to the background
        
        #Add in Reflection Line
        self.reflectionLine = self.addReflectionLine()
        self.showReflectionLine = True
        # self.addRigControl([[290,80],[384,137],[424,237],[381,354]])

        #LARGE GROUP ATTRIBUTES
        self.markerList = []
        self.wireGroups = []

        #Test Parenting 
        # cP1 = ControlPin()   
        # cP1.setPos(QtCore.QPointF(20,20))

        # cP2 = ControlPin()   
        # cP2.setPos(QtCore.QPointF(60,20))

        # m1 = GuideMarker()
        # m1.setPos(QtCore.QPointF(20,20))

        # m2 = GuideMarker()
        # m2.setPos(QtCore.QPointF(60,20))

        # m2.setParentItem(m1)
        # self.scene().addItem(m1)
        # self.scene().addItem(m2)
        # self.scene().addItem(cP1)
        # self.scene().addItem(cP2)

    def setBackgroundImage(self):
        """Function to set the validity of a file path, and if it is good then pass it to the Graphics View for drawing"""
        imagePath = QtGui.QFileDialog.getOpenFileName(caption = "Please choose front character face image ~ 500px x 500px", directory="./images" , filter = "*.png")
        if os.path.exists(imagePath):
            self.characterImageFile = imagePath
            print "characterImageFile : " + str(self.characterImageFile)
            characterImage = QtGui.QPixmap(self.characterImageFile)
            self.width = characterImage.width()
            self.height = characterImage.height()
            self.size = [self.size[0],self.size[1], self.width,self.height]
            self.scene().setSceneRect(self.size[0],self.size[1],self.size[2],self.size[3])
            self.updateSceneRect(QtCore.QRectF(self.size[0],self.size[1],self.size[2],self.size[3]))
            self.reflectionLine.remap(self.width, self.height) # Adjust the Positing and height of the reflection line
            self.setMinimumSize(self.width,self.height)
            self.scene().update()
            self.sizeHint()
        else:
            self.characterImageFile = None
            print "WARNING: NOW VALID IMAGE SELECTED FOR CHARACTER BACKGROUND"

    def addReflectionLine(self):
        scene = self.scene()
        refLine = ReflectionLine(self.width,self.height)
        scene.addItem(refLine)
        return refLine

    def setShowReflectionLine(self, state):
        """Function to show/hide the central reflection line"""
        self.reflectionLine.setVisible(state)
        self.reflectionLine.update()

    def findMarkerGuideCount(self):
        """Run through the markers and find the next Guide Index"""
        markerCount = 1

    # def calc_upper_limits(self):
    #     self.toptemp = (self.maxtemp / 100 + 1) * 100
    #     self.toptime = (int(self.maxtime) / 30 + 1) * 30
    #     self.graph_width_ratio = float(self.size[2]) /self.toptime
    #     self.graph_height_ratio = float(self.size[3]) / self.toptemp

    def add_node(self,xPos,yPos, marker=False):
        scene = self.scene()
        # Insert Node into scene
        # colourGrabber = colourGrab(self.colourBroadCaster, radius = self.restraintDef["radius"])
        node = Node(self, xPos, yPos)
        node.setIndex(self.nodeCount)
        # colourGrabber.setIndex(self.nodecount) #Make sure that the Node and the ColourGrabber have neatly setup indexes
        # self.colourBroadCaster.addColourGrab(colourGrabber) #Make sure that the colour grabber is past to the broadcaster
        scene.addItem(node)
        self.nodeCount += 1
        return node

    def add_guideMarker(self,pos):
        """Function to add a new node at the specified position!"""
        newMarker = GuideMarker()
        newMarker.setPos(self.mapToScene(pos))
        self.scene().addItem(newMarker)
        # print "Marker scene Pos : " + str(newMarker.scenePos())
        # print "Marker View pos : " + str(self.mapToScene(pos))
        return newMarker

    def get_ordered_nodes(self):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        nodes.sort(key=lambda n: n.index)
        return nodes

    def addRigControl(self, controlPosList, color = QtGui.QColor(0, 0, 0)):
        scene = self.scene()
        rigCurveNodes = []
        for p in controlPosList:
            newNode = self.add_node(p[0],p[1])
            # ctrlPoint = QtCore.QPointF(p[0], p[1])
            rigCurveNodes.append(newNode)
            # rigCurveNodes.append(ctrlPoint)
        # print "Node List : " + str(rigCurveNodes)
        # for n in rigCurveNodes: print "Node Pos : " + str(n.pos())
        curve = RigCurve(color, rigCurveNodes)
        scene.addItem(curve)

    def drawBackground(self, painter, rect):
        if self.characterImageFile != None:
            backImage = QtGui.QPixmap(self.characterImageFile)
            # backImage.scaled(500,500, QtCore.Qt.KeepAspectRatio)
            painter.drawPixmap(rect, backImage, rect)
            # print "This was drawn"
        sceneRect = self.sceneRect()
        # print "Back image is: " + str(self.characterImageFile)

    def reflectPos(self, pos):
        """Function to find the reflected position of a guide"""
        refLine = self.reflectionLine.pos().x()
        return QtCore.QPointF(refLine - (pos.x() - refLine), pos.y())

    def reflectGuides(self):
        scene = self.scene()
        """Function to find the list of selected Guide Markers and reflect them around the Reflection Line"""
        for item in scene.items():
            if type(item) == GuideMarker and item.isSelected() == True: #Find our selected GuideMarkers
                itemPos = item.pos() #Now build a marker at the reflected position
                newGuidePos = self.reflectPos(itemPos)
                newMarker = GuideMarker()
                newMarker.setIndex(item.getIndex())
                newMarker.setScale(self.markerScale)
                newMarker.setPos(newGuidePos.x(),newGuidePos.y())
                self.markerList.append(newMarker)
                scene.addItem(newMarker)

    def setMarkerScale(self, scale):
        """Function to cycle through markers and scale"""
        scene = self.scene()
        for item in scene.items():
            if type(item) == GuideMarker: #change the state of its show ID
                item.setScale(float(scale/100.0))
                item.update()
        self.markerScale = float(scale/100.0)  

    def processMarkerActiveIndex(self):
        itemPresent = False
        for index, item in enumerate(self.markerActiveList):
            item.setActiveIndex(index)

    def processMarkerSelection(self, marker):
        itemPresent = False
        for item in self.markerActiveList:
            if marker == item: 
                itemPresent = True

        if itemPresent:
            if len(self.markerActiveList) > 1 :
                self.markerActiveList.remove(marker)
                marker.setActive(False) 
            elif len(self.markerActiveList) == 1: #The list only contains this master so clear the list to be empty and deactivate the marker
                self.markerActiveList = []
                marker.setActive(False)
        else: #the item is not present so we we just need to add it to the list
            self.markerActiveList.append(marker)
            marker.setActive(True)
        self.processMarkerActiveIndex()

    def processMarkerDelete(self, marker):
        itemPresent = False
        for item in self.markerActiveList:
            if marker == item: #the interacted item is in the list, so check if ctrl is pressed
                itemPresent = True

        if itemPresent: #the item is in the list so we need to remove it or, reset the list to empty
            if len(self.markerActiveList) > 1 :
                self.markerActiveList.remove(marker)
                marker.setActive(False)
            else: 
                self.markerActiveList = []
                marker.setActive(False)
        self.markerList.remove(marker) #Remove the marker from the main marker list


    def addWireGroup(self):
        """Function that looks at the makerSelection List and tried to build a Wire Rig"""
        if len(self.markerActiveList) > 2:
            posList = []
            for m in self.markerActiveList: posList.append(m.pos())
            newWireGroup = WireControlGroup(posList, self)
            self.wireGroups.append(newWireGroup)
            for m in self.markerActiveList: 
                m.setActive(False) 
                m.setSelected(False) #Deactivate all markers and deselect them
            self.markerActiveList = [] #Reset the Marker List
        else:
            print "WARNING : THERE ARE NOT ENOUGH MARKERS SELECTED TO CREATE A WIRE GROUP"


    def showItem(self,state,objectType):
        """Function to hide and show markers"""
        scene = self.scene()
        for item in scene.items():
            if type(item) == objectType: #change the state of its show ID
                item.setVisible(state)
                item.update()
            if objectType == Node and type(item) == PinTie:
                item.setVisible(state)
                item.update()
            if objectType == ControlPin and type(item) == PinTie:
                item.setVisible(state)
                item.update()

    def selectFilter(self, state, objectType):
        """A function to control whether items can be selected or not"""
        scene = self.scene()
        for item in scene.items():
            if type(item) == objectType: #change the state of its show ID        
                item.setFlag(QtGui.QGraphicsItem.ItemIsMovable,state)
                item.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,state)
                item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,state)
                if not state: item.setSelected(state)



        #     if ctrl: #ctrl is pressed so  we are deselecting the item and removing from the list
        #         print "length : " + str(len(self.markerActiveList))
        #         if len(self.markerActiveList) > 1 : 
        #             self.markerActiveList.remove(marker)
        #             print "ran if"
        #         else: 
        #             self.markerActiveList = ["ctrlCase"] # Special Case where we are deselecting the only selected marker with a ctrl click
        #             print "ran else"
        #     else: self.markerActiveList = [marker] #ctrl not pressed, so we are starting a new clean list with the marker
        # else: #the item is not present in the list
        #     if ctrl: self.markerActiveList.append(marker) #append the 
        #     else: self.markerActiveList = [marker] #ctrl not pressed, so we are starting a new clean list with the marker
        # # print str(self.markerActiveList)

    def clear(self):
        self.scene().clear() # Clear the scene of all items
        self.reflectionLine = None
        self.markerList = []
        self.markerActiveList = []
        self.wireGroups = []
        self.reflectionLine = self.addReflectionLine()

    def store(self, XMLFile):
        """Function to store all the contents of the Graphics View and write it out to a giant XML File - Work through all elements and Store"""
        GVRoot = xml.Element('faceRigGraphicsView')
        sceneItems = xml.SubElement(GVRoot,'sceneItems')
        for m in self.markerList:
            markerXML = m.store()
            # xml.tostring(markerXML)
            sceneItems.append(markerXML)
        GVXml = FileControl.XMLMan()
        GVXml.setTree(GVRoot)
        GVXml.setFile(XMLFile)
        GVXml.save()
        # print xml.tostring(GVRoot)

    def read(self, XMLFile):
        """Function to read in an entirely new Face Rig Graphics View"""
        scene = self.scene()
        GVXml = FileControl.XMLMan()
        GVXml.setLoad(XMLFile)
        GVMarkers = GVXml.findBranch("GuideMarker")
        for m in GVMarkers:
            newMarker = GuideMarker()
            newMarker.read(m)
            scene.addItem(newMarker)
            self.markerList.append(newMarker) #Add Marker to marker List
            # I Active then it should be added to the Active Marker List too!
            if newMarker.getActive(): self.markerActiveList.append(newMarker)
        self.markerActiveList.sort(key=lambda x: x.getActiveIndex())
        self.processMarkerActiveIndex()  #Update all active states    

    def keyPressEvent(self, event):
        scene = self.scene()
        key = event.key()
        if key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == QtCore.Qt.Key_Delete:
            for item in scene.items():
                if type(item) == GuideMarker and item.isSelected() == True: #Delete out any GuideMarkers that are selection and need to be removed
                    self.processMarkerDelete(item)
                    scene.removeItem(item)
                    del item
            self.processMarkerActiveIndex()
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    # def mousePressEvent(self, event):
    #     # print "GraphWidget mouse"
    #     # print "Mouse clicked - Maybe add a marker?"
    #     modifiers = QtGui.QApplication.keyboardModifiers()
    #     if modifiers == QtCore.Qt.ControlModifier:
    #         #ctrl is pressed so add a marker
    #         mousePos = event.pos()
    #         self.add_guideMarker(mousePos)
    #     QtGui.QGraphicsView.mousePressEvent(self, event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def dragEnterEvent(self, event):
        """Function to overider dragEnterEvent to check that text is being used"""
        if (event.mimeData().hasFormat('text/plain')):
            data = QtCore.QString(event.mimeData().data('text/plain'))
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Function to overider dragMoveEvent to check that text is being used"""
        if event.mimeData().hasFormat("text/plain"):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event): 
        """Function to overider dropEvent to check text has arrived and add it to the graphicsView as appropriate"""
        if (event.mimeData().hasFormat('text/plain')):
            event.acceptProposedAction()
            #Create a new QGraphicsItem and transfer the text across so we have the correct name
            data = QtCore.QString(event.mimeData().data("text/plain"))
            item = buildGuideItem(data)
            item.setIndex(self.markerCount)
            item.setPos(self.mapToScene(event.pos()))
            item.setScale(self.markerScale)
            item.setShowID(self.showMarkerID)
            self.markerList.append(item) #Add Item to the main Marker list
            self.scene().addItem(item)
            print self.markerList
            # item.store()

            # xml = FileControl.XMLMan()
            # xml.setLoad('FaceFiles/test.xml')
            # item.read(xml.getTree())
            self.markerCount += 1
        else:
            event.ignore() 

    # def mousePressEvent(self, mouseEvent):
    #     scene = self.scene()
    #     selGuides = []
    #     if mouseEvent.button() == QtCore.Qt.LeftButton:
    #         possibleItems = self.items(mouseEvent.pos())
    #         for item in possibleItems:
    #            if type(item) == GuideMarker: selGuides.append(item) #The first item in this list is the top layer item, and always the one that is interacted with
        
    #     modifiers = QtGui.QApplication.keyboardModifiers()
    #     ctrlPressed = (modifiers == QtCore.Qt.ControlModifier) #detect if ctrl is being pressed
    #     if len(selGuides) != 0: self.processMarkerSelection(selGuides[0], ctrlPressed) #Check there is an item selected
    #     else: self.markerActiveList = [] # No item Marker has been selected so the selection list is cleared.
    #     # markerIndexes = []
    #     # for item in self.markerActiveList: markerIndexes.append(item.getIndex())
    #     # print str(markerIndexes)
    #     return QtGui.QGraphicsView.mousePressEvent(self, mouseEvent)

    def mouseDoubleClickEvent(self, mouseEvent):
        scene = self.scene()
        selGuides = []
        possibleItems = self.items(mouseEvent.pos())
        if mouseEvent.button() == QtCore.Qt.LeftButton:    #Left Double click on a Marker to activate or deactivate it
            for item in possibleItems:
               if type(item) == GuideMarker: selGuides.append(item)

        if len(selGuides) > 0 :
            self.processMarkerSelection(selGuides[0])
            self.processMarkerActiveIndex()
            return QtGui.QGraphicsView.mouseDoubleClickEvent(self, mouseEvent)

        if mouseEvent.button() == QtCore.Qt.MiddleButton:  #Send a Node back to its Pin with a Double Right button click
            for item in possibleItems:
               if type(item) == Node: 
                    item.goHome()
        return QtGui.QGraphicsView.mouseDoubleClickEvent(self, mouseEvent)


    def contextMenuEvent(self, event):
        scene = self.scene()
        items = self.items(event.pos())
        if len(items) != 0:
            if type(items[0]) == GuideMarker:
                self.guideMarkerContextMenu(event,items[0])
            elif type(items[0]) == Node:
                self.nodeContextMenu(event,items[0])
            elif type(items[0]) == ControlPin:
                pass
            elif type(items[0]) == ReflectionLine:
                self.reflectionLineContextMenu(event,items[0])
                # menu.addAction('ControlPin')

    def reflectionLineContextMenu(self,event,item):
        scene = self.scene()
        menu = QtGui.QMenu()
        menu.setStyleSheet(self.styleData)
        if item.getAdjustable():
            menu.addAction('Lock')
        else:
            menu.addAction('Unlock')
        action = menu.exec_(event.globalPos())
        if action:
            if action.text() == 'Lock': self.reflectionLine.setAdjustable(False)
            elif action.text() == 'Unlock': self.reflectionLine.setAdjustable(True)

    def guideMarkerContextMenu(self,event,item):
        scene = self.scene()
        menu = QtGui.QMenu()
        menu.setStyleSheet(self.styleData)
        if item.getActive():
            menu.addAction('Deactivate')
        else:
            menu.addAction('Activate')
        menu.addSeparator()   
        menu.addAction('Delete')
        menu.addAction('Hide')
        action = menu.exec_(event.globalPos())
        if action:
            if action.text() == 'Deactivate' or action.text() == 'Activate':
                item.setActive(not item.getActive())
            elif action.text() == 'Delete':
                self.processMarkerDelete(item)
                scene.removeItem(item)
                del item
            elif action.text() == 'Hide':
                item.setVisible(False)


    def nodeContextMenu(self,event,item):
        scene = self.scene()
        menu = QtGui.QMenu()
        menu.setStyleSheet(self.styleData)
        menu.addAction('Go Home')
        menu.addSeparator()
        menu.addAction('Reset Wire Group')
        action = menu.exec_(event.globalPos())
        if action:
            if action.text() == 'Go Home':
                item.goHome()
            if action.text() == 'Reset Wire Group':
                item.resetWireGroup()

    # def mouseReleaseEvent(self, mouseEvent):
    #     if len(self.scene().selectedItems()) > 0 and len(self.markerActiveList) == 0: #A drag selection has occured. reset Marker list to selection
    #         for marker in self.scene().selectedItems():
    #             self.markerActiveList.append(marker)

    #     if self.markerActiveList[0] == "ctrlCase": self.markerActiveList = [] #Sepcial case where last selected item has been deselected with a ctrl click

    #     markerIndexes = []
    #     for item in self.markerActiveList: markerIndexes.append(item.getIndex())
    #     print str(markerIndexes)
    #     return QtGui.QGraphicsView.mouseReleaseEvent(self, mouseEvent)
