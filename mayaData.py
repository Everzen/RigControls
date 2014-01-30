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
		return controller[0]

	def isNameUnique(self, name):
		"""Function to check whether the name already exists in the Maya Scene. This is done by creating a new name, and checking to see if the name is the same as the name provided."""
		sceneName = cmds.createNode("transform", name = name)
		cmds.delete(sceneName)
		return sceneName == name
