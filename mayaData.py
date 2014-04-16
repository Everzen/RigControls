##############################################################################################
##mayaData.py - Module to collect all the Maya Specific Commands, and pass them into the data processing, so the appropriate methods are called for the 3D Application

import maya.cmds as cmds
from PySide import QtCore, QtGui

class MayaData(object):
	"""This class contains the instruction calls to test and make changes to the Maya scene
	"""
	def __init__(self):
		self.sceneController = None
		self.appName = "Maya"

	def getAppName(self):
		return self.appName

	def createSceneController(self, name):
		"""Function to create a Maya Locator to act as the scene controller"""
		controller = cmds.spaceLocator(name = name)
		cmds.setAttr(controller[0] + ".localScaleX", 5)
		cmds.setAttr(controller[0] + ".localScaleY", 5)
		cmds.setAttr(controller[0] + ".localScaleZ", 5)
		cmds.setAttr(controller[0] + ".tx", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".ty", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".tz", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".rx", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".ry", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".rz", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".sx", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".sy", channelBox=False, keyable=False)
		cmds.setAttr(controller[0] + ".sz", channelBox=False, keyable=False)
		#Add an initial attribute called "Happy Face". This is just a marker to show the start of the code added attrbiutes.
		self.addTitleAttr(controller[0], "HappyFace")
		print "My controller is : " + controller[0]
		return controller[0]

	def isNameUnique(self, name):
		"""Function to check whether the name already exists in the Maya Scene. This is done by creating a new name, and checking to see if the name is the same as the name provided.
		Can also be used to determine if the current specified sceneController still exists in the scene, or whether it has been deleted. If its name is considered unique, then it has been deleted"""
		sceneName = cmds.createNode("transform", n=str(name))
		cmds.delete(sceneName)
		return (sceneName == name)

	def rename(self, currName, newName):
		"""Function to rename a Maya sceneNode"""
		return cmds.rename(currName, newName)

	def addAttr(self, node, att, isLocked=False, atType='double'):
		"""Function to add a float attribute to the node specified. No restrictions will be applied to the node, but the default will be 0"""
		if not self.attExists(node, att):
			cmds.addAttr(node, longName=att, attributeType=atType, keyable=True)
			cmds.setAttr(node + "." + att, lock=isLocked, keyable=not(isLocked))
			return True
		else: 
			return False

	def deleteAttr(self, node, att):
		cmds.setAttr(str(node) + "." + str(att), l=False) #make sure the attribute us unlocked before trying to remove it.
		cmds.deleteAttr(str(node), at=str(att))


	def addTitleAttr(self, node, titleAttr):
		"""This function just adds a simple name attribute that is a locked off boolean to mark a key point in the Maya Node attribute list"""
		if not self.attExists(node, titleAttr):
			cmds.addAttr(node, longName=titleAttr, attributeType='bool', keyable=True)
			cmds.setAttr(node + "." + titleAttr, True)
			cmds.setAttr(node + "." + titleAttr, lock=True)
			return True
		else: 
			return False

	def objExists(self, objName):
		"""Function to determine whether a node exists in the Maya scene with the name objName"""
		if objName: 
			return cmds.objExists(objName)
		else:
			return False

	def attExists(self, node, att):
		"""Function to run through the attributes of a Node and check to see if this one exists"""
		nodeAttr = cmds.listAttr(node, keyable = True)
		for at in nodeAttr:
			if at == att:
				return True
		return False

	def listLinkAttrs(self, node):
		"""Function to list all the float connectable, keyable attributes on node"""
		return cmds.listAttr(node, scalar=True, read=True, write=True, connectable=True, keyable=True)

	def listUserAttrs(self, node):
		"""Function to list all the attributes that have been added to a node by a user"""
		return (cmds.listAttr(str(node), userDefined=True))

	def listInputConnections(self, node):
		"""Function to list all input connections skipping unitconversions"""
		return cmds.listConnections( str(node), scn=True, source=True )

	def connectAttr(self, sourceNode, sourceAttr, destNode, destAttr):
		"""Function to connect the sourcenode.att to the destNode.att"""
		cmds.connectAttr(sourceNode + "." + sourceAttr, destNode + "." + destAttr)
	
	def disconnectAttr(self, sourceNode, destNode):
		"""Function to disconnect the two nodes from eachother"""
		cmds.disconnectAttr(sphereR, coneR)

	def returnSelectedObject(self):
		"""Function to return a single Item from a selection"""
		currSel = cmds.ls(sl=True)
		if len(currSel) == 0: #There is no selection report this in messagebox
			print "WARNING: No Node was selected"
			return None
		elif len(currSel) == 1: 
			return currSel[0]
		elif len(currSel) > 1: 
			print "WARNING: Multiple Nodes were selected. Only returning the first Node in the selection list"
			return currSel[0]		

	def returnFilteredObjects(self, filterName):
		"""Function to return a list of objects from a selection that contain the substring filterName"""
		currSel = cmds.ls(sl=True)
		filterList = []
		for node in currSel:
			if filterName in node: filterList.append(node)
		return filterList

	def setAttr(self, node, attribute, data):
		"""Function to simply set an attribute"""
		cmds.setAttr((node + "." + attribute), data)

	def createNode(self, name, nodeType):
		"""Function to create a new Maya Node of the appropriate name and type"""
		return cmds.createNode(str(nodeType), n=str(name))

	def deleteNode(self, name):
		if self.objExists(name): 
			cmds.delete(name)