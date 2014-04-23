
import sys
import weakref
from PySide import QtCore, QtGui
import os
import math
import xml.etree.ElementTree as xml


#######Project python imports################################################
from SupportItems import *

#################################CLASSES & FUNCTIONS FOR ACTIVE GRAPHICS ITEMS & CONSTRAINTS##################################################################################


class ReflectionLine(QtGui.QGraphicsItem):
    """A Reflection Line - the black dotted line down the centre of the Rig Graphics View

    It is used as a visual too to see the symmtry of the face.
    It is also used to reflect the positions of Guide Markers that need to be mirrored
    The line is adjustable by the user using the RC context menu.

    """
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

    def remap(self,gViewWidth, gViewHeight):
        self.width = gViewWidth
        self.height = gViewHeight
        self.drawStart = [0, -self.height/2 + self.inset]
        self.drawEnd = [0, self.height/2 - self.inset]
        self.setPos(QtCore.QPointF(self.width/2, self.height/2))
        self.update()


class WireGroup(object):
    """A WireGroups is a class that contains nodes each of which has it own pin
    which represents the location of its home. 

    A PinTie (yellow dotted line) is then drawn between the pin and node to
    help show the translation of the node

    For each node has its pin as a parent, so that translation of the node is measure
    with the pin as the origin (local space).

    Finally a curve (Rigcurve) is the drawn between all the nodes of the WireGroup

    """
    def __init__(self, rigGView, dataProcessor):
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
        self.rigGView = rigGView

        self.dataProcessor = dataProcessor
        # self.initBuild()

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        wireRoot = xml.Element('WireGroup')
        attributes = xml.SubElement(wireRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'name', value = str(self.getName()))
        xml.SubElement(attributes, 'attribute', name = 'colour', value = (str(self.colour.red()) + "," + str(self.colour.green()) + "," + str(self.colour.blue())))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))

        # Now record the xml for the Nodes
        wireNodes = xml.SubElement(wireRoot,'Nodes')
        for n in self.nodes:
            nodeXml = n.store(self.name) # Pass the node the wireGroup Name to help identify referenced nodes (Node Merges)
            wireNodes.append(nodeXml)
        # Now record the xml for the Pins - pinTies should be able to be drawn from the resulting data of nodes and pins
        wirePins = xml.SubElement(wireRoot,'Pins')
        for p in self.pins:
            pinXml = p.store(self.name)
            wirePins.append(pinXml)
        return wireRoot

    def read(self, wireXml):
        """A function to read in a block of XML and set all major attributes accordingly

        This is more complex since we can now have references to nodes/pins in other Wiregroups due to a Node Merges
        As such each Node and Pin is checked as it is loaded, and if it is found to be "native" (stored attribute)
        then it is read in and built as normal. However if it is a reference to another node/pin in a different 
        Wiregroup then a NodePinReference() object is used to store the reference to the appropriate Node. 

        All pins and Nodes that can be built (native ones) are built, but no curve is built, since all referenced nodes
        have to be resolved into the correct Wiregroups before the curves can be drawn. As such the functionality has 
        to be broken into 3 stages. 
        1) Build all native Nodes and Pins for all WireGroups
        2) Resolve all referenced Nodes and Pins for all wiregroups
        3) Only then can we build the curves for all Wiregroups
        """
        for a in wireXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'name': self.setName(a.attrib['value'])
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'colour': 
                newColour = a.attrib['value'].split(",")
                self.setColour(QtGui.QColor(int(newColour[0]), int(newColour[1]),int(newColour[2])))

        # Now read in and generate all the nodes
        self.clear() # Clear out all items, safely deleting everything from the WireGroup and destroying objects

        pins = wireXml.findall('Pins')
        for p in pins[0].findall('Pin'):
            if p.attrib['state'] == 'native': # We have a normal Native Pin so Build it
                newPin = ControlPin(QPVec([0,0])) # Create new Node with Arbitrary pos
                self.pins.append(newPin)
                newPin.read(p)
                self.scene.addItem(newPin)
                newPin.setGroup(self)
            elif p.attrib['state'] == 'reference': # We have a reference to a Node in another Wire Group, so read in the reference
                refPin = NodePinReference()
                refPin.read(p)
                self.pins.append(refPin)
        nodes = wireXml.findall('Nodes')
        for n in nodes[0].findall('Node'):
            if n.attrib['state'] == 'native': # We have a normal Native Pin so Build it
                newNode = Node(QPVec([0,0]), self.dataProcessor) # Create new Node with Arbitray pos
                self.nodes.append(newNode)
                newNode.read(n)
                newNode.setPin(self.findPin(newNode.getPinIndex())) # Set the pin for Node
                self.findPin(newNode.getPinIndex()).setNode(newNode) # Set the Node for the Pin
                # newNode.setWireGroup(self)
                newNode.setGroup(self)
                print "New node being set to DataBundle is : " + str(newNode)
                newNode.setDataBundleInfo() #This methods sets up details such as the attribute name within the Node DataBundle, which is determined by the WireGroup Name and Index
                if newNode.getPin().getConstraintItem(): # We have a constraint Item so make sure we set the node for it
                    newNode.getPin().getConstraintItem().setNode(newNode)
            
            elif n.attrib['state'] == 'reference': # We have a reference to a Node in another Wire Group, so read in the reference
                refNode = NodePinReference()
                refNode.read(n)
                self.nodes.append(refNode)
            # self.scene.addItem(newNode)
        self.createPinTies() # Now nodes and Pins are in Place we can create the pinTies
        # self.createCurve() # Hold off generating the curve until we have resolved all of the reference Nodes and Pins

    def buildFromPositions(self , pinQPointList):
        """Method used to build an entire Wiregroup from a list of positions provided

        This is not used for when we read a face from a file, since by that stage Nodes could have been merged
        between Wiregroups and as such the "read" requires more detail.
        """
        self.pinPositions = pinQPointList
        self.createPins()
        self.createNodes()
        self.createPinTies()
        self.createCurve() 

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = str(newName)
        for node in self.nodes: 
            node.setGroup(self) #Setting The Group again, will update the link to the Group, and set the right names in the DataBundles too.
            node.setDataBundleInfo() #With the name updated, then pass this information through to the DataBundles
        for pin in self.pins: pin.setGroup(self) 

    def getColour(self):
        return self.colour

    def setColour(self,colour):
        self.colour = colour

    def getNodes(self):
        return self.nodes

    def getPins(self):
        return self.pins

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
            cP.setGroup(self)
            self.pins.append(cP)
            self.scene.addItem(cP)

    def createNodes(self):
        self.nodes = []
        for index, p in enumerate(self.pins):
            # node = Node(p.pos())
            node = Node(QtCore.QPointF(0,0), self.dataProcessor)
            node.setIndex(p.getIndex())
            node.setPin(p)
            p.setNode(node)
            # node.setWireGroup(self)
            # node.setWireName(self.name)
            node.setGroup(self)
            node.setDataBundleInfo() #This methods sets up details such as the attribute name within the Node DataBundle, which is determined by the WireGroup Name and Index
            self.nodes.append(node)
            # self.scene.addItem(node)

    def createPinTies(self):
        """This method creates all the PinTies, which is the small yellow dotted line from ControlPin to Node

        This Method is used when reading in nodes/pins too. In this case it has to be careful, since it might
        meet a NodePinReference instead of a "native" node/pin (see "read" method doc string). In these cases 
        it is important that even those a PinTie is not going to be built the length of the self.pinTies list 
        kept in line with the length of the self.nodes and self.pins lists. As such a "None" is added to the 
        list when a reference is met in order to preserve the list length. This is then resolved in the mergeNode
        method.

        """
        self.pinTies = []
        if len(self.pins) > 1 and len(self.pins) == len(self.nodes):
            for index, n in enumerate(self.nodes):
                if type(n) == Node: #Check the type of n, since it might be a reference
                    pin = self.findPin(n.getPinIndex())
                    if pin:
                        pT = PinTie(n, pin)
                        pT.setIndex(pin.getIndex()) #Make the tie Index the same as the pins
                        # n.setPinIndex(index)
                        self.pinTies.append(pT)
                        n.setPinTie(pT)
                        pin.setPinTie(pT)
                        self.scene.addItem(pT)
                        pin.activate() #Now that all pins, ties and Nodes are in place
                else: self.pinTies.append(None) # Append None to keep the self.pinTies list the correct length
        else:
            print "WARNING : NO PIN TIES DRAWN SINCE THERE WERE INSUFFICIENT NODES OR UNEQUAL NODES AND PINS"

    def createCurve(self):
        if self.curve: # IF there is already a curve, then make sure that it is removed from the scene and deleted
            self.scene.removeItem(self.curve)
            del self.curve
            self.curve = None 
        for node in self.nodes: 
            if type(node) == Node: node.clearRigCurveList() # Clear out any dead curves from Node CurveLists. if we have a Node
        if len(self.nodes) > 2:
            self.curve = RigCurve(self.colour, self.nodes)
            self.scene.addItem(self.curve)

    def findNode(self,index):
        """Method used to find a node from within a Wiregroup using the nodes index"""
        for n in self.nodes:
            if n.getIndex() == index:
                return n

    def findPin(self,index):
        """Method used to find a pin from within a Wiregroup using the nodes index"""
        for p in self.pins:
            if p.getIndex() == index:
                return p

    def resetNodes(self):
        """Method to send all the nodes in the Wiregroup back to the origins (pins)"""
        for node in self.nodes:
            if node.getPin().isActive(): #If the pin of the node is active, then we need to send it home.
                node.goHome()

    def mergeNode(self, index, mergeNode, goHome = True):
        """A function to replace the index node in self.nodes with a merged node coming from another Wiregroup

        This method is used both when the user merges nodes in the UI, but also to resolve Node Merges that are 
        saved out and read in from files. It is this function that takes a NodePinReference and replaces it 
        in the wiregroup lists with the correct node/pin from a neighbouring wiregroup.
        """

        if index < len(self.nodes):
            # Proceed with Replacement if we have a valid native Node or a NodePinReference Object
            if self.nodes[index].getGroupName() == self.name or self.nodes[index].name == "NodePinReference": 
                oldNode = self.nodes[index]
                # Directly set the mergeNode Node into the WireGroup
                self.pins[index] = mergeNode.getPin()
                self.nodes[index] = mergeNode
                self.pinTies[index] = mergeNode.getPinTie()
                
                # Delete the Old MergeNode Node and Pin
                if type(oldNode) == Node: # If it is a node then remove it, but it might simply be a reference.
                    self.scene.removeItem(oldNode.getPin())
                    self.scene.removeItem(oldNode.getPinTie())
                    self.scene.removeItem(oldNode)
                
                # For neatness sends the merge node back to its pin. This is deactivated when reading in a file            
                if goHome: mergeNode.goHome() 

    def resolveReferences(self):
        """This is the method that is called after the intial 'native' nodes are read in from a file

        It scans the self.nodes to find references (NodePinReference objects). From there is scans all 
        the other wiregroups in the scene to find the referenced node incorporate it into this wiregroup.

        After these references are resolved for all wiregroups then the final wiregroup curves can be built.
        """
        for index, refNode in enumerate(self.nodes):
            if refNode.name == "NodePinReference": # We have found a reference so find and sub in the Node
                for wireGroup in self.rigGView.wireGroups:
                    # if wireGroup.getName() == refNode.getWireName():
                    if wireGroup.getName() == refNode.getGroupName():
                        targetNode = wireGroup.findNode(refNode.getIndex())
                        self.mergeNode(index, targetNode, goHome = False)

    def clear(self):
        """A Function to completely remove all items from Wiregroup"""
        for n in self.nodes:
            n.setSelected(False) #Deselecting the node helps when deleting the Wiregroup, to ensure we are only asked once about deletion
            n.clearData() #Clear out all the data associated with animCurves etc in the DataBundle
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
        self.pinTies = []
        self.curve = None 





