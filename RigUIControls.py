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
        self.startPos = npVec(startNode().scenePos())
        self.endPos = npVec(endNode().scenePos())
        self.targPos = npVec(targNode().scenePos())
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

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        ReflectionLineRoot = xml.Element('ReflectionLine')
        attributes = xml.SubElement(ReflectionLineRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'width', value = str(self.getWidth()))
        xml.SubElement(attributes, 'attribute', name = 'height', value = str(self.getHeight()))
        xml.SubElement(attributes, 'attribute', name = 'inset', value = str(self.getInset()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        return ReflectionLineRoot

    def read(self, ReflectionLineXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        # ReflectionLineRoot = ReflectionLineXml.getroot()
        for a in ReflectionLineXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'width': self.setWidth(float(a.attrib['value']))
            elif a.attrib['name'] == 'height': self.setHeight(float(a.attrib['value']))
            elif a.attrib['name'] == 'inset': self.setInset(float(a.attrib['value']))
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))
        self.setDraw()
        self.update()

    def getWidth(self):
        return self.width

    def setWidth(self,width):
        self.width = width

    def getHeight(self):
        return self.height

    def setHeight(self,height):
        self.height = height

    def getInset(self):
        return self.inset

    def setInset(self, inset):
        self.inset = inset

    def setDraw(self):
        self.drawStart = [0, -self.height/2 + self.inset]
        self.drawEnd = [0, self.height/2 - self.inset]      

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

class WireGroup():
    def __init__(self, rigGView):
        #LIST OF ATTRIBUTES
        self.name = ""
        self.colour = QtGui.QColor(0,0,0)
        self.scale = 1.0 #Not implemented, but it is stored, so could be used to drive the size of the setup of the wiregroup
        self.pinPositions = []
        self.visibility = True
        self.pins = []
        self.nodes = []
        self.pinTies = []
        self.curve = None
        self.scene = rigGView.scene()
        # self.initBuild()

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        wireRoot = xml.Element('WireGroup')
        attributes = xml.SubElement(wireRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'name', value = str(self.getName()))
        xml.SubElement(attributes, 'attribute', name = 'colour', value = (str(self.colour.red()) + "," + str(self.colour.green()) + "," + str(self.colour.blue())))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))

        #Now record the xml for the Nodes
        wireNodes = xml.SubElement(wireRoot,'nodes')
        for n in self.nodes:
            nodeXml = n.store()
            wireNodes.append(nodeXml)
        #Now record the xml for the Pins - pinTies should be able to be drawn from the resulting data of nodes and pins
        wirePins = xml.SubElement(wireRoot,'pins')
        for p in self.pins:
            pinXml = p.store()
            wirePins.append(pinXml)
        return wireRoot

    def read(self, wireXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in wireXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'name': self.setName(a.attrib['value'])
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'colour': 
                newColour = a.attrib['value'].split(",")
                self.setColour(QtGui.QColor(int(newColour[0]), int(newColour[1]),int(newColour[2])))

        #Now read in and generate all the nodes
        self.clear() #Clear out all items, safely deleting everything from the scene and destroying objects

        pins = wireXml.findall('pins')
        for p in pins[0].findall('pin'):
            newPin = ControlPin(QPVec([0,0])) #Create new Node with Arbitrary pos
            self.pins.append(newPin)
            newPin.read(p)
            self.scene.addItem(newPin)
        nodes = wireXml.findall('nodes')
        for n in nodes[0].findall('node'):
            newNode = Node(QPVec([0,0])) #Create new Node with Arbitray pos
            self.nodes.append(newNode)
            newNode.read(n)
            newNode.setPin(self.findPin(newNode.getPinIndex()))
            newNode.setWireGroup(self)
            # self.scene.addItem(newNode)
        self.createPinTies() #Now nodes and Pins are in Place we can create the pinTies
        self.createCurve() #UPGRADE: Possibly to include a series of smaller curves, not a giant clumsy one

    def buildFromPositions(self , pinQPointList):
        self.pinPositions = pinQPointList
        self.createPins()
        self.createNodes()
        self.createPinTies()
        self.createCurve() #UPGRADE: Possibly to include a series of smaller curves, not a giant clumsy one

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = str(newName)

    def getColour(self):
        return self.colour

    def setColour(self,colour):
        self.colour = colour

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale
        #Now update the scale of all items
        for n in self.nodes: n.setScale(scale)
        for p in self.pins: p.setScale(scale)

    def isVisible(self):
        return self.visibility

    def setVisible(self, visibility):
        self. visibility = visibility

    def createPins(self):
        """Initially place the pins according to markers given, and fill out self.pins"""
        self.pins = []
        for index,p in enumerate(self.pinPositions):
            cP = ControlPin(p)   
            cP.setIndex(index)
            cP.setWireGroup(self)
            self.pins.append(cP)
            self.scene.addItem(cP)

    def createNodes(self):
        self.nodes = []
        for index, p in enumerate(self.pins):
            # node = Node(p.pos())
            node = Node(QtCore.QPointF(0,0))
            node.setIndex(p.getIndex())
            node.setPin(p)
            node.setWireGroup(self)
            self.nodes.append(node)
            # self.scene.addItem(node)

    def createPinTies(self):
        self.pinTies = []
        if len(self.pins) > 1 and len(self.pins) == len(self.nodes):
            for index, n in enumerate(self.nodes):
                pin = self.findPin(n.getPinIndex())
                if pin:
                    pT = PinTie(n, pin)
                    pT.setIndex(pin.getIndex()) #Make the tie Index the same as the pins
                    # n.setPinIndex(index)
                    self.pinTies.append(pT)
                    n.setPinTie(pT)
                    self.scene.addItem(pT)
                else: print "WARNING : NO PIN TIES DRAWN SINCE NO MATCHING PIN WAS FOUND FOR NODE"
        else:
            print "WARNING : NO PIN TIES DRAWN SINCE THERE WERE INSUFFICIENT NODES OR UNEQUAL NODES AND PINS"

    def createCurve(self):
        if len(self.nodes) > 2:
            self.curve = RigCurve(self.colour, self.nodes)
            self.scene.addItem(self.curve)

    def findNode(self,index):
        for n in self.nodes:
            if n.getIndex() == index:
                return n

    def findPin(self,index):
        for p in self.pins:
            if p.getIndex() == index:
                return p

    def resetNodes(self):
        for node in self.nodes:
            node.goHome()

    def clear(self):
        for n in self.nodes:
            self.scene.removeItem(n)
            del n
        for p in self.pins:
            self.scene.removeItem(p)
            del p
        for pT in self.pinTies:
            self.scene.removeItem(pT)
            del pT
        if self.curve: 
            self.scene.removeItem(self.curve)
            del self.curve
        self.nodes = []
        self.pins = []
        self.pinTiles = []
        self.curve = None 


class ControlPin(QtGui.QGraphicsItem):
    def __init__(self, cPos, control = None):
        super(ControlPin, self).__init__()
        # self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.index = 0 
        self.scale = 1
        self.scaleOffset = 2.5
        self.wireGroup = None

        self.setPos(cPos)
        self.setZValue(1) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.


    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        pinRoot = xml.Element('pin')
        attributes = xml.SubElement(pinRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'scaleOffset', value = str(self.getScaleOffset()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        return pinRoot

    def read(self, nodeXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in nodeXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'scaleOffset': self.setScaleOffset(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

    def setIndex(self,value):
        self.index = value

    def getIndex(self):
        return self.index

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getScaleOffset(self):
        return self.scaleOffset

    def setScaleOffset(self, scaleOffset):
        self.scaleOffset = scaleOffset

    def getWireGroup(self):
        return self.wireGroup

    def setWireGroup(self, wireGroup):
        self.wireGroup = wireGroup

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
        # self.setParentItem(self.startNode) # consider implemeting a tie as a child of the pin

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
        self.midPoint =  (self.startNode().scenePos() + self.endNode().scenePos())/2
        self.startPoint = self.startNode().scenePos() - self.midPoint 
        self.endPoint = self.endNode().scenePos() - self.midPoint #+ QtCore.QPointF(20,20)


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
                # print "guide index : " + str(self.guideIndex)
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
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)

        self.index = 0
        self.radius = 8
        self.rigCurveList = []
        self.bezierHandles = [None, None]

        self.scaleOffset = 7
        self.scale = 1.0
        # self.pin.append(weakref.ref(pin))
        self.pin = None
        self.pinIndex = None

        self.pinTie = None
        self.pinTieIndex = None

        self.wireGroup = None
        
        self.restraintDef = restraintDef
        self.move_restrict_circle = None
        self.operatorClass = operatorClass

        # if self.restraintDef:
        #     self.move_restrict_circle = QtGui.QGraphicsEllipseItem(2*self.restraintDef["centerOffset"][0],2*self.restraintDef["centerOffset"][1], 2*self.restraintDef["radius"],2*self.restraintDef["radius"])
        # offsetPos = self.pos() - QPVec(self.restraintDef["center"])
        self.setPos(nPos)
        if self.operatorClass:
            self.operatorClass.setPos([offsetPos.x(),offsetPos.y()]) #Set colourGrabber position
            self.operatorClass.mouseMoveExecute() # Set the initial colour

        self.setZValue(12) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        nodeRoot = xml.Element('node')
        attributes = xml.SubElement(nodeRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'radius', value = str(self.getRadius()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'pinIndex', value = str(self.getPinIndex()))
        xml.SubElement(attributes, 'attribute', name = 'pinTieIndex', value = str(self.getPinTieIndex()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        if self.getBezierHandles(0) != None: xml.SubElement(attributes, 'attribute', name = 'bezierHandle0', value = (str(self.getBezierHandles(0)[0]) + "," + str(self.getBezierHandles(0)[1])))
        else: xml.SubElement(attributes, 'attribute', name = 'bezierHandle0', value = ("None"))
        if self.getBezierHandles(1) != None: xml.SubElement(attributes, 'attribute', name = 'bezierHandle1', value = (str(self.getBezierHandles(1)[0]) + "," + str(self.getBezierHandles(1)[1])))
        else: xml.SubElement(attributes, 'attribute', name = 'bezierHandle1', value = ("None"))

        return nodeRoot

    def read(self, nodeXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in nodeXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'radius': self.setRadius(float(a.attrib['value']))
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'pinIndex': self.setPinIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'pinTieIndex': self.setPinTieIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))
            elif a.attrib['name'] == 'bezierHandle0': 
                if a.attrib['value'] != "None":
                    newPos = a.attrib['value'].split(",")
                    self.setBezierHandles([float(newPos[0]), float(newPos[1])],0)
                else: self.setBezierHandles(None,0)
            elif a.attrib['name'] == 'bezierHandle1': 
                if a.attrib['value'] != "None":
                    newPos = a.attrib['value'].split(",")
                    self.setBezierHandles([float(newPos[0]), float(newPos[1])],1)
                else: self.setBezierHandles(None,1)

    def setIndex(self,value):
        self.index = value

    def getIndex(self):
        return self.index

    def getRadius(self):
        return self.radius

    def setRadius(self, radius):
        self.radius = radius

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getPinIndex(self):
        return self.pinIndex

    def setPinIndex(self, index):
        self.pinIndex = index

    def getPinTieIndex(self):
        return self.pinTieIndex

    def setPinTieIndex(self, index):
        self.pinTieIndex = index


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
            self.setPinIndex(pin.getIndex())
            self.setParentItem(pin)
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PIN ALLOCATION"

    def getPinTie(self):
        return self.pinTie

    def setPinTie(self, pinTie):
        if type(pinTie) == PinTie:
            self.pinTie = weakref.ref(pinTie)
            self.setPinTieIndex(pinTie.getIndex())
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
            self.setPos(QtCore.QPointF(0,0))
            if self.pinTie:
                self.pinTie().drawTie()
            for rigCurve in self.rigCurveList:
                rigCurve().buildCurve()
        else:
            print "WARNING : NODE HAS NO ASSOCIATED PIN AND AS SUCH HAS NO HOME TO GO TO :("

    def boundingRect(self):
        adjust = 0.0
        return QtCore.QRectF((-self.radius - adjust)*self.scale, (-self.radius - adjust)*self.scale,
                             (2*self.radius + adjust)*self.scale, (2*self.radius + adjust)*self.scale)

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        # painter.setPen(QtCore.Qt.NoPen)
        cColour = QtGui.QColor(25,25,50,150)
        if self.isSelected(): cColour = QtGui.QColor(220,220,255,150)
        pen = QtGui.QPen(cColour, 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        # painter.setBrush(QtCore.Qt.lightGray)
        painter.drawEllipse(-self.radius*self.scale, -self.radius*self.scale, 2*self.radius*self.scale, 2*self.radius*self.scale)
        gradient = QtGui.QRadialGradient(0, 0, self.scale*self.radius/2)
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
        painter.drawEllipse((-self.radius/2)*self.scale, (-self.radius/2)*self.scale, self.radius*self.scale, self.radius*self.scale)

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
###########################################################################################################################
#RESTRICTION ITEMS
class OpsRotation(QtGui.QGraphicsItem):
    def __init__(self, constraintItem):
        QtGui.QGraphicsItem.__init__(self)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,False)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.scale = 1.0
        self.length = 10
        self.constraintItem = constraintItem
        self.setZValue(9)

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scaleOffset

    def getLength(self):
        return self.length

    def setLength(self,length):
        self.length = length

    def boundingRect(self):
        adjust = 10
        return QtCore.QRectF(self.scale*(-self.length - adjust), self.scale*(-self.length - adjust),
                             self.scale*(2*self.length + adjust), self.scale*(2*self.length + adjust))       

    def paint(self, painter, option, widget):
        wCurve1 = QtGui.QPainterPath()

        locAx = -7.8 * self.scale
        locAy = -2 * self.scale

        locBx = -4 * self.scale
        locBy = 0 * self.scale

        pen = QtGui.QPen(QtCore.Qt.red, 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        wCurve1 = QtGui.QPainterPath()
        wCurve1.moveTo(QtCore.QPointF(locAx,-locAy))
        wCurve1.cubicTo(QtCore.QPointF(locBx,-locBy),QtCore.QPointF(-locBx,-locBy),QtCore.QPointF(-locAx,-locAy))
        painter.strokePath(wCurve1, painter.pen())
        
        pen = QtGui.QPen(QtCore.Qt.red, 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(locAx-0.5,-locAy,locAx+2,-locAy+1)
        painter.drawLine(locAx-0.5,-locAy,locAx+1,-locAy-2)

        painter.drawLine(-locAx+0.5,-locAy,-locAx-2,-locAy+1)
        painter.drawLine(-locAx+0.5,-locAy,-locAx-1,-locAy-2)


class OpsCross(QtGui.QGraphicsItem):
    def __init__(self, constraintItem):
        QtGui.QGraphicsItem.__init__(self)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.scale = 1.0
        self.length = 4
        self.constraintItem = constraintItem
        self.setZValue(9)

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scaleOffset

    def getLength(self):
        return self.length

    def setLength(self,length):
        self.length = length

    def boundingRect(self):
        adjust = 0
        return QtCore.QRectF(self.scale*(-self.length - adjust), self.scale*(-self.length - adjust),
                             self.scale*(2*self.length + adjust), self.scale*(2*self.length + adjust))        

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtGui.QColor(255,0,0,200), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.scale*-self.length,0,self.scale*self.length,0)
        painter.drawLine(0,self.scale*self.length,0,self.scale*-self.length)

    def mousePressEvent(self, event):
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.parentItem():
            self.prepareGeometryChange()
            self.constraintItem.redraw(self.pos())
            self.update()
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.parentItem():
            self.prepareGeometryChange()
            self.constraintItem.redraw(self.pos())
            self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)


class ConstraintEllipse(QtGui.QGraphicsEllipseItem):
    def __init__(self, w, h):
        QtGui.QGraphicsEllipseItem.__init__(self, -w/2, -h/2, w, h) 
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.scale = 1.0
        self.width = w/2
        self.height = h/2
        self.extension = 15.0
        self.opX = None
        self.opRot = None
        self.setZValue(1)
        self.initBuild()

    def initBuild(self):
        self.opX = OpsCross(self)
        self.opX.setParentItem(self)
        self.opX.setPos(QtCore.QPointF(self.width,-self.height))

        self.opRot = OpsRotation(self)
        self.opRot.setParentItem(self)
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))
        self.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25))) #shade in the circle

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getHeight(self):
        return self.height

    def setHeight(self,height):
        self.height = height

    def boundingRect(self):
        adjust = 0.0
        return QtCore.QRectF(self.scale*(-self.width - adjust), self.scale*(-self.height - adjust - self.extension),
                             self.scale*(2*self.width + adjust), self.scale*(2*self.height + adjust + 2*self.extension))

    def paint(self, painter, option, widget):
        QtGui.QGraphicsEllipseItem.paint(self, painter, option, widget)
        pen = QtGui.QPen(QtGui.QColor(0,0,0), 0.5, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawLine(0,self.scale*self.height+self.extension,0,self.scale*-self.height-self.extension) 
        pen = QtGui.QPen(QtGui.QColor(0,0,0), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(-5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))     
        painter.drawLine(5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension)) 


    def redraw(self, dimPos):
        self.width = abs(dimPos.x())
        self.height = abs(dimPos.y())
        self.setRect(self.scale*(-self.width), self.scale*(-self.height),
                             self.scale*(2*self.width), self.scale*(2*self.height)) 
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))

   
class ConstraintRect(QtGui.QGraphicsRectItem):
    def __init__(self, w, h):
        QtGui.QGraphicsRectItem.__init__(self, -w/2, -h/2, w, h) 
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.scale = 1.0
        self.width = w/2
        self.height = h/2
        self.extension = 15.0
        self.opX = None
        self.setZValue(1)
        self.initBuild()

    def initBuild(self):
        self.opX = OpsCross(self)
        self.opX.setParentItem(self)
        self.opX.setPos(QtCore.QPointF(self.width,-self.height))
        
        self.opRot = OpsRotation(self)
        self.opRot.setParentItem(self)
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))
        self.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25))) #shade in the circle
    # def paint(self, painter, option, widget):
    #     painter.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25)))
    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getHeight(self):
        return self.height

    def setHeight(self,height):
        self.height = height

    def boundingRect(self):
        adjust = 0.0
        return QtCore.QRectF(self.scale*(-self.width - adjust), self.scale*(-self.height - adjust - self.extension),
                             self.scale*(2*self.width + adjust), self.scale*(2*self.height + adjust + 2*self.extension))

    def paint(self, painter, option, widget):
        QtGui.QGraphicsRectItem.paint(self, painter, option, widget)
        pen = QtGui.QPen(QtGui.QColor(0,0,0), 0.5, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawLine(0,self.scale*self.height+self.extension,0,self.scale*-self.height-self.extension) 
        pen = QtGui.QPen(QtGui.QColor(0,0,0), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(-5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))     
        painter.drawLine(5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))

    def redraw(self, dimPos):
        self.width = abs(dimPos.x())
        self.height = abs(dimPos.y())
        self.setRect(self.scale*(-self.width), self.scale*(-self.height),
                             self.scale*(2*self.width), self.scale*(2*self.height))  
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))

