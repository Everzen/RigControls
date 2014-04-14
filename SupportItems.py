
import sys
from PySide import QtCore, QtGui
import os
import weakref
import xml.etree.ElementTree as xml


#######Project python imports################################################
from Utilities import *


#################################CLASSES & FUNCTIONS FOR NON INTERACTIVE GRAPHICS ITEMS##################################################################################


class RigCurveInfo():
    """
    A Class to assist calculations for how the curve that connects Nodes in a WireGroup should be calculated

    Useful data such as node positions, vectors between nodes and perpendicular vectors are calculated
    """
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



class PinTie(QtGui.QGraphicsItem):
    """A PinTie is the yellow dotted line that connects a ControlPin (pin) to the moving Node, or SuperNode

       This should be updated every time the node or the ControlPin (pin) move. This is normally done by  
       calling the "drawTie()" method in the "itemChange()" method of the node or ControlPin
    """
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






class RigCurve(QtGui.QGraphicsItem):
    """Draws the curve that connects all the nodes together in a WireGroup

    The user cannot interact with this curve, it is drawn automaticall when a Node or ControlPin is moved

    Currently, this curve is very intensive, and needs optimising in a serious way using dirty bits to 
    limit the number of times the redraw is calculated. Investigate this!  
    """
    def __init__(self, color, controlNodes, parent=None, scene=None):
        super(RigCurve, self).__init__(parent, scene)

        self.selected = False
        self.color = color
        self.nodeList = self.getNodeList(controlNodes)
        self.curveSwing = 0.25
        self.handlescale = 0.3
        self.secondHandleScale = 0.5
        self.dirty = True

        # Set Draw sorting order - 0 is furthest back. Put curves and pins near
        # the back. Nodes and markers nearer the front.
        self.setZValue(0)

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
        "Recalculates the curve if it is dirty and paints it"

        if self.dirty:
            self.buildCurve()

        pen = QtGui.QPen(QtCore.Qt.black, 1.2, QtCore.Qt.DotLine)
        painter.setPen(pen)
        # painter.setBrush(self.color)
        painter.strokePath(self.path, painter.pen())

    def dirtyCurve(self):
        "Marks the curve as dirty to register that it needs to be recalculated before drawing"

        self.dirty = True

    def buildCurve(self):
        "Rebuilds the curve if it is dirty and marks it as clean"

        if not self.dirty:
            return

        self.dirty = False

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