class SuperNodeGroup(object):
    """A SuperNodeGroup contains a SuperNode and a pin to represent the original
       position of the superNode.

    A PinTie (yellow dotted line) between the superNode and its pin.

    The pin is parent of the superNode, so that the translation of the SuperNode 
    is measured with the pin as the origin (local space).

    """
    name = "SuperNodeGroup"

    def __init__(self, nPos, form, rigGView, dataProcessor):
        #LIST OF ATTRIBUTES
        self.name = "holdingName" #Put in a holding name, so the name is not reported as None
        self.locked = True
        self.form = form
        self.scale = 1.0 #Not implemented, but it is stored, so could be used to drive the size of the setup of the wiregroup
        self.colour = QtGui.QColor(0,0,0)
        self.visible = True # Now implemented but stored, since hiding will be built in, in later versions
        self.superNode = None
        self.pin = None
        self.pinTie = None
        self.scene = rigGView.scene()

        self.dataProcessor = dataProcessor

        self.initBuild(nPos)

    def initBuild(self, nPos):
        #Create pin, SuperNode and PinTie from start position
        cP = ControlPin(nPos) #Build Pin
        cP.setGroup(self)
        self.pin = cP

        sNode = SuperNode(QtCore.QPointF(0,0), self.dataProcessor) #Build SuperNode
        sNode.setForm(self.form)
        sNode.setPin(cP)
        cP.setNode(sNode)
        self.superNode = sNode
        # self.superNode.setSuperNodeGroup(self)
        self.superNode.setGroup(self)
        
        pT = PinTie(sNode, cP)
        sNode.setPinTie(pT)
        cP.setPinTie(pT)
        self.pinTie = pT

        self.scene.addItem(cP)
        self.scene.addItem(pT)
        cP.setLocked(False)

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        superNodeGroupRoot = xml.Element('SuperNodeGroup')
        attributes = xml.SubElement(superNodeGroupRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'name', value = str(self.getName()))
        xml.SubElement(attributes, 'attribute', name = 'form', value = str(self.getForm()))
        xml.SubElement(attributes, 'attribute', name = 'locked', value = str(self.isLocked()))
        xml.SubElement(attributes, 'attribute', name = 'colour', value = (str(self.colour.red()) + "," + str(self.colour.green()) + "," + str(self.colour.blue())))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))

        # Now record the xml for the superNode and Pin
        # pinTies should be able to be drawn from the resulting data of nodes and pins
        superNodeGroupRoot.append(self.superNode.store())
        superNodeGroupRoot.append(self.pin.store(self.name))

        return superNodeGroupRoot

    def read(self, superNodeGroupXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in superNodeGroupXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'name': self.setName(a.attrib['value'])
            elif a.attrib['name'] == 'form': self.setForm(a.attrib['value'])
            elif a.attrib['name'] == 'locked': self.setLocked(str(a.attrib['value']) == 'True')            
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'colour': 
                newColour = a.attrib['value'].split(",")
                self.setColour(QtGui.QColor(int(newColour[0]), int(newColour[1]),int(newColour[2])))

        # Now read in and generate superNode, Pin and PinTie
        self.clear() # Clear out superNode, Pin and PinTie

        pinXml = superNodeGroupXml.findall('Pin')[0]
        newPin = ControlPin(QPVec([0,0])) 
        newPin.read(pinXml)
        newPin.setGroup(self)
        self.scene.addItem(newPin)

        sNodeXml = superNodeGroupXml.findall('SuperNode')[0]
        newSNode = SuperNode(QtCore.QPointF(0,0), self.dataProcessor) # Create new SuperNode with Arbitrary pos
        newSNode.setForm(self.form)
        self.scene.addItem(newSNode)
        # We need to add the SuperNode to the Scene before we read it, so that it has
        # access to all the other nodes in the scene for deciphering skinning information
        newSNode.read(sNodeXml) 

        newSNode.setPin(newPin) # Set pin to the SuperNode and SuperNode to the Pin
        newPin.setNode(newSNode)

        self.pin = newPin
        self.superNode = newSNode
        # self.superNode.setSuperNodeGroup(self)
        self.superNode.setGroup(self)


        self.setScale(self.scale) # The scale now needs to be read into the items

        pT = PinTie(newSNode, newPin) # Create new PinTie to link SuperNode and Pin
        newSNode.setPinTie(pT)
        newPin.setPinTie(pT)
        self.pinTie = pT
        self.scene.addItem(pT)

        if self.superNode.getPin().getConstraintItem(): # If We have a constraint Item make sure we set the node for it
            self.superNode.getPin().getConstraintItem().setNode(self.superNode)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = str(name)
        if self.superNode: 
            self.superNode.setGroup(self) #Setting The Group again, will update the link to the Group, and set the right names in the DataBundles too.
            self.superNode.setDataBundleInfo()#With the name updated, then pass this information through to the DataBundles
        self.pin.setGroup(self)

    def isLocked(self):
        return self.locked

    def setLocked(self, locked):
        self.locked = bool(locked)

    def isVisible(self):
        return self.visible

    def setVisible(self, visible):
        self.visible = visible

    def getForm(self):
        return self.form

    def setForm(self, form):
        self.form = str(form)

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale
        #Now update the scale of all items
        if self.superNode : self.superNode.setScale(scale)
        if self.pin : self.pin.setScale(scale)

    def getColour(self):
        return self.colour

    def setColour(self,colour):
        self.colour = colour

    def getSuperNode(self):
        return self.superNode

    def setSuperNode(self, superNode):
        # print "Node is : " + str(node)
        if type(superNode) == superNode: self.superNode = superNode

    def getPin(self):
        return self.pin

    def setPin(self, pin):
        if type(pin) == ControlPin: self.pin = pin

    def getPinTie(self):
        return self.pinTie

    def setPinTie(self, pinTie):
        if type(pinTie) == PinTie: self.pinTie = pinTie

    def clear(self):
        if self.superNode: 
            self.superNode.clearData() #Clear out the data and AnimCurves associated with this superNode
            self.scene.removeItem(self.superNode)
            del self.superNode
        if self.pin: 
            self.scene.removeItem(self.pin)
            del self.pin
        if self.pinTie: 
            self.scene.removeItem(self.pinTie)
            del self.pinTie
        self.superNode = None
        self.pin = None
        self.pinTie = None 




class ControlPin(QtGui.QGraphicsItem):
    """A Control Pin is the small black cross with curved outer lines that accompanies each Node

    The Control Pin (pin) is the parent of the node and represents the nodes home 
    (origin in local space)

    Each pin has a single node.

    The pin is not interacted with by the user, unless the RC context menu is used to activate
    the pin so that its position can be adjusted.

    SuperNodes can skin pins. In this case SuperNodes will partly influence the position of a
    pin through its own movement and associated skinning value.

    """
    def __init__(self, cPos, control = None):
        super(ControlPin, self).__init__()      
        self.index = 0 
        self.scale = 1
        self.scaleOffset = 1
        self.alpha = 1.0 # Not implemented, since the pin is so subtle.
        self.group = None
        self.groupName = None
        self.constraintItem = None
        self.active = True
        self.node = None
        self.pinTie = None
        self.locked = True

        self.setPos(cPos)
        self.setZValue(12) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.


    def store(self, groupName):
        """Method to write out a block of XML that records all the major attributes that will be needed for save/load

        The first thing to do is check to see if the pin is natively from this Wiregroup, or to see if it has been 
        Merged in from another wiregroup. This can be done by checking the wirenames. If it is from this wire group then
        its state is recorded as "native". It it isnt from this wiregroup then its state is recorded as "reference" 

        The data then stored for each state is identical, but is treated differently when the data is read back in,
        in the Wiregroup read method. 
        """
        state = "native"
        if self.groupName != groupName: state = "reference" 

        # print "Input wireName : " + str(wireName) + " Pin WireName : " + str(self.wireName)
        pinRoot = xml.Element('Pin', state = str(state))
        attributes = xml.SubElement(pinRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'scaleOffset', value = str(self.getScaleOffset()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'active', value = str(self.isActive()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        xml.SubElement(attributes, 'attribute', name = 'rotation', value = str(self.rotation()))
        xml.SubElement(attributes, 'attribute', name = 'locked', value = str(self.isLocked()))

        #Now Store the constraint Information add it to the XML
        constraintXml = xml.SubElement(pinRoot,'ConstraintItem')
        if self.constraintItem: 
            constraintItemXml = self.constraintItem.store()
            constraintXml.append(constraintItemXml) 
        return pinRoot

    def read(self, pinXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in pinXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'scaleOffset': self.setScaleOffset(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))
            elif a.attrib['name'] == 'rotation': 
                self.setRotation(float(a.attrib['value']))
            elif a.attrib['name'] == 'active': self.setActive(str(a.attrib['value']) == 'True') #At the very end check the active state of the pin
            elif a.attrib['name'] == 'locked': self.setLocked(str(a.attrib['value']) == 'True') #At the very end check the locked


        #Now read in the constraint Item information
        constraintXML = pinXml.findall('ConstraintItem')
        for cItemXml in constraintXML[0]:
            cItem = None
            if cItemXml.tag == "ConstraintEllipse": cItem = ConstraintEllipse() #We have an ConstraintEllipse so lets build one and load in the settings
            elif cItemXml.tag == "ConstraintRect": cItem = ConstraintRect() #We have an ConstraintRect so lets build one and load in the settings
            elif cItemXml.tag == "ConstraintLine": cItem = ConstraintLine() #We have an ConstraintLine so lets build one and load in the settings
            
            if cItem:
                cItem.setPin(self)
                self.setConstraintItem(cItem)
                cItem.read(cItemXml)

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

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)

    def getGroup(self):
        return self.group

    def setGroup(self, group):
        self.group = group
        self.groupName = group.getName()

    def getGroupName(self):
        return self.groupName

    def setGroupName(self, groupName):
        self.groupName = str(groupName)   

    def getConstraintItem(self):
        return self.constraintItem

    def setConstraintItem(self, item):
        """Function to set the Constraint Item, and make sure that the constraintItem recognises the pin and the node"""
        if type(item) == ConstraintLine or type(item) == ConstraintRect or type(item) == ConstraintEllipse:
            self.constraintItem = item
            if self.node: item.setNode(self.getNode())
            self.constraintItem.calibrateDataBundle() #This will line up the dataBundle output with the limits of the constraintItem

    def isActive(self):
        return self.active

    def setActive(self, active):
        self.active = active

    def activate(self):
        if not self.active: 
            response = QtGui.QMessageBox.Yes
            if self.constraintItem: 
                delConstraintItem = QtGui.QMessageBox()
                self.styleData = self.scene().views[0].styleData
                delConstraintItem.setStyleSheet(self.styleData)
                delConstraintItem.setWindowTitle("Pin Deactivation")
                delConstraintItem.setText("Are you sure you want to deactivate the pin? There is a constraint Item present, and this item will be removed if you continue.")
                delConstraintItem.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                delConstraintItem.setDefaultButton(QtGui.QMessageBox.No)
                response = delConstraintItem.exec_()
            if response == QtGui.QMessageBox.Yes:
                self.scaleOffset = 1.0
                self.getNode().goHome()
                self.getNode().setVisible(False)
                self.getPinTie().setVisible(False)
                if self.constraintItem: #Remove the constraint Item if it is there.  
                    self.scene().removeItem(self.constraintItem)
                    self.constraintItem = None
        else: 
            self.scaleOffset = 2.5
            self.getNode().setVisible(True)
            self.getPinTie().setVisible(True)            
            self.update()

    def getNode(self):
        return self.node

    def setNode(self, node):
        # print "Node is : " + str(node)
        if type(node) == Node: self.node = node

    def getPinTie(self):
        return self.pinTie

    def setPinTie(self, pinTie):
        if type(pinTie) == PinTie: self.pinTie = pinTie

    def isLocked(self):
        return self.locked

    def setLocked(self, locked):
        self.locked = bool(locked)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, not self.locked)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, not self.locked)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, not self.locked)

    def drawWireControl(self, painter):
        wCurve1 = QtGui.QPainterPath()

        locAx = -1.6 * self.scale*self.scaleOffset
        locAy = 2.78 * self.scale*self.scaleOffset

        locBx = -0.556 * self.scale*self.scaleOffset
        locBy = 3.25 * self.scale*self.scaleOffset

        pen = QtGui.QPen(QtCore.Qt.black, 0.25, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        # wCurve1 = QtGui.QPainterPath()
        # wCurve1.moveTo(QtCore.QPointF(locAx,locAy))
        # wCurve1.cubicTo(QtCore.QPointF(locBx,locBy),QtCore.QPointF(-locBx,locBy),QtCore.QPointF(-locAx,locAy))

        # wCurve2 = QtGui.QPainterPath()
        # wCurve2.moveTo(QtCore.QPointF(locAy,locAx))
        # wCurve2.cubicTo(QtCore.QPointF(locBy,locBx),QtCore.QPointF(locBy,-locBx),QtCore.QPointF(locAy,-locAx))
        
        # wCurve3 = QtGui.QPainterPath()
        # wCurve3.moveTo(QtCore.QPointF(locAx,-locAy))
        # wCurve3.cubicTo(QtCore.QPointF(locBx,-locBy),QtCore.QPointF(-locBx,-locBy),QtCore.QPointF(-locAx,-locAy))

        # wCurve4 = QtGui.QPainterPath()
        # wCurve4.moveTo(QtCore.QPointF(-locAy,locAx))
        # wCurve4.cubicTo(QtCore.QPointF(-locBy,locBx),QtCore.QPointF(-locBy,-locBx),QtCore.QPointF(-locAy,-locAx))
        
        # # painter.setBrush(self.color)
        # painter.strokePath(wCurve1, painter.pen())
        # painter.strokePath(wCurve2, painter.pen())
        # painter.strokePath(wCurve3, painter.pen())
        # painter.strokePath(wCurve4, painter.pen())

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtCore.Qt.black, 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        painter.drawLine(0,self.scale*self.scaleOffset*1.0,0,self.scale*self.scaleOffset*-1.0)
        painter.drawLine(self.scale*self.scaleOffset*-1.0,0,self.scale*self.scaleOffset*1.0,0)
    
        # painter.drawRect(self.boundingRect())

        if self.active:
            # Now add wire details if needed
            self.drawWireControl(painter)

    def boundingRect(self):
        adjust = 0
        size = 1
        return QtCore.QRectF(self.scale*self.scaleOffset*(-size - adjust), self.scale*self.scaleOffset*(-size - adjust),
                             self.scale*self.scaleOffset*2*(size  + adjust), self.scale*self.scaleOffset*2*(size + adjust))

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            if self.pinTie:
                self.pinTie.drawTie()

            # If there is a node then it will be moved, so update the curve that runs through it
            if self.getNode(): self.getNode().dirtyCurve()
        return QtGui.QGraphicsItem.itemChange(self, change, value)





class GuideMarker(QtGui.QGraphicsItem):
    """Guide markers are the squre icons with the diagonal red lines.

    These are used to mark out the places in which we want to add the nodes
    when building a Wire Group.

    In future development they may well be used to mark the positions for other
    controls

    """

    name = "GuideMarker"

    def __init__(self):
        super(GuideMarker, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        ####MARKER IDENTIFIERS####################################
        self.index = None        
        self.active = False
        self.activeIndex = 0
        self.minimumScale = 0.8
        self.scale = 1.0
        self.alpha = 1.0
        self.colourList = [QtGui.QColor(255,0,0), QtGui.QColor(0,255,0), QtGui.QColor(0,0,255), QtGui.QColor(0,255,255), QtGui.QColor(255,0,255), QtGui.QColor(255,255,0), QtGui.QColor(255,125,0), QtGui.QColor(125,255,0),QtGui.QColor(255,0,125),QtGui.QColor(125,0,255),QtGui.QColor(0,255,125),QtGui.QColor(0,125,255),QtGui.QColor(255,125,125),QtGui.QColor(125,255,125),QtGui.QColor(125,125,255),QtGui.QColor(255,255,125),QtGui.QColor(255,125,255),QtGui.QColor(125,255,255)]
        self.guideColourIndex = 0
        self.setZValue(20) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

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
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
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
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'guideColourIndex': self.setGuideColourIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

    def getMinimumScale(self):
        return self.minimumScale

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)

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
        return QtCore.QRectF(self.scale*(-15 - adjust), self.scale*(-15 - adjust),
                             self.scale*2*(15 + adjust), self.scale*2*(15 + adjust))

    def drawActive(self, painter):
        """A function to draw an active glow around the marker when activated"""
        if self.active:
            pen = QtGui.QPen(QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),255*self.alpha), self.scale*0.5, QtCore.Qt.SolidLine)
            gradient = QtGui.QRadialGradient(0, 0, self.scale*18)
            gradient.setColorAt(0, QtGui.QColor(self.colourList[self.guideColourIndex].red(),0,0,100*self.alpha))
            gradient.setColorAt(1, QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),20*self.alpha))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawEllipse(self.scale*-18, self.scale*-18, self.scale*36, self.scale*36)        

    def drawActiveIndex(self,painter):
        if self.active: #Conditions met to disply numbers on corners
            pen = QtGui.QPen(QtGui.QColor(180,180,180,255*self.alpha), 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            fontsize = 9
            if self.scale < 1.0:
                fontsize = int(9*self.scale)
            painter.setFont(QtGui.QFont('Arial', fontsize))
            painter.drawText(self.scale*9,self.scale*5,str(self.activeIndex))

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        self.drawActive(painter)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setPen(QtGui.QPen(QtGui.QColor(180,180,180,255*self.alpha), 0))
        painter.drawRect(self.scale*-8, self.scale*-8, self.scale*16, self.scale*16)
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine))
        painter.drawRect(self.scale*-4, self.scale*-4, self.scale*8, self.scale*8)
        # painter.drawRect(-12.5, -2.75, 25, 5)
        pen = QtGui.QPen(QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),255*self.alpha), 0.5, QtCore.Qt.SolidLine)
        if option.state & QtGui.QStyle.State_Sunken or self.isSelected(): # selected
            gradient = QtGui.QRadialGradient(0, 0, self.scale*4)
            gradient.setColorAt(1, QtGui.QColor(self.colourList[self.guideColourIndex].red(),0,0,150*self.alpha))
            gradient.setColorAt(0, QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),20*self.alpha))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(self.scale*-4, self.scale*-4, self.scale*8, self.scale*8)
            pen = QtGui.QPen(QtGui.QColor(self.colourList[self.guideColourIndex].red(),self.colourList[self.guideColourIndex].green(),self.colourList[self.guideColourIndex].blue(),255*self.alpha), 2*self.scale, QtCore.Qt.SolidLine)

        painter.setPen(pen)
        painter.drawLine(self.scale*-12,self.scale*-12,self.scale*12,self.scale*12)
        painter.drawLine(self.scale*-12,self.scale*12,self.scale*12,self.scale*-12)
        self.drawActiveIndex(painter)
        # painter.drawRect(self.boundingRect())

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            pass
            # print "Marker Move pos : " + str(self.scenePos())  
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        self.setPos(self.mapToScene(event.pos())) #Trying to line centre of node to mouse move
        QtGui.QGraphicsItem.mousePressEvent(self, event)




