##############################################################################################
##mayaData.py - Module to collect all the Maya Specific Commands, and pass them into the data processing, so the appropriate methods are called for the 3D Application

import maya.cmds as cmds


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
		print "My controller is : " + controller[0]
		return controller[0]

	def isNameUnique(self, name):
		"""Function to check whether the name already exists in the Maya Scene. This is done by creating a new name, and checking to see if the name is the same as the name provided.
		Can also be used to determine if the current specified sceneController still exists in the scene, or whether it has been deleted. If its name is considered unique, then it has been deleted! 
		"""
		sceneName = cmds.createNode("transform", name = name)
		cmds.delete(sceneName)
		return sceneName == name

	def addAttr(self, node, att):
		"""Function to add a float attribute to the node specified. No restrictions will be applied to the node, but the default will be 0"""
		if not self.attExists(node, att):
			cmds.addAttr(node, longName=att, attributeType='double', keyable=True)
			return True
		else: 
			return False

	def attExists(self, node, att):
		"""Function to run through the attributes of a Node and check to see if this one exists"""
		nodeAttr = cmds.listAttr(node, keyable = True)
		for at in nodeAttr:
			if at == att:
				return True
		return False