###########################################################################################################################
class RigGraphicsView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self) 
        self.width = 500
        self.height = 500
        self.size = (0, 0, self.width, self.height)
        self.setAcceptDrops(True)

        f=open('darkorange.stylesheet', 'r')  #Set up Style Sheet for customising anything within the Graphics View
        self.styleData = f.read()
        f.close()

        policy = QtCore.Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(self.size[0],self.size[1],self.size[2],self.size[3])
        self.setScene(scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        self.scale(1,1)
        self.setMinimumSize(500, 500)
        self.setWindowTitle(self.tr("Elastic Nodes"))
        self.inhibit_edit = False

        # View Settings
        self.backgroundImage = None

        self.markerCount = 1
        self.markerScale = 1.0
        self.markerActiveList = []   #Do not need to store this in XML since we can find the actual markers that have an

        #Add in Reflection Line
        self.reflectionLine = self.addReflectionLine()
        self.showReflectionLine = True

        #LARGE GROUP ATTRIBUTES
        self.markerList = []
        self.wireGroups = []

        #TESTING ADDING NEW ITEMS
        el = ConstraintEllipse(80,80)
        el.setPos(200,200)

        rect = ConstraintRect(80,90)
        rect.setPos(400,300)

        self.scene().addItem(el)
        self.scene().addItem(rect)

    def getBackgroundImage(self):
        return self.backgroundImage

    def setBackgroundImage(self, image):
        if image:   
            if os.path.exists(image):
                self.backgroundImage = image
            else: self.backgroundImage = None
        else: self.backgroundImage = None

    def getMarkerCount(self):
        return self.markerCount

    def setMarkerCount(self, markerCount):
        self.markerCount = markerCount

    def getMarkerScale(self):
        return self.markerScale

    def setMarkerScaleSlider(self, scale):
        """Function to cycle through markers and scale"""
        scene = self.scene()
        for item in scene.items():
            if type(item) == GuideMarker: #change the state of its show ID
                item.setScale(float(scale/100.0))
                item.update()
        self.markerScale = float(scale/100.0)

    def setMarkerScale(self,markerScale):
        self.markerScale = markerScale

    def getReflectionLine(self):
        return self.reflectionLine

    def setReflectionLine(self, reflectionLine):
        self.reflectionLine = reflectionLine

    def getMarkerList(self):
        return self.markerList

    def getWireGroups(self):
        return self.wireGroups

    def loadBackgroundImage(self):
        imagePath = QtGui.QFileDialog.getOpenFileName(caption = "Please choose front character face image ~ 500px x 500px", directory="./images" , filter = "*.png")
        if os.path.exists(imagePath):
            self.backgroundImage = imagePath 
            self.setupBackground() 


    def setupBackground(self, remap = True):
        """Function to set the validity of a file path, and if it is good then pass it to the Graphics View for drawing"""
        if self.backgroundImage:
            characterImage = QtGui.QPixmap(self.backgroundImage)
            self.width = characterImage.width()
            self.height = characterImage.height()
            self.size = [self.size[0],self.size[1], self.width,self.height]
            self.scene().setSceneRect(self.size[0],self.size[1],self.size[2],self.size[3])
            self.updateSceneRect(QtCore.QRectF(self.size[0],self.size[1],self.size[2],self.size[3]))
            if remap: self.reflectionLine.remap(self.width, self.height) # Adjust the Positing and height of the reflection line
            self.setMinimumSize(self.width,self.height)
            self.scene().update()
            self.sizeHint()


    def addReflectionLine(self):
        scene = self.scene()
        refLine = ReflectionLine(self.width,self.height)
        scene.addItem(refLine)
        return refLine

    def setShowReflectionLine(self, state):
        """Function to show/hide the central reflection line"""
        self.reflectionLine.setVisible(state)
        self.reflectionLine.update()

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

    def drawBackground(self, painter, rect):
        if self.backgroundImage != None:
            backImage = QtGui.QPixmap(self.backgroundImage)
            # backImage.scaled(500,500, QtCore.Qt.KeepAspectRatio)
            painter.drawPixmap(rect, backImage, rect)
            # print "This was drawn"
        sceneRect = self.sceneRect()
        # print "Back image is: " + str(self.backgroundImage)

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
            newWireGroup = WireGroup(self)
            newWireGroup.buildFromPositions(posList)
            newWireGroup.setScale(self.markerScale)
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

    def clear(self, isReflectionLine = True):
        self.scene().clear() # Clear the scene of all items
        self.setBackgroundImage(None)
        self.reflectionLine = None
        self.markerList = []
        self.markerActiveList = []
        self.wireGroups = []
        if isReflectionLine: self.reflectionLine = self.addReflectionLine()

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
            self.markerList.append(item) #Add Item to the main Marker list
            self.scene().addItem(item)
            # print self.markerList
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


class FaceGVCapture():
    def __init__(self, faceGView):
        """Class to capture all of the information out of the Graphics View"""
        self.view = faceGView
        self.scene = self.view.scene()
        self.viewXML = None
        self.xMLFile = None

    def setXMLFile(self,xMLFile):
        self.xMLFile = xMLFile
        self.setTree()

    def setTree(self):
        self.viewXML = FileControl.XMLMan()
        self.viewXML.setLoad(self.xMLFile)        

    def store(self):
        if self.xMLFile:
            self.viewXML = FileControl.XMLMan()
            self.viewXML.tree = xml.Element('faceRigGraphicsView')
            self.viewSettings = xml.SubElement(self.viewXML.tree,'viewSettings')
            self.sceneItems = xml.SubElement(self.viewXML.tree,'sceneItems')

            self.captureBackgroundImage() #Record the background Image
            self.captureViewSettings() # Capture remainng View settings
            self.captureReflectionLine()
            self.captureMarkers()
            self.captureWireGroups()

            #Now we have captured everything into a super giant XML tree we need to save this out.
            self.viewXML.setFile(self.xMLFile)
            self.viewXML.save()
        else: print "WARNING : COULD NOT SAVE FACE RIG TO FILE, SINCE A VALID FILE NAME WAS NOT SUPPLIED"

    def read(self):
        if self.viewXML:
            scene = self.view.scene()
            self.view.clear(isReflectionLine = False) #Clear the entire Graphics View, including reflection Line

            self.readBackgroundImage()
            self.readViewSettings()
            self.readRelectionLine()
            self.readMarkers()
            self.readWireGroups()
        else: print "WARNING : COULD NOT LOAD FACE RIG, SINCE A VALID FILE NAME WAS NOT SUPPLIED"

    def captureBackgroundImage(self):
        """Function to process background Image into XML"""
        backgroundImage = xml.SubElement(self.viewSettings, 'attribute', name = 'backgroundImage', value = str(self.view.getBackgroundImage()))

    def readBackgroundImage(self):
        """Function to process background Image from XML"""
        viewSettings = self.viewXML.findBranch("viewSettings")[0]
        for a in viewSettings.findall( 'attribute'):
            if a.attrib['name'] == 'backgroundImage': self.view.setBackgroundImage(str(a.attrib['value']))
        self.view.setupBackground(remap = False) # Do not remap the reflection Line since it does not exist yet! 

    def captureViewSettings(self):
        """Function to process View Settings into XML"""
        markerCount = xml.SubElement(self.viewSettings, 'attribute', name = 'markerCount', value = str(self.view.getMarkerCount()))
        markerScale = xml.SubElement(self.viewSettings, 'attribute', name = 'markerScale', value = str(self.view.getMarkerScale()))

    def readViewSettings(self):
        """Function to process view Settings from XML"""
        viewSettings = self.viewXML.findBranch("viewSettings")[0]
        for a in viewSettings.findall( 'attribute'):
            if a.attrib['name'] == 'markerCount': self.view.setMarkerCount(int(a.attrib['value']))
            elif a.attrib['name'] == 'markerScale': self.view.setMarkerScale(float(a.attrib['value']))

    def captureReflectionLine(self):
        """Function to process Reflection Line into XML"""
        reflectionLine = self.view.getReflectionLine()
        reflectionLineXml = reflectionLine.store()
        self.sceneItems.append(reflectionLineXml)

    def readRelectionLine(self):
        scene = self.view.scene()
        reflectionLineXml = self.viewXML.findBranch("ReflectionLine")
        if len(reflectionLineXml) ==  1: #We have found a single Correct Reflection Line
            newReflectionLine = ReflectionLine(20,20)  #Initialise Reflection line with arbitary width and height that we can over ride immediately with read method
            newReflectionLine.read(reflectionLineXml[0])
            scene.addItem(newReflectionLine)
            self.view.setReflectionLine(newReflectionLine)
        else: print "WARNING : REFLECTION LINE ERROR : NO REFLECTION LINES OR MULTIPLE REFLECTIONS LINES WERE LOADED"

    def captureMarkers(self):
        """Function to process Markers into XML"""
        markers = self.view.getMarkerList()
        for m in markers:
            markerXML = m.store()
            self.sceneItems.append(markerXML)

    def readMarkers(self):
        scene = self.view.scene()
        markers = self.viewXML.findBranch("GuideMarker")
        for m in markers:
            newMarker = GuideMarker()
            newMarker.read(m)
            scene.addItem(newMarker)
            self.view.markerList.append(newMarker) #Add Marker to marker List
            if newMarker.getActive(): self.view.markerActiveList.append(newMarker)
        self.view.markerActiveList.sort(key=lambda x: x.getActiveIndex())
        self.view.processMarkerActiveIndex()  #Update all active states 

    def captureWireGroups(self):
        """Function to process WireGroups into XML"""
        wireGroups = self.view.getWireGroups()
        for w in wireGroups:
            wireXml = w.store()
            self.sceneItems.append(wireXml)
    
    def readWireGroups(self):
        """A Function to generate WireGroups from XML"""
        scene = self.view.scene()
        wireGroups = self.viewXML.findBranch("WireGroup")
        for w in wireGroups:
            newWireGroup = WireGroup(self.view)
            newWireGroup.read(w)
            self.view.wireGroups.append(newWireGroup)