class ExpressionStateNode(QtGui.QGraphicsItem):
    """These are used to capture the entire state of a Happy face

    The current state of the face can be recorded and then you can slide in percentage changes towards the captured state
    """
    def __init__(self):
        super(ExpressionStateNode, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        ####EPRESSIONNODE IDENTIFIERS####################################
        self.index = None    
        self.name = "Expression"    
        self.active = False
        self.minimumScale = 0.8
        self.scale = 1.0
        self.alpha = 1.0
        self.width = 95
        self.height = 22
        self.sliderBoxHeight = 22
        self.borderRect = QtCore.QRectF(self.scale*(0), self.scale*(0), self.scale*(self.width), self.scale*(self.height + self.sliderBoxHeight))
        self.colour = QtGui.QColor(255,0,0)
        self.setZValue(20) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

        self.sliderStartPos = self.setSliderStartPos()
        self.sliderEndPos = self.setSliderEndPos()
        self.slider = None
        self.init()

    def init(self):
        """Function to setup the item width and height parameters and the ExpressionSlider"""
        self.update()
        self.setSliderStartPos()
        self.setSliderEndPos()

        self.slider = ExpressionPercentageSlider(self)
        self.slider.setParentItem(self)
        self.slider.setPos(self.sliderStartPos)

        # tempPainter = QtGui.QPainter()
        # borderRect = tempPainter.drawText(0,0,200,20,0,str(self.name))
        # self.width = borderRect.width()
        # self.height = borderRect.height()
        # print "My dim : " + str(self.width) + " " + str(self.height)

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        GuideMarkerRoot = xml.Element('GuideMarker')
        attributes = xml.SubElement(GuideMarkerRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'active', value = str(self.getActive()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
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
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

    def getMinimumScale(self):
        return self.minimumScale

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)

    def getIndex(self):
        return self.index

    def setIndex(self,index):
        self.index = index

    def getActive(self):
        return self.active

    def setActive(self, state):
        self.active = state
        self.update()

    def setSliderStartPos(self):
        """Function to find where the start of the slider line should be sitting"""
        self.sliderStartPos = QtCore.QPointF(5,self.scale*self.height+(0.5*self.sliderBoxHeight))

    def setSliderEndPos(self):
        """Function to find where the end of the slider line should be sitting"""
        self.sliderEndPos = QtCore.QPointF(self.scale*self.width - 5,self.scale*self.height+(0.5*self.sliderBoxHeight))

    def boundingRect(self):
        adjust = 5
        # return QtCore.QRectF(self.scale*(0 - adjust), self.scale*(0 - adjust),
        #                     self.scale*(self.width + adjust), self.scale*(self.height + self.sliderBoxHeight + adjust))
        return QtCore.QRectF(-adjust, -adjust, self.borderRect.width() + 2*adjust, self.borderRect.height() + 2*adjust + self.sliderBoxHeight)

    def drawName(self,painter):
        """Function to write the expression name and draw rectangle around it"""
        pen = QtGui.QPen(QtGui.QColor(180,180,180,255*self.alpha), 1, QtCore.Qt.SolidLine)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        fontsize = 14
        if self.scale < 1.0:
            fontsize = int(9*self.scale)
        painter.setFont(QtGui.QFont('Arial', fontsize))

        self.borderRect = painter.drawText(0,0,200,20,0,str(self.name))

        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(self.borderRect)



    def paint(self, painter, option, widget):
        """Function to paint the ExpressionCaptureNode, including writing expression name and drawing expression slider line"""
        self.drawName(painter)

        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(0,self.scale*self.height, self.scale*self.width, self.scale*self.sliderBoxHeight)
        pen = QtGui.QPen(QtGui.QColor(0,0,0,50*self.alpha), 0.5, QtCore.Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.sliderStartPos,self.sliderEndPos) #Draw Slider Line

        painter.setPen(QtCore.Qt.NoPen)
        gradient = QtGui.QRadialGradient(self.scale*self.width/2,self.scale*self.height/2, self.scale*self.width)
        gradient.setColorAt(1, QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(),150*self.alpha))
        gradient.setColorAt(0, QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(),20*self.alpha))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawRect(0,0, self.scale*self.width, self.scale*self.height)

        pen = QtGui.QPen(QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(),255*self.alpha), 2*self.scale, QtCore.Qt.SolidLine)
        self.drawName(painter)


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            pass
            # print "Marker Move pos : " + str(self.scenePos())  
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        pass
        # self.setPos(self.mapToScene(event.pos())) #Trying to line centre of node to mouse move
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def sliderChangedMovement(self, eventPos): 
        """Function to return the position that the Expression item should be at, on a mouse move"""
        localPos = eventPos
        xPos = localPos.x()
        if xPos < self.sliderStartPos.x(): 
            xPos = self.sliderStartPos.x()
        elif xPos > self.sliderEndPos.x(): 
            xPos = self.sliderEndPos.x()
        # return self.mapToScene(QtCore.QPointF(xPos,self.sliderStartPos.y()))
        return (QtCore.QPointF(xPos,self.sliderStartPos.y()))

    def movePercentage(self,currentPos):
        """Function to calculate the distance that the slider has moved and return as a percentage"""
        slideRange = self.sliderEndPos.x() - self.sliderStartPos.x()
        slideDistance = currentPos.x() - self.sliderStartPos.x()
        movePercentage = 100.0*float(slideDistance)/float(slideRange)
        return movePercentage



class ExpressionPercentageSlider(QtGui.QGraphicsItem):
    """Used as the slider handle on the ExpressionCaptureNode
    """
    def __init__(self, expressionStateNode):
        super(ExpressionPercentageSlider, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.width = 4
        self.height = 8
        self.scale = 1.0
        self.expressionStateNode = expressionStateNode
        self.colour = QtGui.QColor(255,0,0)
        self.alpha = 1.0

    def init(self):
        """Function to setup the slider on its parent expressionStateNode"""
        pass

    def boundingRect(self):
        adjust = 4
        return QtCore.QRectF(-0.5 * self.scale*(self.width + adjust), -0.5*self.scale*(self.height + adjust),
                            self.scale*(self.width + 2*adjust), self.scale*(self.height + 2*adjust))

    def paint(self, painter, option, widget):
        """Function to paint the ExpressionSlider"""
        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(-0.5 * self.scale*self.width, -0.5*self.scale*self.height, self.scale*self.width, self.scale*self.height)

        painter.setPen(QtCore.Qt.NoPen)
        gradient = QtGui.QRadialGradient(self.scale*self.width/2,self.scale*self.height/2, self.scale*self.width)
        gradient.setColorAt(1, QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(),150*self.alpha))
        gradient.setColorAt(0, QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(),20*self.alpha))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawRect(-0.5 * self.scale*self.width, -0.5*self.scale*self.height, self.scale*self.width, self.scale*self.height)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            newPos = self.expressionStateNode.sliderChangedMovement(value)
            print "My Current Percentage is : " + str(self.expressionStateNode.movePercentage(newPos))
            return newPos  #Origins are the same for both the slider and the ExpressionStateNode, so no real mappings are needed

        return QtGui.QGraphicsItem.itemChange(self, change, value)





