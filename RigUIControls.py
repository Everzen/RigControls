##############LEDLIGHTLines############################################
import sys
import weakref
import math
from PyQt4 import QtCore, QtGui
import numpy as np
import socket #for sending out UPD signals
import os

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
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)

        self.initUI()

    def initUI(self):
        # self.drawStart = [self.width/2, self.inset]
        # self.drawEnd = [self.width/2, self.height - 2*self.inset]
        self.drawStart = [0, -self.height/2 + self.inset]
        self.drawEnd = [0, self.height/2 - self.inset]
        self.setPos(QtCore.QPointF(self.width/2, self.height/2))

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        self.prepareGeometryChange()
        pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawLine(self.drawStart[0],self.drawStart[1],self.drawEnd[0],self.drawEnd[1])

    def boundingRect(self):
        adjust = 5.0
        return QtCore.QRectF( -adjust, -self.height/2 + self.inset - adjust,
                             2*adjust, self.height - 2*self.inset + 2*adjust)

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

class ControlPin(QtGui.QGraphicsItem):
    def __init__(self, control = None):
        super(ControlPin, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.scale = 3

    def drawWireControl(self, painter):
        wCurve1 = QtGui.QPainterPath()

        locAx = -1.6 * self.scale
        locAy = 2.78 * self.scale

        locBx = -0.556 * self.scale
        locBy = 3.25 * self.scale

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
        # painter.drawLine(self.scale*-3,self.scale*-3,self.scale*3,self.scale*3)
        # painter.drawLine(self.scale*-3,self.scale*3,self.scale*3,self.scale*-3)
        painter.drawLine(0,self.scale*3,0,self.scale*-3)
        painter.drawLine(self.scale*-3,0,self.scale*3,0)

        #Now add wire details if needed
        self.drawWireControl(painter)

    def boundingRect(self):
        adjust = 5
        return QtCore.QRectF(self.scale*(-3 - adjust), self.scale*(-3 - adjust),
                             self.scale*(6 + adjust), self.scale*(6 + adjust))

#################################RIGGER GRAPHICS ITEMS#############################################################################

class GuideMarker(QtGui.QGraphicsItem):
    def __init__(self):
        super(GuideMarker, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        # self.setCacheMode(self.DeviceCoordinateCache)
        ####MARKER IDENTIFIERS####################################
        self.index = None        
        self.guideIndex = None
        self.guideName = None
        self.showID = True
        self.active = False
        self.activeIndex = 0
        self.scale = 1.0
        self.colourList = [QtGui.QColor(255,0,0), QtGui.QColor(0,255,0), QtGui.QColor(0,0,255), QtGui.QColor(0,255,255), QtGui.QColor(255,0,255), QtGui.QColor(255,255,0), QtGui.QColor(255,125,0), QtGui.QColor(125,255,0),QtGui.QColor(255,0,125),QtGui.QColor(125,0,255),QtGui.QColor(0,255,125),QtGui.QColor(0,125,255),QtGui.QColor(255,125,125),QtGui.QColor(125,255,125),QtGui.QColor(125,125,255),QtGui.QColor(255,255,125),QtGui.QColor(255,125,255),QtGui.QColor(125,255,255)]
        self.guideColour = self.colourList[1]
        # self.setPos(QtCore.QPointF(50,50))
        # self.move_restrict_rect = QtGui.QGraphicsRectItem(50,50,,410)
        # self.colourBroadcaster = colourBroadcaster #Pass the slider a Broadcaster

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

    def getguideIndex(self):
        return self.guideIndex

    def setguideIndex(self,gIndex):
        self.guideIndex = gIndex
        self.setGuideColour()

    def getguideName(self):
        return self.guideName

    def setguideName(self,gName):
        self.guideName = gName

    def setGuideColour(self):
        if self.guideIndex < len(self.colourList):
            self.guideColour = self.colourList[self.guideIndex]
        else:
            self.guideColour = QtGui.QColor.red

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

    def boundingRect(self):
        adjust = 5
        numberstretch = 5
        return QtCore.QRectF(self.scale*(-18 - adjust), self.scale*(-18 - adjust),
                             self.scale*(36 + adjust), self.scale*(36 + adjust + numberstretch))

    def drawActive(self, painter):
        """A function to draw an active glow around the marker when activated"""
        if self.active:
            pen = QtGui.QPen(self.guideColour, 0.5, QtCore.Qt.SolidLine)
            gradient = QtGui.QRadialGradient(0, 0, self.scale*18)
            gradient.setColorAt(0, QtGui.QColor(self.guideColour.red(),0,0,100))
            gradient.setColorAt(1, QtGui.QColor(self.guideColour.red(),self.guideColour.green(),self.guideColour.blue(),20))
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
        pen = QtGui.QPen(self.guideColour, 0.5, QtCore.Qt.SolidLine)
        if option.state & QtGui.QStyle.State_Sunken or self.isSelected(): # selected
            gradient = QtGui.QRadialGradient(0, 0, self.scale*4)
            gradient.setColorAt(1, QtGui.QColor(self.guideColour.red(),0,0,150))
            gradient.setColorAt(0, QtGui.QColor(self.guideColour.red(),self.guideColour.green(),self.guideColour.blue(),20))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(self.scale*-4, self.scale*-4, self.scale*8, self.scale*8)
            pen = QtGui.QPen(self.guideColour, 2, QtCore.Qt.SolidLine)

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
    def __init__(self, graphWidget, xPos, yPos, restraintDef=None, moveThreshold=5, operatorClass = None):
        QtGui.QGraphicsItem.__init__(self)
        self.index = 0
        self.graph = weakref.ref(graphWidget)
        self.rigCurveList = []
        self.bezierHandles = [None, None]
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        # self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.restraintDef = restraintDef
        self.move_restrict_circle = None
        self.operatorClass = operatorClass
        self.setPos(xPos,yPos)
        self.marker = False
        # if self.restraintDef:
        #     self.move_restrict_circle = QtGui.QGraphicsEllipseItem(2*self.restraintDef["centerOffset"][0],2*self.restraintDef["centerOffset"][1], 2*self.restraintDef["radius"],2*self.restraintDef["radius"])
        # offsetPos = self.pos() - QPVec(self.restraintDef["center"])
        if self.operatorClass:
            self.operatorClass.setPos([offsetPos.x(),offsetPos.y()]) #Set colourGrabber position
            self.operatorClass.mouseMoveExecute() # Set the initial colour

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

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             22 + adjust, 23 + adjust)

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.lightGray)
        painter.drawEllipse(-10, -10, 20, 20)
        gradient = QtGui.QRadialGradient(0, 0, 22)
        if option.state & QtGui.QStyle.State_Sunken: # selected
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkGreen).lighter(120))
        else:
            gradient.setColorAt(1, QtCore.Qt.blue)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-6, -6, 12, 12)


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for rigCurve in self.rigCurveList:
                rigCurve().buildCurve()
        # print "Item new position :" + str(self.pos().x()) + ", " + str(self.pos().y())
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            # print "Node pressed"
            QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if not self.graph().inhibit_edit:
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
        #
        policy = QtCore.Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
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
        self.markerSelectionList = []
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
        self.addRigControl([[290,80],[384,137],[424,237],[381,354]])

        #Test Parenting 
        cP1 = ControlPin()   
        cP1.setPos(QtCore.QPointF(20,20))

        cP2 = ControlPin()   
        cP2.setPos(QtCore.QPointF(60,20))

        m1 = GuideMarker()
        m1.setPos(QtCore.QPointF(20,20))

        m2 = GuideMarker()
        m2.setPos(QtCore.QPointF(60,20))

        m2.setParentItem(m1)
        self.scene().addItem(m1)
        self.scene().addItem(m2)
        self.scene().addItem(cP1)
        self.scene().addItem(cP2)

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
                newMarker.setguideIndex(self.markerGuideCount)
                newMarker.setIndex(item.getIndex())
                newMarker.setScale(self.markerScale)
                newMarker.setShowID(self.showMarkerID)
                # newMarker.setPos(self.mapToScene(newGuidePos.x(),newGuidePos.y()))
                newMarker.setPos(newGuidePos.x(),newGuidePos.y())
                scene.addItem(newMarker)

    def setShowMarkerID(self, state):
        """Function to show/hide the Guide Index, and index on Guide Markers"""
        scene = self.scene()
        for item in scene.items():
            if type(item) == GuideMarker: #change the state of its show ID
                item.setShowID(state)
                item.update()
        self.showMarkerID = state

    def setMarkerScale(self, scale):
        """Function to cycle through markers and scale"""
        scene = self.scene()
        for item in scene.items():
            if type(item) == GuideMarker: #change the state of its show ID
                item.setScale(float(scale/100.0))
                item.update()
        self.markerScale = float(scale/100.0)  

    def processMarkerActiceIndex(self):
        itemPresent = False
        for index, item in enumerate(self.markerSelectionList):
            item.setActiveIndex(index)

    def processMarkerSelection(self, marker):
        itemPresent = False
        for item in self.markerSelectionList:
            if marker == item: 
                itemPresent = True

        if itemPresent:
            if len(self.markerSelectionList) > 1 :
                self.markerSelectionList.remove(marker)
                marker.setActive(False) 
            elif len(self.markerSelectionList) == 1: #The list only contains this master so clear the list to be empty and deactivate the marker
                self.markerSelectionList = []
                marker.setActive(False)
        else: #the item is not present so we we just need to add it to the list
            self.markerSelectionList.append(marker)
            marker.setActive(True)
        self.processMarkerActiceIndex()

    def processMarkerDelete(self, marker):
        itemPresent = False
        for item in self.markerSelectionList:
            if marker == item: #the interacted item is in the list, so check if ctrl is pressed
                itemPresent = True

        if itemPresent: #the item is in the list so we need to remove it or, reset the list to empty
            if len(self.markerSelectionList) > 1 :
                self.markerSelectionList.remove(marker)
                marker.setActive(False)
            else: 
                self.markerSelectionList = []
                marker.setActive(False)


        #     if ctrl: #ctrl is pressed so  we are deselecting the item and removing from the list
        #         print "length : " + str(len(self.markerSelectionList))
        #         if len(self.markerSelectionList) > 1 : 
        #             self.markerSelectionList.remove(marker)
        #             print "ran if"
        #         else: 
        #             self.markerSelectionList = ["ctrlCase"] # Special Case where we are deselecting the only selected marker with a ctrl click
        #             print "ran else"
        #     else: self.markerSelectionList = [marker] #ctrl not pressed, so we are starting a new clean list with the marker
        # else: #the item is not present in the list
        #     if ctrl: self.markerSelectionList.append(marker) #append the 
        #     else: self.markerSelectionList = [marker] #ctrl not pressed, so we are starting a new clean list with the marker
        # # print str(self.markerSelectionList)

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
            self.processMarkerActiceIndex()
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
            item.setguideIndex(self.markerGuideCount) 
            item.setPos(self.mapToScene(event.pos()))
            item.setScale(self.markerScale)
            item.setShowID(self.showMarkerID)
            self.scene().addItem(item)
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
    #     else: self.markerSelectionList = [] # No item Marker has been selected so the selection list is cleared.
    #     # markerIndexes = []
    #     # for item in self.markerSelectionList: markerIndexes.append(item.getIndex())
    #     # print str(markerIndexes)
    #     return QtGui.QGraphicsView.mousePressEvent(self, mouseEvent)

    def mouseDoubleClickEvent(self, mouseEvent):
        scene = self.scene()
        selGuides = []
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            possibleItems = self.items(mouseEvent.pos())
            for item in possibleItems:
               if type(item) == GuideMarker: selGuides.append(item)

        print "Double"
        if len(selGuides) > 0 :
            self.processMarkerSelection(selGuides[0])
            self.processMarkerActiceIndex()
            return QtGui.QGraphicsView.mouseDoubleClickEvent(self, mouseEvent)
        else: 
            return QtGui.QGraphicsView.mouseDoubleClickEvent(self, mouseEvent)


    # def mouseReleaseEvent(self, mouseEvent):
    #     if len(self.scene().selectedItems()) > 0 and len(self.markerSelectionList) == 0: #A drag selection has occured. reset Marker list to selection
    #         for marker in self.scene().selectedItems():
    #             self.markerSelectionList.append(marker)

    #     if self.markerSelectionList[0] == "ctrlCase": self.markerSelectionList = [] #Sepcial case where last selected item has been deselected with a ctrl click

    #     markerIndexes = []
    #     for item in self.markerSelectionList: markerIndexes.append(item.getIndex())
    #     print str(markerIndexes)
    #     return QtGui.QGraphicsView.mouseReleaseEvent(self, mouseEvent)