class Node(QtGui.QGraphicsItem):
    """The Node is the main circular item that the user interacts with in the WireGroup

    Nodes when moved away from their parent ControlPin (pin) generate the offset that
    will be used to drive the change on the maya character face mesh (or servo for
    animatronic)

    Their home is the location of their pin, which is their origin in local space.

    Nodes can be constrained using a constraintItem, which can restrict their 
    movement to a shape (ellispse/rectangle) or a straight line
    """
    name = "Node"

    def __init__(self, nPos, dataProcessor):
        QtGui.QGraphicsItem.__init__(self)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)

        self.index = 0
        self.radius = 8
        self.rigCurveList = []
        self.bezierHandles = [None, None]

        self.scaleOffset = 7
        self.minimumScale = 0.8
        self.scale = 1.0
        self.colour = QtGui.QColor(25,25,255,150)
        # self.pin.append(weakref.ref(pin))
        self.pin = None
        self.pinIndex = None

        self.pinTie = None
        self.pinTieIndex = None

        self.group = None #group is now used whether it is WireGroup or SuperNodeGroup. Testing Implentation
        self.groupName = None

        # self.wireGroup = None
        # self.wireName = ""

        self.hightlighted = False
        self.setPos(nPos)
        self.setZValue(12) #Set Draw sorting order - 0 is furthest back. Put curves and pins near the back. Nodes and markers nearer the front.

        self.dataProcessor = dataProcessor
        self.dataBundle = None
        self.dataProcessor.attachBundle(self) #This method will create a new DataBundle and attach it to both this Node and the central DataProcessor

    def store(self,wireName):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load

        The first thing to do is check to see if the node is natively from this Wiregroup, or to see if it has been 
        Merged in from another wiregroup. This can be done by checking the groupNames. If it is from this wire group then
        its state is recorded as "native". It it isnt from this wiregroup then its state is recorded as "reference" 

        The data then stored for each state is identical, but is treated differently when the data is read back in,
        in the Wiregroup read method.
        """
        # We need to identify if the Node is referenced for is native to this WireGroup
        state = "native"
        if self.groupName != wireName: state = "reference" 
        # print "Input wireName : " + str(wireName) + " Node WireName : " + str(self.wireName)
        nodeRoot = xml.Element('Node', state = str(state))
        attributes = xml.SubElement(nodeRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'radius', value = str(self.getRadius()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'pinIndex', value = str(self.getPinIndex()))
        xml.SubElement(attributes, 'attribute', name = 'pinTieIndex', value = str(self.getPinTieIndex()))
        # xml.SubElement(attributes, 'attribute', name = 'wireName', value = str(self.getWireName()))
        xml.SubElement(attributes, 'attribute', name = 'groupName', value = str(self.getGroupName()))
        xml.SubElement(attributes, 'attribute', name = 'colour', value = (str(self.getColour().red()) + "," + str(self.getColour().green()) + "," + str(self.getColour().blue())))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        if self.getBezierHandles(0) != None: xml.SubElement(attributes, 'attribute', name = 'bezierHandle0', value = (str(self.getBezierHandles(0)[0]) + "," + str(self.getBezierHandles(0)[1])))
        else: xml.SubElement(attributes, 'attribute', name = 'bezierHandle0', value = ("None"))
        if self.getBezierHandles(1) != None: xml.SubElement(attributes, 'attribute', name = 'bezierHandle1', value = (str(self.getBezierHandles(1)[0]) + "," + str(self.getBezierHandles(1)[1])))
        else: xml.SubElement(attributes, 'attribute', name = 'bezierHandle1', value = ("None"))

        # Now record the xml for the DataBundle if there is one
        dataBundlesXml = xml.SubElement(nodeRoot,'DataBundles')
        if self.dataBundle:
            dataBundleXml = self.dataBundle.store()
            dataBundlesXml.append(dataBundleXml)

        return nodeRoot

    def read(self, nodeXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in nodeXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'radius': self.setRadius(float(a.attrib['value']))
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'pinIndex': self.setPinIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'pinTieIndex': self.setPinTieIndex(int(a.attrib['value']))
            # elif a.attrib['name'] == 'wireName': self.setWireName(str(a.attrib['value']))
            elif a.attrib['name'] == 'groupName': self.setGroupName(str(a.attrib['value']))
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
            elif a.attrib['name'] == 'colour':
                newColour = a.attrib['value'].split(",")
                self.setColour(QtGui.QColor(float(newColour[0]), float(newColour[1]),float(newColour[2])))                

        #Now we have to load in the dataBundle information. The dataBundle will have been created when the Node was created, so just read in the data
        dataBundleXml = nodeXml.findall('DataBundles/DataBundle')[0]
        self.dataBundle.read(dataBundleXml)  
        self.dataBundle.setNode(self) #Finall make sure that the dataBundle that has just been loaded in knows about node     


    def setIndex(self,value):
        self.index = value

    def getIndex(self):
        return self.index

    def getRadius(self):
        return self.radius

    def setRadius(self, radius):
        self.radius = radius

    def getMinimumScale(self):
        return self.minimumScale

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

    # def getWireName(self):
    #     return self.wireName

    # def setWireName(self,name):
    #     self.wireName = str(name)

    # def getWireGroup(self):
    #     if not self.wireGroup: print "WARNING : NO REGISTERED WIRE GROUP ON THE NODE, SO NO GROUP TO RETURN"
    #     return self.wireGroup

    # def setWireGroup(self, wireGroup):
    #     self.wireGroup = wireGroup
    #     self.wireName = wireGroup.getName()
    #     self.dataBundle.setHostName(self.wireName) #Passes the name of the wireGroup through to the DataBundle so attrbute names can be checked

    def getGroup(self):
        if not self.group: print "WARNING : NO REGISTERED GROUP ON THE NODE, SO NO GROUP TO RETURN"
        return self.group

    def setGroup(self, group):
        self.group = group
        self.groupName = group.getName()
        self.dataBundle.setHostName(self.groupName) #Passes the name of the wireGroup through to the DataBundle so attrbute names can be checked

    def getGroupName(self):
        return self.groupName

    def setGroupName(self, groupName):
        self.groupName = str(groupName) 

    def getColour(self):
        return self.colour

    def setColour(self, colour):
        if type(colour) == QtGui.QColor: self.colour = colour

    def isHighlighted(self):
        return self.hightlighted

    def setHighlighted(self, highlighted):
        self.hightlighted = bool(highlighted)
        self.update()
        # print "Highlighted Called: " + str(highlighted)

    def addRigCurve(self, rigCurve):
        self.rigCurveList.append(weakref.ref(rigCurve))
        # print "Rig Curve List is : " + str(self.rigCurveList) + " - for Node :" + str(self)

    def clearRigCurveList(self):
        """Method to run through all the curves in the rigCurveList and 
        throw out any dead ones, that could be caused by processes like Node Merging
        """

        for curve in self.rigCurveList:
            if curve() == None: self.rigCurveList.remove(curve)

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
        return self.pinTie() #Calls the weakreference, which will call the object itself

    def setPinTie(self, pinTie):
        if type(pinTie) == PinTie:
            self.pinTie = weakref.ref(pinTie)
            self.setPinTieIndex(pinTie.getIndex())
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PINTIE ALLOCATION"

    def getDataBundle(self):
        return self.dataBundle

    def setDataBundle(self, bundle):
        """Function to set dataBundle to the Node, but also the pass the node down into the DataBundle, and the associated AttributeConnectors"""
        self.dataBundle = bundle
        self.dataBundle.setNode(self)

    def clearData(self):
        """Function to loop through the DataBundle and make sure that all data and scene AnimCurve Nodes are cleaned up"""
        if self.dataBundle: #we Have a valid dataBundle, so clear it out
            self.dataBundle.clearData()

    def resetWireGroup(self):
        if self.group:
            self.group.resetNodes()

    def goHome(self):
        """Function to centralise the node back to the pin and update any associated rigCurves and pinTies"""
        print "Before Home Pos : " + str(self.pos().x()) + "," + str(self.pos().y()) 
        if self.pin:
            self.setPos(QtCore.QPointF(0,0))
            print "After Home Pos : " + str(self.pos().x()) + "," + str(self.pos().y()) 
            if self.dataBundle:
                self.dataBundle.setX(0.0)
                self.dataBundle.setY(0.0)
            if self.pinTie:
                self.pinTie().drawTie()
            self.dirtyCurve() # Redraw the curve that is going through the WireGroup
        else:
            print "WARNING : NODE HAS NO ASSOCIATED PIN AND AS SUCH HAS NO HOME TO GO TO :("

    def setDataBundleInfo(self):
        """Sets the Expected Attribute Name that will eventually be assigned to the Scene Controller as an extra attribute"""
        # attrName = str(self.wireName) + str(self.index)
        attrName = str(self.groupName) + str(self.index)
        self.dataBundle.setControllerAttrName(attrName)
        self.dataBundle.setNode(self)

    def dirtyCurve(self):
        "Marks any associated curves as dirty"
        # print "RigCurveList =  " + str(self.rigCurveList)
        for rigCurve in self.rigCurveList:
            rigCurve().dirtyCurve()

    def boundingRect(self):
        adjust = 2
        return QtCore.QRectF((-self.radius - adjust)*self.scale, (-self.radius - adjust)*self.scale,
                             (2*(self.radius + adjust))*self.scale, (2*(self.radius + adjust))*self.scale)

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        # painter.setPen(QtCore.Qt.NoPen)
        cColour = QtGui.QColor(25,25,50,150)
        if self.isSelected(): cColour = QtGui.QColor(220,220,255,150)
        if self.hightlighted:
            pen = QtGui.QPen(cColour, 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            gradient = QtGui.QRadialGradient(0, 0, self.scale*self.radius)
            gradient.setColorAt(0, self.colour)
            gradient.setColorAt(0.2, self.colour)
            gradient.setColorAt(0.9, QtGui.QColor(255,255,255, 255))
            gradient.setColorAt(1.0, QtGui.QColor(255,255,255, 10))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawEllipse(-self.radius*self.scale, -self.radius*self.scale, 2*self.radius*self.scale, 2*self.radius*self.scale)

        pen = QtGui.QPen(cColour, 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        gradient = QtGui.QRadialGradient(0, 0, self.scale*self.radius/2)
        gradient.setColorAt(0, self.colour)
        gradient.setColorAt(0.2, self.colour)
        gradient.setColorAt(0.3, QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(), 125))
        gradient.setColorAt(1.0, QtGui.QColor(self.colour.red(),self.colour.green(),self.colour.blue(), 10))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawEllipse(-self.radius*self.scale, -self.radius*self.scale, 2*self.radius*self.scale, 2*self.radius*self.scale)
        QtGui.QPen(QtCore.Qt.black, 1.2, QtCore.Qt.SolidLine)
        painter.drawEllipse((-self.radius/2)*self.scale, (-self.radius/2)*self.scale, self.radius*self.scale, self.radius*self.scale)
        # painter.drawRect(self.boundingRect()) #Testing Bounding Box....

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            #Item has been moved so report out the data using the dataBundle
            print "Firing"
            if self.dataBundle:
                newPos = self.pos()
                self.dataBundle.setX(newPos.x())
                self.dataBundle.setY(newPos.y())
                # print "Float Data : " + str(self.dataBundle.getX()) + ", " + str(self.dataBundle.getY()) 
            if self.pinTie:
                # print "There is a tie"
                self.pinTie().drawTie()
            self.dirtyCurve() # The node movement requires redrawing of the WireGroup Curve
            if self.getPin(): #Check to see if there is a pin
                if self.getPin().getConstraintItem(): #check to see if there is a constraint Item
                    if type(self.getPin().getConstraintItem()) == ConstraintLine: # We have the special case of the ConstraintLine in place
                        return self.mapFromScene(self.getPin().getConstraintItem().constrainItemChangedMovement(self.mapToScene(value))) #get the constraint cordinates and map them back to our local space
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # print "Before Click Pos : " + str(self.pos().x()) + "," + str(self.pos().y()) 
            self.setPos(self.mapToParent(event.pos())) #Trying to line centre of node to mouse move
            if self.dataBundle:
                newPos = self.pos()
                # print "After Click Pos : " + str(self.pos().x()) + "," + str(self.pos().y()) 
                self.dataBundle.setX(newPos.x())
                self.dataBundle.setY(newPos.y())
                # print "Mouse Click Float Data : " + str(self.dataBundle.getX()) + ", " + str(self.dataBundle.getY()) 
            if self.pinTie:
                # print "There is a tie"
                self.pinTie().drawTie()
            self.update()
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        return QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, mouseEvent):
        # check of mouse moved within the restricted area for the item 
        if self.getPin().getConstraintItem():
            return self.getPin().getConstraintItem().constrainMovement(mouseEvent)
        else: QtGui.QGraphicsItem.mouseMoveEvent(self, mouseEvent)



class NodePinReference():
    """This provides storage information of the wireGroup Name and Index of a Node/ControlPin 
    in another WireGroup, so it can be pulled in and shared into the current WireGroup.

    This occurs when Nodes are Merged across into other Wiregroups.
    """
    name = "NodePinReference"

    def __init__(self):
        self.index = None
        self.wireName = None

    def getIndex(self):
        return self.index

    def setIndex(self, index):
        self.index = int(index)

    def getWireName(self):
        return self.wireName

    def setWireName(self, wireName):
        self.wireName = str(wireName)

    def read(self, nodePinXml):
        """Function to read in some simple data into the reference Object so later we can locate the required Pin/Node"""
        for a in nodePinXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'wireName': self.setWireName(str(a.attrib['value']))


class SuperNode(Node):
    """A superNode subclasses the Node to give more flexibility and functionality

    The superNode exists by itself, with its parent Pin, and associated PinTie

    Its home is the location of its pin (origin in local space)

    SuperNodes can be constrained in their movement in the same way a Node can be.

    SuperNodes can also have skinning information associated with them
    (self.skinnedPins). This information allows the superNode to influence/move
    the Control Pins of nodes in a WireGroup. This is vital to reproduce visually
    accurate facial movements, especially around the lips, jaw and eyes

    SuperNodes can be drawn in different ways to represent different arrow type 
    controls. Currently this is done with switch statements, but should probably be
    upgraded to using polymorphism.

    """
    def __init__(self, nPos, dataProcessor):
        Node.__init__(self, nPos, dataProcessor)
        self.name = ""
        self.form = "Arrow_4Point" #Possibilities are arrow_4Point, arrow_sidePoint, arrow_upDownPoint  
        self.scale = 0.8
        self.scaleOffset = 2
        self.alpha = 1.0
        # self.superNodeGroup = None
        self.minimumScale = 0.2
        self.colour = QtGui.QColor(250,160,100,255*self.alpha)
        self.path = QtGui.QPainterPath()
        self.skinningItem = None
        self.skinnedPins = []
        
        self.dataProcessor = dataProcessor
        

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        superNodeRoot = xml.Element('SuperNode')
        attributes = xml.SubElement(superNodeRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'name', value = str(self.getName()))
        xml.SubElement(attributes, 'attribute', name = 'form', value = str(self.getForm()))
        xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
        xml.SubElement(attributes, 'attribute', name = 'radius', value = str(self.getRadius()))
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'pinIndex', value = str(self.getPinIndex()))
        xml.SubElement(attributes, 'attribute', name = 'pinTieIndex', value = str(self.getPinTieIndex()))
        # xml.SubElement(attributes, 'attribute', name = 'wireName', value = str(self.getWireName()))
        xml.SubElement(attributes, 'attribute', name = 'groupName', value = str(self.getGroupName()))
        xml.SubElement(attributes, 'attribute', name = 'colour', value = (str(self.getColour().red()) + "," + str(self.getColour().green()) + "," + str(self.getColour().blue())))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        if self.getBezierHandles(0) != None: xml.SubElement(attributes, 'attribute', name = 'bezierHandle0', value = (str(self.getBezierHandles(0)[0]) + "," + str(self.getBezierHandles(0)[1])))
        else: xml.SubElement(attributes, 'attribute', name = 'bezierHandle0', value = ("None"))
        if self.getBezierHandles(1) != None: xml.SubElement(attributes, 'attribute', name = 'bezierHandle1', value = (str(self.getBezierHandles(1)[0]) + "," + str(self.getBezierHandles(1)[1])))
        else: xml.SubElement(attributes, 'attribute', name = 'bezierHandle1', value = ("None"))

        #Store Skinning Information
        skinPinsXml = xml.SubElement(superNodeRoot,'SkinningPinInfos')
        for skinPin in self.skinnedPins:
            skinPinXml = skinPin.store()
            skinPinsXml.append(skinPinXml)

        # Now record the xml for the DataBundle if there is one
        dataBundlesXml = xml.SubElement(superNodeRoot,'DataBundles')
        if self.dataBundle:
            dataBundleXml = self.dataBundle.store()
            dataBundlesXml.append(dataBundleXml)

        return superNodeRoot

    def read(self, superNodeXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in superNodeXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'name': self.setName(str(a.attrib['value']))
            elif a.attrib['name'] == 'form': self.setForm(str(a.attrib['value']))
            elif a.attrib['name'] == 'radius': self.setRadius(float(a.attrib['value']))
            elif a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'pinIndex': self.setPinIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'pinTieIndex': self.setPinTieIndex(int(a.attrib['value']))
            # elif a.attrib['name'] == 'wireName': self.setWireName(str(a.attrib['value']))
            elif a.attrib['name'] == 'groupName': self.setGroupName(str(a.attrib['value']))
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
            elif a.attrib['name'] == 'colour':
                newColour = a.attrib['value'].split(",")
                self.setColour(QtGui.QColor(float(newColour[0]), float(newColour[1]),float(newColour[2]))) 

        # Read skinning information
        self.skinnedPins = [] # Clear Out all the Skinning info ready for the new values to be read in
        skinnedpinsXml = superNodeXml.findall('SkinningPinInfos')
        for skinPinXml in skinnedpinsXml[0].findall('SkinningPinInfo'):
            newSkinInfo = SkinningPinInfo()
            newSkinInfo.read(skinPinXml) # Read in names of WireGroups and PinIndexes
            newSkinInfo.setSuperNode(self)
            rigGVWireGroups = self.scene().views()[0].wireGroups
            for wireGroup in rigGVWireGroups:
                if wireGroup.getName() == newSkinInfo.getWireGroupName(): # We have found our WireGroup
                    newSkinInfo.setWireGroup(wireGroup)
                    for pin in wireGroup.pins:
                        if pin.getIndex() == newSkinInfo.getPinIndex(): # We have found our Pin
                            # Set the Pin, but without resetting the skinpos that we have already
                            # accurately loaded in.
                            newSkinInfo.setPin(pin, setSkinPos = False) 
            if newSkinInfo.getWireGroup() == None:
                print "WARNING: SkinningInfo has failed to fine correct WireGroup"
            if newSkinInfo.getPin() == None:
                print "WARNING: SkinningInfo has failed to fine correct Pin"
            self.skinnedPins.append(newSkinInfo)

        #Now we have to load in the dataBundle information. The dataBundle will have been created when the Node was created, so just read in the data
        dataBundleXml = superNodeXml.findall('DataBundles/DataBundle')[0]
        self.dataBundle.read(dataBundleXml)
        self.dataBundle.setNode(self) #Finall make sure that the dataBundle that has just been loaded in knows about node     


    def getName(self):
        return self.name

    def setName(self, name):
        self.name = str(name)

    # def getSuperNodeGroup(self):
    #     return self.superNodeGroup

    # def setSuperNodeGroup(self, superNodeGroup):
    #     self.superNodeGroup = superNodeGroup
    #     self.dataBundle.setHostName(superNodeGroup.getName()) #Passes the name of the SuperNodeGroup through to the DataBundle so attribute names can be checked

    def getForm(self):
        return self.form

    def setForm(self,form):
        self.form = str(form)
        self.update()

    def setColour(self,colour):
        if type(colour) == QtGui.QColor: self.colour = QtGui.QColor(colour.red(), colour.green(), colour.blue(), 255*self.alpha)

    def getSkinningItem(self):
        return self.skinningItem

    def setSkinningItem(self, skinningItem):
        if type(skinningItem) == SkinningEllipse: 
                self.skinningItem = skinningItem
                # print "Skin : " + str(self.skinningItem)

    def getSkinnedPins(self):
        return self.skinnedPins

    def setSkinnedPins(self, nodes):
        """Function to assign skinning Info for each of the nodes to the Super Node"""
        if self.skinningItem:
            self.skinnedPins = []
            self.goHome() #Send the superNode Home to neaten everything with rest poses
            superNodePinPos = self.getPin().pos()
            skinRadius = self.skinningItem.getWidth()
            for node in nodes: #find the pin of the node and assign a suitable skinning value
                node.goHome()
                pinDist = np.linalg.norm(npVec(node.getPin().pos()) - npVec(superNodePinPos)) #This might need to be separated in to separate skinning values for each axis
                skinValue = 1 - float(pinDist/skinRadius)
                skinValue = round(skinValue, 2)
                skinInfo = SkinningPinInfo()
                skinInfo.setSuperNode(self)
                skinInfo.setPin(node.getPin())
                # print "Wire Name : " + str(node.getWireGroup().getName())
                skinInfo.setWireGroup(node.getGroup())
                # print "get skin wire Name " + str(skinInfo.getWireGroupName())
                skinInfo.setSkinValue(skinValue)
                self.skinnedPins.append(skinInfo)
            
            #Now that we have skinned we need to remove the skinning Item
            self.scene().removeItem(self.skinningItem)
            self.skinningItem = None
            self.scene().views()[0].populateSkinningTable(self)
        else: 
            print "WARNING : CANNOT SKIN NODES/PINS SINCE NO SUITABLE SKINNING ITEM WAS FOUND ON THE SUPERNODE"

    def goHome(self):
        """Function to centralise the node back to the pin and update any associated rigCurves and pinTies"""
        print "Before Home Pos : " + str(self.pos().x()) + "," + str(self.pos().y()) 
        if self.pin:
            self.setPos(QtCore.QPointF(0,0))
            print "After Home Pos : " + str(self.pos().x()) + "," + str(self.pos().y()) 
            if self.dataBundle:
                self.dataBundle.setX(0.0)
                self.dataBundle.setY(0.0) 

        if self.pin:
            self.setPos(QtCore.QPointF(0,0))
            if self.pinTie:
                self.pinTie().drawTie()
            self.dirtyCurve() # The SuperNode movement requires redrawing of the Curve if there is one
            for skinPin in self.skinnedPins: 
                skinPin.goHome()
                homeNode = skinPin.getPin().getNode()
                if homeNode:  #Hacky way of updating the curves when the pin is sent home! Maybe wrap into a neat function
                    homeNode.dirtyCurve()    
        else:
            print "WARNING : NODE HAS NO ASSOCIATED PIN AND AS SUCH HAS NO HOME TO GO TO :("


    def drawArrow_4Point(self, painter, option, widget):
        penCol = self.colour
        pen = QtGui.QPen(penCol, 1, QtCore.Qt.SolidLine)

        if self.hightlighted: #If the node is highlighted for dataTable Identifying purposes
            penCol = QtGui.QColor(240,240,255,200)
            pen = QtGui.QPen(penCol, 3 , QtCore.Qt.SolidLine)

        painter.setPen(pen)

        self.path = QtGui.QPainterPath()
        self.path.moveTo(QtCore.QPointF(3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(15*self.scaleOffset*self.scale,0*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,-6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(6*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(0*self.scaleOffset*self.scale,-15*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-6*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,-6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-15*self.scaleOffset*self.scale,0*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-6*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(0*self.scaleOffset*self.scale,15*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(6*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))

    def drawArrow_sidePoint(self, painter, option, widget):
        penCol = self.colour
        pen = QtGui.QPen(penCol, 1, QtCore.Qt.SolidLine)

        if self.hightlighted: #If the node is highlighted for dataTable Identifying purposes
            penCol = QtGui.QColor(240,240,255,200)
            pen = QtGui.QPen(penCol, 3 , QtCore.Qt.SolidLine)

        painter.setPen(pen)

        self.path = QtGui.QPainterPath()
        self.path.moveTo(QtCore.QPointF(3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(15*self.scaleOffset*self.scale,0*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,-6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(9*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,-6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-15*self.scaleOffset*self.scale,0*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,6*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-9*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))

    def drawArrow_upDownPoint(self, painter, option, widget):
        penCol = self.colour
        pen = QtGui.QPen(penCol, 1, QtCore.Qt.SolidLine)

        if self.hightlighted: #If the node is highlighted for dataTable Identifying purposes
            penCol = QtGui.QColor(240,240,255,200)
            pen = QtGui.QPen(penCol, 3 , QtCore.Qt.SolidLine)

        painter.setPen(pen)

        self.path = QtGui.QPainterPath()
        self.path.moveTo(QtCore.QPointF(3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(6*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(0*self.scaleOffset*self.scale,-15*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-6*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,-9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,-3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-3*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(-6*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(0*self.scaleOffset*self.scale,15*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(6*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,9*self.scaleOffset*self.scale))
        self.path.lineTo(QtCore.QPointF(3*self.scaleOffset*self.scale,3*self.scaleOffset*self.scale))

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        if self.form == "Arrow_4Point": self.drawArrow_4Point(painter, option, widget)
        elif self.form == "Arrow_sidePoint": self.drawArrow_sidePoint(painter, option, widget)
        elif self.form == "Arrow_upDownPoint": self.drawArrow_upDownPoint(painter, option, widget)
        else: return Node.paint(self, painter, option, widget)
        painter.strokePath(self.path, painter.pen())

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for skinPin in self.skinnedPins: 
                skinPin.update() #Update the pin positions of the skinned Nodes
                skinPin.getPin().itemChange(change, value)

        elif change == QtGui.QGraphicsItem.ItemSelectedChange:
            # if value.toBool():
            if value:
                self.scene().views()[0].populateSkinningTable(self)
                # self.scene().views()[0].skinTableWidget.populate(self)

        Node.itemChange(self, change, value)      
        return Node.itemChange(self, change, value)

############################################CONSTRAINT ITEMS###############################################################################

#RESTRICTION ITEMS
class OpsRotation(QtGui.QGraphicsItem):
    """This is the small red curve with two arrows serving as rotation control

    This item is used to control the rotation of constraintItems

    It sits as a child of the ControlPin, but responds to mouseclick and mousemove
    methods to induce a rotation in its parent ControlPin, which in turn rotates
    the entire constraintItem system

    """
    def __init__(self, constraintItem):
        QtGui.QGraphicsItem.__init__(self)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,False)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.scale = 1.0
        self.alpha = 1.0
        self.length = 1.0
        self.constraintItem = constraintItem
        self.setZValue(2)

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        OpsRotXml = xml.Element('OpsRot')
        attributes = xml.SubElement(OpsRotXml,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'length', value = str(self.getLength()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        return OpsRotXml

    def read(self, OpsRotXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in OpsRotXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'length': self.setLength(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getLength(self):
        return self.length

    def setLength(self,length):
        self.length = length

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)

    def boundingRect(self):
        adjust = 0
        return QtCore.QRectF(self.scale*self.length*(-10 - adjust), self.scale*self.length*(-5 - adjust),
                             self.scale*self.length*(20 + 2*adjust), self.scale*self.length*(10 + 2*adjust))       

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        wCurve1 = QtGui.QPainterPath()

        locAx = -7.8 * self.scale*self.length
        locAy = -2 * self.scale*self.length

        locBx = -4 * self.scale*self.length
        locBy = 0 * self.scale*self.length

        pen = QtGui.QPen(QtGui.QColor(255,20,0,255*self.alpha), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        wCurve1 = QtGui.QPainterPath()
        wCurve1.moveTo(QtCore.QPointF(locAx,-locAy))
        wCurve1.cubicTo(QtCore.QPointF(locBx,-locBy),QtCore.QPointF(-locBx,-locBy),QtCore.QPointF(-locAx,-locAy))
        painter.strokePath(wCurve1, painter.pen())
        
        pen = QtGui.QPen(QtGui.QColor(255,20,0,255*self.alpha), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(locAx-0.5,-locAy,locAx+2,-locAy+1)
        painter.drawLine(locAx-0.5,-locAy,locAx+1,-locAy-2)

        painter.drawLine(-locAx+0.5,-locAy,-locAx-2,-locAy+1)
        painter.drawLine(-locAx+0.5,-locAy,-locAx-1,-locAy-2)

    def mousePressEvent(self, event):
        if self.parentItem().getNode(): self.parentItem().getNode().goHome() #If we are adjusting the constraint area, then first send the node home
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.parentItem() and self.constraintItem:
            # print "Event Pos : " + str(self.mapToScene(event.pos()))
            s_coords = self.constraintItem.sceneCoordinates(self.mapToScene(event.pos()))
            theta_deg = self.constraintItem.calculateAngle(s_coords)   
            self.constraintItem.doTransform(theta_deg, s_coords[2], s_coords[3])

        # QtGui.QGraphicsItem.mouseMoveEvent(self, event)


class OpsCross(QtGui.QGraphicsItem):
    """This is a small red cross that is used to visually define the dimensions of shapes

    It is used to control the shapes and line lengths of constraintItems and SkinningItems

    It is added as child of the ControlPin as part of a constraintItem

    By clicking and dragging this item, provides the information to redefine the shape or 
    line length of the constraint Item or SkinningItem

    """
    def __init__(self, constraintItem):
        QtGui.QGraphicsItem.__init__(self)
        self.scale = 1.0
        self.alpha = 1.0
        self.length = 4
        self.slider = False
        self.sliderLimit = 0
        self.index = 0
        self.constraintItem = constraintItem
        self.setZValue(2)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)


    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        OpsCrossXml = xml.Element('OpsCross')
        attributes = xml.SubElement(OpsCrossXml,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'length', value = str(self.getLength()))
        xml.SubElement(attributes, 'attribute', name = 'slider', value = str(self.isSlider()))
        xml.SubElement(attributes, 'attribute', name = 'sliderLimit', value = str(self.getSliderLimit()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        return OpsCrossXml

    def read(self, OpsCrossXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in OpsCrossXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'length': self.setLength(float(a.attrib['value']))
            elif a.attrib['name'] == 'slider': self.setSlider(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'sliderLimit': self.setSliderLimit(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))


    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getLength(self):
        return self.length

    def setLength(self,length):
        self.length = length

    def isSlider(self):
        return self.slider

    def setSlider(self, slider):
        self.slider = bool(slider)

    def getSliderLimit(self):
        return self.sliderLimit

    def setSliderLimit(self, limit):
        self.sliderLimit = limit

    def getIndex(self):
        return self.index

    def setIndex(self, index):
        self.index = int(index)

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)

    def boundingRect(self):
        adjust = 1
        return QtCore.QRectF(self.scale*(-self.length - adjust), self.scale*(-self.length - adjust),
                             self.scale*(2*self.length + 2*adjust), self.scale*(2*self.length + 2*adjust))        

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        pen = QtGui.QPen(QtGui.QColor(255,0,0,200*self.alpha), 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.scale*-self.length,0,self.scale*self.length,0)
        painter.drawLine(0,self.scale*self.length,0,self.scale*-self.length)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25*self.alpha))) #shade in the circle
        # painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        if self.parentItem().getNode(): 
            self.parentItem().getNode().goHome() #If we are adjusting the constraint area, then first send the node home
            self.scene().clearSelection() #if we are manipulating this constraint area, then all other scene items should be deselected
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.isSlider():
            pass
        else:
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

    def itemChange(self, change, value):
        if self.isSlider(): #Check if the cross is meant to have restricted movement
            if change == QtGui.QGraphicsItem.ItemPositionChange:
                yPos = 0
                if self.getIndex() == 0:
                    # print "Hit Head"
                    # yPos = value.toPointF().y()
                    yPos = value.y()
                    if yPos >= 0 - self.getSliderLimit():
                        yPos = 0 - self.getSliderLimit()
                    self.parentItem().redraw(0)
                    # print "Head Pos : " + str(yPos)
                elif self.getIndex() == 1:
                    # print "Hit Tail"
                    # yPos = value.toPointF().y()
                    yPos = value.y()
                    if yPos <= 0 + self.getSliderLimit():
                        yPos = 0 + self.getSliderLimit()
                    self.parentItem().redraw(1)                   
                return QtCore.QPointF(0,yPos)
            return QtGui.QGraphicsItem.itemChange(self, change, value)
        else: return QtGui.QGraphicsItem.itemChange(self, change, value)


class ConstraintEllipse(QtGui.QGraphicsEllipseItem):
    """This is used to constrain the movement of a node or superNode to within the Ellipse Shape

    An OpsCross and OpsRotation item is used to define its shape and rotation.

    This ConstraintItem is parented to the ControlPin of the Node. It does not rotate itself, but
    appears to rotate since the ControlPin (parent) is being rotated from instructions from the 
    OpsRotation Item

    There is probably a way to optimise the code across the ConstraintItems 
    (ConstraintEllipse, ConstraintRect and ConstraintLine)

    """
    name = "ConstraintEllipse"

    def __init__(self):
        self.scale = 1.0
        self.width = 25
        self.height = 25
        self.alpha = 1.0
        self.ghostArea = False
        self.extension = 15.0
        QtGui.QGraphicsEllipseItem.__init__(self, -self.width, -self.height, 2*self.width, 2*self.height) 
        self.opX = None
        self.opRot = None
        self.pin = None
        self.pinIndex = 0
        self.node = None
        self.nodeIndex = 0
        self.setZValue(2)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True) 
        self.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent,True)      
        self.initBuild()

    def initBuild(self):
        self.opX = OpsCross(self)
        self.opX.setParentItem(self)
        self.opX.setPos(QtCore.QPointF(self.width,-self.height))

        self.opRot = OpsRotation(self)
        self.opRot.setParentItem(self)
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-9))

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        ConstraintEllipseXml = xml.Element('ConstraintEllipse')
        attributes = xml.SubElement(ConstraintEllipseXml,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'height', value = str(self.getHeight()))
        xml.SubElement(attributes, 'attribute', name = 'width', value = str(self.getWidth()))
        xml.SubElement(attributes, 'attribute', name = 'ghostArea', value = str(self.isGhostArea()))
        xml.SubElement(attributes, 'attribute', name = 'extension', value = str(self.getExtension()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        
        #Now record the xml for the OpCross
        OpsItemsXml = xml.SubElement(ConstraintEllipseXml,'OpsItems')
        OpCXml = self.opX.store()
        OpsItemsXml.append(OpCXml)
        OpRXml = self.opRot.store()
        OpsItemsXml.append(OpRXml)
        return ConstraintEllipseXml

    def read(self, ConstraintEllipseXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in ConstraintEllipseXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'height': self.setHeight(float(a.attrib['value']))
            elif a.attrib['name'] == 'width': self.setWidth(float(a.attrib['value']))
            elif a.attrib['name'] == 'extension': self.setExtension(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

        #The Ops Cross and OpsRot are created, so hunt through the XML and make sure all their attributes are loaded in
        OpsItemsXml = ConstraintEllipseXml.findall('OpsItems')
        for itemXml in OpsItemsXml[0]: #This should only find One OpsCross
            if itemXml.tag == "OpsCross": self.opX.read(itemXml)
            if itemXml.tag == "OpsRot": self.opRot.read(itemXml)
        self.redraw(self.opX.pos())
        self.lock()

        for a in ConstraintEllipseXml.findall( 'attributes/attribute'): #Finsh by setting and ghost visibility states
            if a.attrib['name'] == 'ghostArea': self.setGhostArea(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
        self.update()

    def mapAttributes(self,constraintItem):
        """Function to map the attributes across to the input constrainItem"""
        constraintItem.setScale(self.getScale())
        constraintItem.setWidth(self.getWidth())
        constraintItem.setHeight(self.getHeight())
        constraintItem.setAlpha(self.getAlpha())
        constraintItem.setGhostArea(self.isGhostArea())
        constraintItem.opX.setPos(self.opX.pos())
        constraintItem.redraw(self.opX.pos())
        constraintItem.setVisible(self.isVisible())

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getHeight(self):
        return self.height

    def setHeight(self,height):
        self.height = height

    def getExtension(self):
        return self.extension

    def setExtension(self,extension):
        self.extension = extension

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)
        self.opX.setAlpha(float(alpha))
        self.opRot.setAlpha(float(alpha))

    def isGhostArea(self):
        return self.ghostArea

    def setGhostArea(self, ghost):
        self.ghostArea = bool(ghost)
        self.opX.setVisible(not bool(ghost))
        self.opRot.setVisible(not bool(ghost))

    def getPinIndex(self):
        return self.pinIndex

    def setPinIndex(self, index):
        self.pinIndex = index

    def getPin(self):
        return self.pin

    def setPin(self, pin):
        if type(pin) == ControlPin:
            self.pin = pin
            self.setPinIndex(pin.getIndex())
            self.setParentItem(pin)
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PIN ALLOCATION"

    def getNodeIndex(self):
        return self.nodeIndex

    def setNodeIndex(self, index):
        self.nodeIndex = index

    def getNode(self):
        return self.node

    def setNode(self, node):
        if type(node) == Node or type(node) == SuperNode:
            self.node = node
            self.setNodeIndex(node.getIndex())
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO ITEM FOR ALLOCATION"

    def lock(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False)  
        self.opX.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False) 

    def calibrateDataBundle(self):
        if self.node:
            if self.node.dataBundle:
                dBundle = self.node.dataBundle
                dBundle.setMaxX(self.width)
                dBundle.setMinX(-self.width)
                dBundle.setMaxY(self.height)
                dBundle.setMinY(-self.height)

    def boundingRect(self):
        adjust = 2
        return QtCore.QRectF(self.scale*(-self.width - adjust), self.scale*(-self.height - adjust - self.extension-3),
                             self.scale*(2*self.width + 2*adjust), self.scale*(2*self.height + adjust + 2*self.extension + 5))

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        self.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25*self.alpha))) #shade in the circle
        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
        if not self.ghostArea: self.setPen(pen)
        else: 
            self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,15*self.alpha))) #shade in the circle
        QtGui.QGraphicsEllipseItem.paint(self, painter, option, widget)
        if not self.ghostArea:
            pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(0,self.scale*self.height - 2,0,self.scale*-self.height-self.extension) 
            pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            if self.width > 5:
                painter.drawLine(-5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))     
                painter.drawLine(5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))
            else:
                painter.drawLine(-self.width,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))     
                painter.drawLine(self.width,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))
            if self.width > 3: painter.drawLine(3,0,-3,0)
            else: painter.drawLine(self.width,0,-self.width,0)

    def redraw(self, dimPos):
        self.width = abs(dimPos.x())
        self.height = abs(dimPos.y())
        self.setRect(self.scale*(-self.width), self.scale*(-self.height),
                             self.scale*(2*self.width), self.scale*(2*self.height)) 
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))
        self.calibrateDataBundle()

    def sceneCoordinates(self, sMousePt): #Code curtesy of ZetCode
        s_mouse_x = sMousePt.x()
        s_mouse_y = sMousePt.y()
        constraintCentre = self.boundingRect().center()
        arrow_x = constraintCentre.x()
        arrow_y = constraintCentre.y()
        sConstraintPt = self.mapToScene(arrow_x, arrow_y)
        s_arrow_x = sConstraintPt.x()
        s_arrow_y = sConstraintPt.y() 
        return (s_mouse_x, s_mouse_y, arrow_x, arrow_y, 
            s_arrow_x, s_arrow_y)
 
    def calculateAngle(self, coords):
        s_mouse_x, s_mouse_y = coords[0], coords[1] 
        s_arrow_x, s_arrow_y = coords[4], coords[5]
        a = abs(s_mouse_x - s_arrow_x)
        b = abs(s_mouse_y - s_arrow_y)
        # print "Opposite : " + str(a)
        # print "Adjacent : " + str(b)
        theta_deg = 0.0

        if a == 0 and b == 0:
            return
        elif a == 0 and s_mouse_y < s_arrow_y:
            theta_deg = 270
        elif a == 0 and s_mouse_y > s_arrow_y: 
            theta_deg = 90
        else:
            theta_rad = math.atan(b / a)
            theta_deg = math.degrees(theta_rad)
            if (s_mouse_x < s_arrow_x and \
                s_mouse_y > s_arrow_y):
                theta_deg = 180 - theta_deg
            elif (s_mouse_x < s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 180 + theta_deg   
            elif (s_mouse_x > s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 360 - theta_deg               
        # print str(theta_deg)
        return (theta_deg + 90)

    def doTransform(self, theta_deg, arrow_x, arrow_y):
        if self.getPin():
            self.getPin().setRotation(theta_deg)

    def mouseMoveEvent(self, mouseEvent):
        if self.pin == None: return QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, mouseEvent) #If there is no pin we are free to move, else we are locked to a pin

    def constrainMovement(self, mouseEvent):
        if self.contains(self.mapFromScene(mouseEvent.scenePos())): # make sure the incoming cordinates are map to the constraint Item for processing "contains"
            # print "node is : " + str(self.node)
            return QtGui.QGraphicsItem.mouseMoveEvent(self.node, mouseEvent)


class ConstraintRect(QtGui.QGraphicsRectItem):
    """This is used to constrain the movement of a node or superNode to within the Rectangle Shape

    An OpsCross and OpsRotation item is used to define its shape and rotation.

    This ConstraintItem is parented to the ControlPin of the Node. It does not rotate itself, but
    appears to rotate since the ControlPin (parent) is being rotated from instructions from the 
    OpsRotation Item

    There is probably a way to optimise the code across the ConstraintItems 
    (ConstraintEllipse, ConstraintRect and ConstraintLine)

    """    

    name = "ConstraintRect"

    def __init__(self):
        self.scale = 1.0
        self.alpha = 1.0
        self.width = 25
        self.height = 25
        self.ghostArea = False
        self.extension = 15.0
        QtGui.QGraphicsRectItem.__init__(self, -self.width , -self.height, 2*self.width, 2*self.height) 
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent,True)      
        self.opX = None
        self.pin = None
        self.pinIndex = 0
        self.node = None
        self.nodeIndex = 0
        self.setZValue(2)
        self.initBuild()

    def initBuild(self):
        self.opX = OpsCross(self)
        self.opX.setParentItem(self)
        self.opX.setPos(QtCore.QPointF(self.width,-self.height))
        
        self.opRot = OpsRotation(self)
        self.opRot.setParentItem(self)
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        ConstraintRectXml = xml.Element('ConstraintRect')
        attributes = xml.SubElement(ConstraintRectXml,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'height', value = str(self.getHeight()))
        xml.SubElement(attributes, 'attribute', name = 'width', value = str(self.getWidth()))
        xml.SubElement(attributes, 'attribute', name = 'ghostArea', value = str(self.isGhostArea()))
        xml.SubElement(attributes, 'attribute', name = 'extension', value = str(self.getExtension()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        
        #Now record the xml for the OpCross
        OpsItemsXml = xml.SubElement(ConstraintRectXml,'OpsItems')
        OpCXml = self.opX.store()
        OpsItemsXml.append(OpCXml)
        OpRXml = self.opRot.store()
        OpsItemsXml.append(OpRXml)
        return ConstraintRectXml

    def read(self, ConstraintRectXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in ConstraintRectXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'height': self.setHeight(float(a.attrib['value']))
            elif a.attrib['name'] == 'width': self.setWidth(float(a.attrib['value']))
            elif a.attrib['name'] == 'extension': self.setExtension(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))
            #The Ops Cross and OpsRot are created, so hunt through the XML and make sure all their attributes are loaded in
        OpsItemsXml = ConstraintRectXml.findall('OpsItems')
        for itemXml in OpsItemsXml[0]: #This should only find One OpsCross
            if itemXml.tag == "OpsCross": self.opX.read(itemXml)
            if itemXml.tag == "OpsRot": self.opRot.read(itemXml)
        self.redraw(self.opX.pos())
        self.lock()

        for a in ConstraintRectXml.findall( 'attributes/attribute'): #Finsh by setting and ghost visibility states
            if a.attrib['name'] == 'ghostArea': self.setGhostArea(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
        self.update()

    def mapAttributes(self,constraintItem):
        """Function to map the attributes across to the input constrainItem"""
        constraintItem.setScale(self.getScale())
        constraintItem.setWidth(self.getWidth())
        constraintItem.setHeight(self.getHeight())
        constraintItem.setAlpha(self.getAlpha())
        constraintItem.setGhostArea(self.isGhostArea())
        constraintItem.opX.setPos(self.opX.pos())
        constraintItem.redraw(self.opX.pos())
        constraintItem.setVisible(self.isVisible())

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getHeight(self):
        return self.height

    def setHeight(self,height):
        self.height = height

    def getExtension(self):
        return self.extension

    def setExtension(self,extension):
        self.extension = extension

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)
        self.opX.setAlpha(float(alpha))
        self.opRot.setAlpha(float(alpha))

    def isGhostArea(self):
        return self.ghostArea

    def setGhostArea(self, ghost):
        self.ghostArea = bool(ghost)
        self.opX.setVisible(not bool(ghost))
        self.opRot.setVisible(not bool(ghost))

    def getPinIndex(self):
        return self.pinIndex

    def setPinIndex(self, index):
        self.pinIndex = index

    def getPin(self):
        return self.pin

    def setPin(self, pin):
        if type(pin) == ControlPin:
            self.pin = pin
            self.setPinIndex(pin.getIndex())
            self.setParentItem(pin)
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PIN ALLOCATION"

    def getNodeIndex(self):
        return self.nodeIndex

    def setNodeIndex(self, index):
        self.nodeIndex = index

    def getNode(self):
        return self.node

    def setNode(self, node):
        if type(node) == Node or type(node) == SuperNode:
            self.node = node
            self.setNodeIndex(node.getIndex())
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO CONSTRAINITEM FOR CONSTRAINT ALLOCATION"

    def lock(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False)  
        self.opX.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False) 


    def calibrateDataBundle(self):
        if self.node:
            if self.node.dataBundle:
                dBundle = self.node.dataBundle
                dBundle.setMaxX(self.width)
                dBundle.setMinX(-self.width)
                dBundle.setMaxY(self.height)
                dBundle.setMinY(-self.height)

    def boundingRect(self):
        adjust = 2
        return QtCore.QRectF(self.scale*(-self.width - adjust), self.scale*(-self.height - adjust - self.extension),
                             self.scale*(2*self.width + 2*adjust), self.scale*(2*self.height + 2*adjust + 2*self.extension))

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
        self.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,25*self.alpha))) #shade in the rect
        if not self.ghostArea: self.setPen(pen)
        else: 
            self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.setBrush(QtGui.QBrush(QtGui.QColor(255,20,0,15*self.alpha))) #shade in the rect
        QtGui.QGraphicsRectItem.paint(self, painter, option, widget)

        if not self.ghostArea:
            painter.drawLine(0,self.scale*self.height - 2,0,self.scale*-self.height-self.extension)  
            pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            if self.width > 5:
                painter.drawLine(-5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))     
                painter.drawLine(5,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))
            else:
                painter.drawLine(-self.width,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))     
                painter.drawLine(self.width,-(self.scale*self.height+self.extension-5),0,-(self.scale*self.height+self.extension))
            if self.width > 3: painter.drawLine(3,0,-3,0)
            else: painter.drawLine(self.width,0,-self.width,0)


    def redraw(self, dimPos):
        self.width = abs(dimPos.x())
        self.height = abs(dimPos.y())
        self.setRect(self.scale*(-self.width), self.scale*(-self.height),
                             self.scale*(2*self.width), self.scale*(2*self.height))  
        self.opRot.setPos(QtCore.QPointF(0,-self.height-self.extension-5))
        self.calibrateDataBundle()

    def sceneCoordinates(self, sMousePt): #Code curtesy of ZetCode
        s_mouse_x = sMousePt.x()
        s_mouse_y = sMousePt.y()
        constraintCentre = self.boundingRect().center()
        arrow_x = constraintCentre.x()
        arrow_y = constraintCentre.y()
        sConstraintPt = self.mapToScene(arrow_x, arrow_y)
        s_arrow_x = sConstraintPt.x()
        s_arrow_y = sConstraintPt.y() 
        return (s_mouse_x, s_mouse_y, arrow_x, arrow_y, 
            s_arrow_x, s_arrow_y)
 
    def calculateAngle(self, coords):
        s_mouse_x, s_mouse_y = coords[0], coords[1] 
        s_arrow_x, s_arrow_y = coords[4], coords[5]
        a = abs(s_mouse_x - s_arrow_x)
        b = abs(s_mouse_y - s_arrow_y)
        # print "Opposite : " + str(a)
        # print "Adjacent : " + str(b)
        theta_deg = 0.0

        if a == 0 and b == 0:
            return
        elif a == 0 and s_mouse_y < s_arrow_y:
            theta_deg = 270
        elif a == 0 and s_mouse_y > s_arrow_y: 
            theta_deg = 90
        else:
            theta_rad = math.atan(b / a)
            theta_deg = math.degrees(theta_rad)
            if (s_mouse_x < s_arrow_x and \
                s_mouse_y > s_arrow_y):
                theta_deg = 180 - theta_deg
            elif (s_mouse_x < s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 180 + theta_deg   
            elif (s_mouse_x > s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 360 - theta_deg               
        # print str(theta_deg)
        return (theta_deg + 90)

    def doTransform(self, theta_deg, arrow_x, arrow_y):
        if self.getPin():
            self.getPin().setRotation(theta_deg)

    def mouseMoveEvent(self, mouseEvent):
        if self.pin == None: return QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, mouseEvent) #If there is no pin we are free to move, else we are locked to a pin

    def constrainMovement(self, mouseEvent):
        if self.contains(self.mapFromScene(mouseEvent.scenePos())): # make sure the incoming cordinates are map to the constraint Item for processing "contains"
            return QtGui.QGraphicsItem.mouseMoveEvent(self.node, mouseEvent)


class ConstraintLine(QtGui.QGraphicsItem):
    """This is used to constrain the movement of a node or superNode to a straight Line

    Two OpsCrosses and a OpsRotation item are used to define its shape and rotation.

    This ConstraintItem is parented to the ControlPin of the Node. It does not rotate itself, but
    appears to rotate since the ControlPin (parent) is being rotated from instructions from the 
    OpsRotation Item

    There is probably a way to optimise the code across the ConstraintItems 
    (ConstraintEllipse, ConstraintRect and ConstraintLine)

    """ 

    name = "ConstraintLine"

    def __init__(self):
        QtGui.QGraphicsItem.__init__(self) 
        self.scale = 1.0
        self.alpha = 1.0
        self.headLength = 25
        self.tailLength = 25
        self.ghostArea = False
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,False)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False)
        self.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent,True)      
        self.crossOffset = 7
        self.opXHead = None
        self.opXTail = None
        self.pin = None
        self.pinIndex = 0
        self.node = None
        self.nodeIndex = 0
        self.setZValue(2)
        self.initBuild()

    def initBuild(self):
        self.opXHead = OpsCross(self)
        self.opXHead.setParentItem(self)
        self.opXHead.setPos(QtCore.QPointF(0,-self.headLength - self.crossOffset))
        self.opXHead.setSlider(True)
        self.opXHead.setSliderLimit(self.crossOffset)
        
        self.opXTail = OpsCross(self)
        self.opXTail.setParentItem(self)
        self.opXTail.setPos(QtCore.QPointF(0,self.tailLength + self.crossOffset))
        self.opXTail.setIndex(1)
        self.opXTail.setSlider(True)
        self.opXTail.setSliderLimit(self.crossOffset)

        self.opRot = OpsRotation(self)
        self.opRot.setParentItem(self)
        self.opRot.setPos(QtCore.QPointF(0,-self.headLength - self.crossOffset - 9))

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        ConstraintLineXml = xml.Element('ConstraintLine')
        attributes = xml.SubElement(ConstraintLineXml,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'headLength', value = str(self.getHeadLength()))
        xml.SubElement(attributes, 'attribute', name = 'tailLength', value = str(self.getTailLength()))
        xml.SubElement(attributes, 'attribute', name = 'ghostArea', value = str(self.isGhostArea()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        
        #Now record the xml for the OpCross
        OpsItemsXml = xml.SubElement(ConstraintLineXml,'OpsItems')
        OpCHeadXml = self.opXHead.store()
        OpsItemsXml.append(OpCHeadXml)
        OpCTailXml = self.opXTail.store()
        OpsItemsXml.append(OpCTailXml)
        OpRXml = self.opRot.store()
        OpsItemsXml.append(OpRXml)
        return ConstraintLineXml

    def read(self, ConstraintLineXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in ConstraintLineXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'headLength': self.setHeadLength(float(a.attrib['value']))
            elif a.attrib['name'] == 'tailLength': self.setTailLength(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))
            #The Ops Cross and OpsRot are created, so hunt through the XML and make sure all their attributes are loaded in
        OpsItemsXml = ConstraintLineXml.findall('OpsItems')
        for index, itemXml in enumerate(OpsItemsXml[0]): #This will return two OpsCross, the first is the head, the second is the tail
            if itemXml.tag == "OpsCross" and index == 0: self.opXHead.read(itemXml)
            elif itemXml.tag == "OpsCross" and index == 1: self.opXTail.read(itemXml)
            elif itemXml.tag == "OpsRot": self.opRot.read(itemXml)
        self.redraw(0) #Redraw for both the head and tail OpCrosses
        self.redraw(1)
        self.lock()

        for a in ConstraintLineXml.findall( 'attributes/attribute'): #Finsh by setting and ghost visibility states
            if a.attrib['name'] == 'ghostArea': self.setGhostArea(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
        self.update()


    def mapAttributes(self,constraintItem):
        """Function to map the attributes across to the input constrainItem"""
        constraintItem.setScale(self.getScale())
        constraintItem.setAlpha(self.getAlpha())
        constraintItem.setHeadLength(self.getHeadLength())
        constraintItem.setTailLength(self.getTailLength())        
        constraintItem.setGhostArea(self.isGhostArea())
        constraintItem.opXHead.setPos(self.opXHead.pos())
        constraintItem.opXTail.setPos(self.opXTail.pos())
        constraintItem.redraw(0) #redraw head and tail postions
        constraintItem.redraw(1)
        constraintItem.setVisible(self.isVisible())

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getHeadLength(self):
        return self.headLength

    def setHeadLength(self, headLength):
        self.headLength = headLength

    def getTailLength(self):
        return self.tailLength

    def setTailLength(self, tailLength):
        self.tailLength = tailLength

    def isGhostArea(self):
        return self.ghostArea

    def setGhostArea(self, ghost):
        self.ghostArea = bool(ghost)
        self.opXHead.setVisible(not bool(ghost))
        self.opXTail.setVisible(not bool(ghost))
        self.opRot.setVisible(not bool(ghost))

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)
        self.opXHead.setAlpha(float(alpha))
        self.opXTail.setAlpha(float(alpha))
        self.opRot.setAlpha(float(alpha))

    def getPinIndex(self):
        return self.pinIndex

    def setPinIndex(self, index):
        self.pinIndex = index

    def getPin(self):
        return self.pin

    def setPin(self, pin):
        if type(pin) == ControlPin:
            self.pin = pin
            self.setPinIndex(pin.getIndex())
            self.setParentItem(pin)
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PIN ALLOCATION"

    def getNodeIndex(self):
        return self.nodeIndex

    def setNodeIndex(self, index):
        self.nodeIndex = index

    def getNode(self):
        return self.node

    def setNode(self, node):
        if type(node) == Node or type(node) == SuperNode:
            self.node = node
            self.setNodeIndex(node.getIndex())
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO CONSTRAINITEM FOR CONSTRAINT ALLOCATION"

    def lock(self):
        """This method pretty much shuts the graphical representation of the contraintLine down, so that it does
        not get in the way for when the user tries to interact with more useful objects
        """
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,False)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False)  
        self.opXHead.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False) 
        self.opXTail.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False) 

    def calibrateDataBundle(self):
        if self.node:
            if self.node.dataBundle:
                dBundle = self.node.dataBundle
                dBundle.setMaxX(0)
                dBundle.setMinX(0)
                dBundle.setMaxY(self.tailLength)
                dBundle.setMinY(-self.headLength)

    def boundingRect(self):
        adjust = 2
        return QtCore.QRectF(self.scale*(-5 - adjust), self.scale*(-self.headLength - adjust +1 ),
                             self.scale*(10 + 2*adjust), self.scale*(self.headLength + self.tailLength + 2))

    def paint(self, painter, option, widget):
        # QtGui.QGraphicsRectItem.paint(self, painter, option, widget)
        self.prepareGeometryChange()
        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
        if self.ghostArea: pen = QtGui.QPen(QtGui.QColor(0,0,0,100*self.alpha), 0.25, QtCore.Qt.SolidLine)

        painter.setPen(pen)
        painter.drawLine(0,1*self.scale*self.tailLength,0,1*self.scale*-self.headLength) 
        painter.drawLine(5,self.scale*-self.headLength,-5,self.scale*-self.headLength)
        painter.drawLine(5,self.scale*self.tailLength,-5,self.scale*self.tailLength)
        painter.drawLine(3,0,-3,0)

    def redraw(self, index): #index indicates which cross we are interested in - on this Line 0 is a head, and 1 is a tail
        if index == 0:
            self.setHeadLength(abs(self.opXHead.pos().y()) - self.crossOffset)
            self.opRot.setPos(QtCore.QPointF(0,-self.headLength - self.crossOffset - 9))
        elif index == 1:
            self.setTailLength(abs(self.opXTail.pos().y()) - self.crossOffset)
        self.update()
        self.calibrateDataBundle()


    def sceneCoordinates(self, sMousePt): #Code curtesy of ZetCode
        s_mouse_x = sMousePt.x()
        s_mouse_y = sMousePt.y()
        constraintCentre = self.boundingRect().center()
        arrow_x = constraintCentre.x()
        arrow_y = constraintCentre.y()
        sConstraintPt = self.mapToScene(arrow_x, arrow_y)
        s_arrow_x = sConstraintPt.x()
        s_arrow_y = sConstraintPt.y() 
        return (s_mouse_x, s_mouse_y, arrow_x, arrow_y, 
            s_arrow_x, s_arrow_y)
 
    def calculateAngle(self, coords):
        s_mouse_x, s_mouse_y = coords[0], coords[1] 
        s_arrow_x, s_arrow_y = coords[4], coords[5]
        a = abs(s_mouse_x - s_arrow_x)
        b = abs(s_mouse_y - s_arrow_y)
        # print "Opposite : " + str(a)
        # print "Adjacent : " + str(b)
        theta_deg = 0.0

        if a == 0 and b == 0:
            return
        elif a == 0 and s_mouse_y < s_arrow_y:
            theta_deg = 270
        elif a == 0 and s_mouse_y > s_arrow_y: 
            theta_deg = 90
        else:
            theta_rad = math.atan(b / a)
            theta_deg = math.degrees(theta_rad)
            if (s_mouse_x < s_arrow_x and \
                s_mouse_y > s_arrow_y):
                theta_deg = 180 - theta_deg
            elif (s_mouse_x < s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 180 + theta_deg   
            elif (s_mouse_x > s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 360 - theta_deg               
        # print str(theta_deg)
        return (theta_deg + 90)

    def doTransform(self, theta_deg, arrow_x, arrow_y):
        if self.getPin():
            self.getPin().setRotation(theta_deg)

    def mouseMoveEvent(self, mouseEvent):
        if self.pin == None: return QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, mouseEvent) #If there is no pin we are free to move, else we are locked to a pin

    def constrainMovement(self, mouseEvent): #Simple return since the Line Constraint operates on Item Changed
        if type(self.node) == Node or type(self.node) == SuperNode:
            return QtGui.QGraphicsItem.mouseMoveEvent(self.node, mouseEvent)

    def constrainItemChangedMovement(self, eventPos): #New rules need to be written for constraining the point across the line
        localPos = self.mapFromScene(eventPos)
        # print "EventPos = "  + str(eventPos)
        yPos = localPos.y()
        # print "localPos = "  + str(yPos)
        if yPos < -2*self.headLength: yPos = -2*self.headLength
        elif yPos > 2*self.tailLength: yPos = 2*self.tailLength
        # print "AdjustedPos = "  + str(yPos)
        # print "Value passing back : " + str(self.mapToScene(QtCore.QPointF(0,yPos)))
        return self.mapToScene(QtCore.QPointF(0,yPos))


#############################################################SKINNING ITEM##############################################################

class SkinningEllipse(QtGui.QGraphicsEllipseItem):
    """This is used to the region that nodes can be captured for skinning to a SuperNode

    An OpsCross item is used to define its shape. It can only be circular

    If a node lies within the circle then if it is selected then it can be skinned to the 
    SuperNode by using the RC context menu on the SuperNode itself.

    This Item still needs to be implemented into XML Storage and Reading.

    The skinning Value that is attributed to each node is inversely proportional to the 
    distance that the node lies away from the SuperNode Control Pin (SuperNode Origin)
    
    """ 

    name = "SkinningEllipse"

    def __init__(self):
        self.scale = 1.0
        self.width = 50
        self.alpha = 1.0
        self.ghostArea = False
        self.extension = 8
        QtGui.QGraphicsEllipseItem.__init__(self, -self.width, -self.width, 2*self.width, 2*self.width) 
        self.opX = None
        self.opRot = None
        self.pin = None
        self.pinIndex = 0
        self.node = None
        self.nodeIndex = 0
        self.crossOffset = 5
        self.setZValue(2)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False) 
        self.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent,True)      
        self.initBuild()

    def initBuild(self):
        self.opX = OpsCross(self)
        self.opX.setParentItem(self)
        self.opX.setPos(QtCore.QPointF(0,-self.width - self.crossOffset))
        self.opX.setSlider(True)
        self.opX.setSliderLimit(self.crossOffset)

        # self.opRot = OpsRotation(self)
        # self.opRot.setParentItem(self)
        # self.opRot.setPos(QtCore.QPointF(0,-self.width-self.extension - self.crossOffset))

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        ConstraintEllipseXml = xml.Element('SkinningEllipse')
        attributes = xml.SubElement(ConstraintEllipseXml,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'scale', value = str(self.getScale()))
        xml.SubElement(attributes, 'attribute', name = 'alpha', value = str(self.getAlpha()))
        xml.SubElement(attributes, 'attribute', name = 'height', value = str(self.getHeight()))
        xml.SubElement(attributes, 'attribute', name = 'width', value = str(self.getWidth()))
        xml.SubElement(attributes, 'attribute', name = 'ghostArea', value = str(self.isGhostArea()))
        xml.SubElement(attributes, 'attribute', name = 'extension', value = str(self.getExtension()))
        xml.SubElement(attributes, 'attribute', name = 'zValue', value = str(self.zValue()))
        xml.SubElement(attributes, 'attribute', name = 'visible', value = str(self.isVisible()))
        xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.pos().x())) + "," + str(self.pos().y()))
        
        #Now record the xml for the OpCross
        OpsItemsXml = xml.SubElement(ConstraintEllipseXml,'OpsItems')
        OpCXml = self.opX.store()
        OpsItemsXml.append(OpCXml)
        OpRXml = self.opRot.store()
        OpsItemsXml.append(OpRXml)
        return ConstraintEllipseXml

    def read(self, ConstraintEllipseXml):
        """A function to read in a block of XML and set all major attributes accordingly"""
        for a in ConstraintEllipseXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'scale': self.setScale(float(a.attrib['value']))
            elif a.attrib['name'] == 'alpha': self.setAlpha(float(a.attrib['value']))
            elif a.attrib['name'] == 'height': self.setHeight(float(a.attrib['value']))
            elif a.attrib['name'] == 'width': self.setWidth(float(a.attrib['value']))
            elif a.attrib['name'] == 'extension': self.setExtension(float(a.attrib['value']))
            elif a.attrib['name'] == 'zValue': self.setZValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'pos': 
                newPos = a.attrib['value'].split(",")
                self.setPos(float(newPos[0]), float(newPos[1]))

        #The Ops Cross and OpsRot are created, so hunt through the XML and make sure all their attributes are loaded in
        OpsItemsXml = ConstraintEllipseXml.findall('OpsItems')
        for itemXml in OpsItemsXml[0]: #This should only find One OpsCross
            if itemXml.tag == "OpsCross": self.opX.read(itemXml)
            if itemXml.tag == "OpsRot": self.opRot.read(itemXml)
        self.redraw(self.opX.pos())
        self.lock()

        for a in ConstraintEllipseXml.findall( 'attributes/attribute'): #Finsh by setting and ghost visibility states
            if a.attrib['name'] == 'ghostArea': self.setGhostArea(str(a.attrib['value']) == 'True')
            elif a.attrib['name'] == 'visible': self.setVisible(str(a.attrib['value']) == 'True')
        self.update()

    def getScale(self):
        return self.scale

    def setScale(self, scale):
        self.scale = scale

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getExtension(self):
        return self.extension

    def setExtension(self,extension):
        self.extension = extension

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = float(alpha)
        self.opX.setAlpha(float(alpha))

    def isGhostArea(self):
        return self.ghostArea

    def setGhostArea(self, ghost):
        self.ghostArea = bool(ghost)
        self.opX.setVisible(not bool(ghost))
        self.opRot.setVisible(not bool(ghost))

    def getPinIndex(self):
        return self.pinIndex

    def setPinIndex(self, index):
        self.pinIndex = index

    def getPin(self):
        return self.pin

    def setPin(self, pin):
        if type(pin) == ControlPin:
            self.pin = pin
            self.setPinIndex(pin.getIndex())
            self.setParentItem(pin)
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO NODE FOR PIN ALLOCATION"

    def getNodeIndex(self):
        return self.nodeIndex

    def setNodeIndex(self, index):
        self.nodeIndex = index

    def getNode(self):
        return self.node

    def setNode(self, node):
        if type(node) == Node or type(node) == SuperNode:
            self.node = node
            self.setNodeIndex(node.getIndex())
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO CONSTRAINITEM FOR CONSTRAINT ALLOCATION"

    def lock(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable,False)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False)  
        self.opX.setFlag(QtGui.QGraphicsItem.ItemIsSelectable,False) 

    def boundingRect(self):
        adjust = 2
        return QtCore.QRectF(self.scale*(-self.width - adjust), self.scale*(-self.width - adjust - self.extension-3),
                             self.scale*(2*self.width + 2*adjust), self.scale*(2*self.width + adjust + 2*self.extension + 5))

    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        gradient = QtGui.QRadialGradient(0, 0, self.scale*self.width)
        gradient.setColorAt(0, QtGui.QColor(255,0,0,25 * self.alpha))
        gradient.setColorAt(0.25, QtGui.QColor(255,125,0,25 * self.alpha))
        gradient.setColorAt(0.5, QtGui.QColor(255,255,0,25 * self.alpha))
        gradient.setColorAt(0.75, QtGui.QColor(125,255,0,25 * self.alpha))
        gradient.setColorAt(1.0, QtGui.QColor(0,255,0,25 * self.alpha))
        self.setBrush(QtGui.QBrush(gradient))
        pen = QtGui.QPen(QtGui.QColor(0,0,0,255*self.alpha), 0.25, QtCore.Qt.SolidLine)
        self.setPen(pen)
        self.setBrush(QtGui.QBrush(gradient))
        QtGui.QGraphicsEllipseItem.paint(self, painter, option, widget)

        if self.width > 3: 
            painter.drawLine(3,0,-3,0)
            painter.drawLine(0,3,0,-3)
        else: 
            painter.drawLine(self.width,0,-self.width,0)
            painter.drawLine(0,self.width,0,-self.width)

    def redraw(self, index): #index indicates which cross we are interested in - on this Line 0 is a head, and 1 is a tail
        if index == 0:
            self.setWidth(abs(self.opX.pos().y()) - self.crossOffset)
            self.setRect(self.scale*(-self.width), self.scale*(-self.width),
                             self.scale*(2*self.width), self.scale*(2*self.width)) 
            # self.opRot.setPos(QtCore.QPointF(0,-self.width - self.crossOffset - self.extension))
        self.update()

    def sceneCoordinates(self, sMousePt): #Code curtesy of ZetCode
        s_mouse_x = sMousePt.x()
        s_mouse_y = sMousePt.y()
        constraintCentre = self.boundingRect().center()
        arrow_x = constraintCentre.x()
        arrow_y = constraintCentre.y()
        sConstraintPt = self.mapToScene(arrow_x, arrow_y)
        s_arrow_x = sConstraintPt.x()
        s_arrow_y = sConstraintPt.y() 
        return (s_mouse_x, s_mouse_y, arrow_x, arrow_y, 
            s_arrow_x, s_arrow_y)
 
    def calculateAngle(self, coords):
        s_mouse_x, s_mouse_y = coords[0], coords[1] 
        s_arrow_x, s_arrow_y = coords[4], coords[5]
        a = abs(s_mouse_x - s_arrow_x)
        b = abs(s_mouse_y - s_arrow_y)
        # print "Opposite : " + str(a)
        # print "Adjacent : " + str(b)
        theta_deg = 0.0

        if a == 0 and b == 0:
            return
        elif a == 0 and s_mouse_y < s_arrow_y:
            theta_deg = 270
        elif a == 0 and s_mouse_y > s_arrow_y: 
            theta_deg = 90
        else:
            theta_rad = math.atan(b / a)
            theta_deg = math.degrees(theta_rad)
            if (s_mouse_x < s_arrow_x and \
                s_mouse_y > s_arrow_y):
                theta_deg = 180 - theta_deg
            elif (s_mouse_x < s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 180 + theta_deg   
            elif (s_mouse_x > s_arrow_x and \
                s_mouse_y < s_arrow_y):
                theta_deg = 360 - theta_deg               
        # print str(theta_deg)
        return (theta_deg + 90)

    def doTransform(self, theta_deg, arrow_x, arrow_y):
        self.setRotation(theta_deg)

    # def mouseMoveEvent(self, mouseEvent):
    #     if self.pin == None: return QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, mouseEvent) #If there is no pin we are free to move, else we are locked to a pin

    # def constrainMovement(self, mouseEvent):
    #     if self.contains(self.mapFromScene(mouseEvent.scenePos())): # make sure the incoming cordinates are map to the constraint Item for processing "contains"
    #         print "node is : " + str(self.node)
    #         return QtGui.QGraphicsItem.mouseMoveEvent(self.node, mouseEvent)



class SkinningPinInfo():
    """This is used to store the skinning information that allows a SuperNode to move the ControlPin in a WireGroup

    One instance of this class is created for each node that is skinned to a superNode. These instances are the stored
    in the "skinnedPins" attribute on the SuperNode.

    The SkinningPinInfo records the initial skinning position of the ControlPin, and then calculates the influence on 
    the position of ControlPin by the translation of the SuperNode and the associated Skinning Value
    """
    def __init__(self):
        self.superNode = None
        # self.superNodeName = None
        self.pin = None
        self.pinIndex = None
        self.wireGroup = None
        self.wireGroupName = ""

        self.pinSkinPos = None
        self.skinValue = 0

    def store(self):
        """Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
        skinningPinInfoRoot = xml.Element('SkinningPinInfo')
        attributes = xml.SubElement(skinningPinInfoRoot,'attributes')
        xml.SubElement(attributes, 'attribute', name = 'pinIndex', value = str(self.getPinIndex()))
        xml.SubElement(attributes, 'attribute', name = 'wireGroupName', value = str(self.getWireGroupName()))
        xml.SubElement(attributes, 'attribute', name = 'pinSkinPos', value = (str(self.pinSkinPos.x())) + "," + str(self.pinSkinPos.y()))
        xml.SubElement(attributes, 'attribute', name = 'skinValue', value = str(self.getSkinValue()))

        return skinningPinInfoRoot

    def read(self, nodeXml):
        """A function to read in a block of XML and set all major attributes accordingly. Has to run through all Items in the scene to find the Correct WireGroup/SuperNode/Pin"""
        for a in nodeXml.findall( 'attributes/attribute'):
            if a.attrib['name'] == 'pinIndex': self.setPinIndex(int(a.attrib['value']))
            elif a.attrib['name'] == 'wireGroupName': self.setWireGroupName(str(a.attrib['value']))
            elif a.attrib['name'] == 'skinValue': self.setSkinValue(float(a.attrib['value']))
            elif a.attrib['name'] == 'pinSkinPos': 
                newSkinPos = a.attrib['value'].split(",")
                self.setPinSkinPos(QtCore.QPointF(float(newSkinPos[0]), float(newSkinPos[1])))
 

    def getSuperNode(self):
        return self.superNode

    def setSuperNode(self, superNode):
        if type(superNode) == SuperNode:
            self.superNode = superNode
            # self.setSuperNodeName(superNode.getName())

    def getSuperNodeName(self):
        return self.superNodeName

    def setSuperNodeName(self, name):
        self.superNodeName = str(name)

    def getPin(self):
        return self.pin

    def setPin(self, pin, setSkinPos = True):
        """Function to set the pin of the skinningInfo"""
        if type(pin) == ControlPin:
            self.pin = pin
            self.setPinIndex(pin.getIndex())
            if setSkinPos: self.pinSkinPos = self.pin.pos()
        else: 
            print "WARNING : INVALID OBJECT WAS PASSED TO ITEM FOR ALLOCATION"

    def getPinIndex(self):
        return self.pinIndex

    def setPinIndex(self, index):
        self.pinIndex = int(index)

    def getWireGroup(self):
        return self.wireGroup

    def setWireGroup(self, wireGroup):
        self.wireGroup = wireGroup
        self.wireGroupName = wireGroup.getName()

    def getWireGroupName(self):
        return self.wireGroupName

    def setWireGroupName(self, wireGroupName):
        self.wireGroupName = wireGroupName

    def getPinSkinPos(self):
        return self.pinSkinPos

    def setPinSkinPos(self, pinSkinPos):
        self.pinSkinPos = pinSkinPos

    def getSkinValue(self):
        return self.skinValue

    def setSkinValue(self, value):
        val = float(value)
        if val > 1.0 : self.skinValue = 1.0
        elif val < 0.0 : self.skinValue = 0.0
        else: self.skinValue = val

    def goHome(self):
        if self.pin: 
            self.pin.setPos(self.pinSkinPos)
            if self.pin.getPinTie(): self.pin.getPinTie().drawTie() #If we are moving the pin back, update the Tie

    def update(self):
        if self.superNode and self.pin:
            newTranslation = ((self.superNode.scenePos()-self.superNode.getPin().scenePos()) * self.skinValue) + self.pinSkinPos
            self.pin.setPos(newTranslation)
