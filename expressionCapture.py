from PySide import QtGui, QtCore
import xml.etree.ElementTree as xml

from ControlItems import ExpressionStateNode #, ExpressionPercentageSlider

class ExpressionCaptureProcessor(object):
	"""Manages the total calculation of all recorded expressions on the Happy Face

	Takes the current referenceExpression (self.expressionReference) and compares any contributions from the ExpressionFaceStates in the
	library self.expressionLibrary
	"""
	def __init__(self):
		self.rigGraphicsView = None
		self.faceSnapShot = None #This is the state of the HappyFace to which all the expressions are compared
		self.expressionLibrary = []

	def store(self):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
		expressionCaptureProcessorRoot = xml.Element('ExpressionCaptureProcessor')

		#Store all the expressionItemsData
		faceSnapShotTitleXml = xml.SubElement(expressionCaptureProcessorRoot,'FaceSnapShot')
		if self.faceSnapShot:
			faceSnapShotXml = self.faceSnapShot.store(isFaceSnapShot = True)
			faceSnapShotTitleXml.append(faceSnapShotXml)

		#Store all the expressionFaceStaes in the self.ExpressionLibrary
		expressionFaceStateTitleXml = xml.SubElement(expressionCaptureProcessorRoot,'ExpressionLibrary')
		for expState in self.expressionLibrary:
		    expStateXml = expState.store()
		    expressionFaceStateTitleXml.append(expStateXml)

		return expressionCaptureProcessorRoot

	def read(self, expressionCaptureProcessorXml):
		"""A function to read in a block of XML and set all major attributes accordingly"""
		self.faceSnapShot = None #Clear out any snapshots and Expression Libraries
		self.expressionLibrary = []
		# Read the FaceSnapShot data and then the ExpresionLibrary Data
		faceSnapShotDataTitleXml = expressionCaptureProcessorXml.findall('FaceSnapShot')
		faceSnapShotDataXml = faceSnapShotDataTitleXml[0].findall('ExpressionFaceState')[0] #There should only be one FaceSnapShot, so take the first in the list
		newfaceSnapShot = ExpressionFaceState(self.rigGraphicsView) #Create new ExpressionFaceState, pass it the current rigGraphicsView, which must have already been set! 
		newfaceSnapShot.read(faceSnapShotDataXml, isFaceSnapShot = True)
		self.faceSnapShot = newfaceSnapShot

		self.expressionLibrary = [] # Clear Out all the expressionLibrary
		expressionLibraryXml = expressionCaptureProcessorXml.findall('ExpressionLibrary')
		for expressionStateXml in expressionLibraryXml[0].findall('ExpressionFaceState'):
			newExpressionState = ExpressionFaceState(self.rigGraphicsView) #Create new ExpressionFaceState, pass it the current rigGraphicsView, which must have already been set! 
			newExpressionState.setExpressionCaptureProcessor(self) #Make sure the ExpressionCaptureProcessor is passed to the Expression
			newExpressionState.read(expressionStateXml)
			self.expressionLibrary.append(newExpressionState)
			newExpressionStateNode = ExpressionStateNode() #Create the appropriate ExpressionState Node and Pair up the data with ExpressionFaceState
			self.rigGraphicsView.scene().addItem(newExpressionStateNode) #Add the new Item to the scene with all the data
			newExpressionState.setExpressionStateNode(newExpressionStateNode) 
			newExpressionStateNode.setExpressionFaceState(newExpressionState)
			newExpressionStateNode.setName(newExpressionState.getName())
			# newExpressionStateNode.update()
			# self.rigGraphicsView.scene().update(self.rigGraphicsView.scene().sceneRect())
			# print "About to Match Slider at : " + str(newExpressionState.sliderPos)
			newExpressionState.matchPos()
			newExpressionState.matchPercentage() #Moves the sliderPosition to the data read position and updates the expression for that new position.	
		self.processCombinedExpressions() #Now all expression are in place. Computate the entire Face	

	def getRigGraphicsView(self):
		return self.rigGraphicsView

	def setRigGraphicsView(self, rigGraphicsView):
		self.rigGraphicsView = rigGraphicsView

	def getFaceSnapShot(self):
		return self.faceSnapShot

	def setFaceSnapShot(self):
		if self.faceSnapShot: #We already have a snapshot, so update it. 
			self.faceSnapShot.recordState()
			self.faceSnapShot.clearDeltas()
		else:
			self.faceSnapShot = ExpressionFaceState(self.rigGraphicsView)
			self.faceSnapShot.recordState()
		self.resetSliders() 

	def addExpression(self, name):
		"""Function to create a new ExpressionFaceState and store it, corresponding to the appropirate ExpressionStateNode"""
		newExpression = ExpressionFaceState(self.rigGraphicsView) #Create a new ExpressionFaceState, capture the current Face and name it
		newExpression.setName(name)
		newExpression.setExpressionCaptureProcessor(self) #Inform the new expression of the ExpressionCaptureProcessor
		# newExpression.recordState()
		self.expressionLibrary.append(newExpression)
		return newExpression

	def removeExpression(self, name):
		"""Function to search through all the expressionLibrary and remove this ExpressionFaceState if it is found"""
		delExpression = None
		for exp in self.expressionLibrary:
			if exp.getName() == name: #We have found our Expression to be removed
				delExpression = exp
		if delExpression:
			self.expressionLibrary.remove(delExpression)

	def processCombinedExpressions(self):
		"""Function to run through all the ExpressionFaceStates, monitor the deltas and calcluate the accumulated delta, and slide the nodes to that position

		Current version might be a little slow, since it collects all deltas for all items, even if there are only going to be a selection moved. Look at optimising.
		"""
		if self.faceSnapShot: #Check we have a snapShot to compare things to. Otherwise there is no comparison to make
			self.mapSelected() #Run to determine whether we are processing a selection, or if we are working acros the entire face.
			self.faceSnapShot.clearDeltas() #Clear all the deltas out of the faceSnapShot
			for expression in self.expressionLibrary: #Loop through all expressions comparing them to the faceSnapShot
				if expression.getPercentage() != 0.0: #First check that there is a percentage contribution from that Expression, if not, then we ignore it!
					for snapItem in self.faceSnapShot.getExpressionItemsData():
						matchExpItem = expression.findExpressionItemMatch(snapItem)
						if matchExpItem: #If, then we have found a match
							snapItem.addDelta(matchExpItem, expression.getPercentage())
			#Now that we have calculated all the new deltas, then all we need to do is make the final move for each of the nodes
			if self.faceSnapShot.isEffectWholeFace(): #We have no selection of nodes so we will be moving the entire face
				for snapItem in self.faceSnapShot.getExpressionItemsData():
					snapItem.setDeltaPos()
			else: #A selection of nodes exists, so only adjust those nodes
				for snapItem in self.faceSnapShot.getExpressionItemsData():
					if snapItem.isSelected(): #The node is part of the selection, so adjust it
						snapItem.setDeltaPos()
		else: 
			print "No FaceSnapShot: No Action Taken"

	def isNameUnique(self, expressionName):
		"""Cycle through all expressions in the Expression Library and check that this name is unique"""
		unique = True
		for exp in self.expressionLibrary: 
			if expressionName == exp.getName(): unique = False
		return unique

	def resetSliders(self):
		"""Function to loop through all the expressions, find their ExpressionStateNode's and reset their sliders"""
		for exp in self.expressionLibrary:
			exp.getExpressionStateNode().resetSlider()

	def cleanUp(self):
		"""Function that loops through all expressions in the library and the faceSnapShot,
		deletes out any unliked ExpressionFaceStates, where their node has been deleted
		"""
		if self.faceSnapShot: #If there is a snapShot then clean it up
			self.faceSnapShot.cleanUp()

		for exp in self.expressionLibrary: #CleaupExpressions
			exp.cleanUp()

	def clearAll(self):
		"""Function to clear out all faceSnapShot and expressionLibrary data. Called in the event of a RigGV clear All"""
		self.faceSnapShot = None #This is the state of the HappyFace to which all the expressions are compared
		self.expressionLibrary = []	

	def mapSelected(self):
		"""Function to record in each of the ExpressionItemStates of the faceSnapShot, whether the node was selected or not

		This loop works but feels slow and messy"""
		effectWholeFace = True #variable to decide whetther the whole face is to be effected by the expression. If a node is found to be selected, then this will be false

		if self.faceSnapShot: #Check we have a snapShot to compare things to. Otherwise there is no comparison to make
			self.faceSnapShot.collectActiveControlNodes() #Update the activeNodes

			for node in self.faceSnapShot.getActiveNodes():
				for expItem in self.faceSnapShot.getExpressionItemsData():
					if node == expItem.getNode(): #We have found the node in question record whether it is selected
						expItem.setIsSelected(node.isSelected())
						if effectWholeFace: #Check to see if effectWholeFace has already been set to false. If it hasn't then check the node selection. If node is selected then we are dealing a partial face move, so set effectWholeFace to False
							if node.isSelected():
								effectWholeFace = False
			#After the Entire loop we decide whether we are effeecting the entire face from the selections that we have processed
			self.faceSnapShot.setEffectWholeFace(effectWholeFace)
		else: 
			print "No FaceSnapShot: No Action Taken"

	def focusExpression(self, expressionFaceState):
		"""Function to dial the supplied expression state to full, and turn all the others off (percent 0).
		This is used when a new expression has been create and is being set. It ensures the current expression that is recorded is dialled in on full, and all other expressions are dialled off
		"""
		for exp in self.expressionLibrary:
			if exp == expressionFaceState:
				exp.setPercentage(100.0)
			else:
				exp.setPercentage(0.0)
		self.processCombinedExpressions() #Now process the face as a result of the new percentage positions



class ExpressionFaceState(object):
	"""Captures all the data for the Happy Face in a set position

	Does this by looping through all ControlItems that are active and recording their positions
	"""
	def __init__(self, rigGraphicsView):
		self.rigGraphicsView = rigGraphicsView
		self.expressionCaptureProcessor = None
		self.name = "Expression" #This is the name given to the expression - Take this from the ExpressionStateNode
		self.expressionItemsData = []
		self.activeNodes = []
		self.percentage = 0.0
		self.effectWholeFace = True #Simple identifier to see if we are updating the entire face with the expression slider, or just the items that are recorded as selected.
		self.active = False

		#Attributes referring to the expressionStateNode - This is done to try and get all data storable from just this ExpressionFaceState - the ExpressionStateNode is then created from this data
		self.expressionStateNode = None #This is the rigGraphicsView ExpressionStateNode that this ExpressionFaceState is linked to.
		self.colour = QtGui.QColor(255,0,0)
		self.pos = QtCore.QPointF(0,0)
		self.sliderPos = QtCore.QPointF(0,0)

	def store(self, isFaceSnapShot = False):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
		expressionFaceStateRoot = xml.Element('ExpressionFaceState')
		attributes = xml.SubElement(expressionFaceStateRoot,'attributes')
		xml.SubElement(attributes, 'attribute', name = 'name', value = str(self.getName()))
		xml.SubElement(attributes, 'attribute', name = 'percentage', value = str(self.getPercentage()))
		if not isFaceSnapShot:
			xml.SubElement(attributes, 'attribute', name = 'colour', value = (str(self.getColour().red()) + "," + str(self.getColour().green()) + "," + str(self.getColour().blue())))
			xml.SubElement(attributes, 'attribute', name = 'pos', value = (str(self.getPos().x())) + "," + str(self.getPos().y()))
			# xml.SubElement(attributes, 'attribute', name = 'sliderPos', value = (str(self.getSliderPos().x())) + "," + str(self.getSliderPos().y()))

		#Store all the expressionItemsData
		expressionItemsDataXml = xml.SubElement(expressionFaceStateRoot,'ExpressionItemData')
		for expItem in self.expressionItemsData:
			expItemXml = expItem.store()
			expressionItemsDataXml.append(expItemXml)
		return expressionFaceStateRoot

	def read(self, expressionFaceStateXml, isFaceSnapShot = False):
		"""A function to read in a block of XML and set all major attributes accordingly"""
		for a in expressionFaceStateXml.findall( 'attributes/attribute'):
			if a.attrib['name'] == 'name': self.setName(str(a.attrib['value']))
			elif a.attrib['name'] == 'percentage': self.setPercentage(float(a.attrib['value']))
			if not isFaceSnapShot:
				if a.attrib['name'] == 'pos':
					newPos = a.attrib['value'].split(",")
					self.setPos(QtCore.QPointF(float(newPos[0]), float(newPos[1])))
				# elif a.attrib['name'] == 'sliderPos':
				# 	newSliderPos = a.attrib['value'].split(",")
				# 	self.setSliderPos(QtCore.QPointF(float(newSliderPos[0]), float(newSliderPos[1])))
				elif a.attrib['name'] == 'colour':
				    newColour = a.attrib['value'].split(",")
				    self.setColour(QtGui.QColor(float(newColour[0]), float(newColour[1]),float(newColour[2])))

		print "My read Slider Pos is: " + str(self.sliderPos)
		# Read ExpressionItemsData
		self.expressionItemsData = [] # Clear Out all the ExpressionItemData
		expressionItemsDataXml = expressionFaceStateXml.findall('ExpressionItemData')
		for expressionItemXml in expressionItemsDataXml[0].findall('ExpressionItemState'):
			newExpressionItem = ExpressionItemState(None) #Create a new ExpressionItemState, passing it None, so it cannot strip any node information. Load this in by hand using read
			newExpressionItem.read(expressionItemXml)
			self.expressionItemsData.append(newExpressionItem)
		self.matchUpNodes() #Run this to loop through all the control Nodes in the rigGV and match them up to the ExpressionItemStates

	def getName(self):
		return self.name

	def setName(self, name):
		self.name = name

	def getExpressionStateNode(self):
		return self.expressionStateNode

	def setExpressionStateNode(self, expressionStateNode):
		self.expressionStateNode = expressionStateNode

	def getPos(self):
		"""Returns the position of the linked ExpressionStateNode"""
		if self.expressionStateNode: 
			print "got ExpressNode"
			self.pos = self.expressionStateNode.pos()
			return self.pos
		return None

	def matchPos(self):
		"""Function to update ExpressionStateNode to that position, and update the Slider to the appropriate position too"""
		if self.expressionStateNode: 
			self.expressionStateNode.setPos(self.pos)
			# print "setting sliderPosition to : " + str(self.sliderPos)
			# self.expressionStateNode.getSlider().setPos(self.sliderPos)
			# self.expressionStateNode.movePercentage(self.sliderPos) #Now the position of the slider is in place, then update the expression.

	def setPos(self, pos):
		"""Function to update local pos Attribute and set the ExpressionStateNode to that position"""
		self.pos = pos

	def getSliderPos(self):
		"""Returns the position of the linked ExpressionStateNode"""
		if self.expressionStateNode: 
			self.sliderPos = self.expressionStateNode.getSlider().pos()
			return self.sliderPos
		return None

	def setSliderPos(self, sliderPos):
		self.sliderPos = sliderPos

	def isActive(self):
		return self.active

	def setActive(self, active):
		self.active = active

	def getColour(self):
		"""Returns the colour of the linked ExpressionStateNode"""
		return self.colour

	def setColour(self, colour):
		"""Function to update colour and set the ExpressionStateNode to that colour"""
		self.colour = colour

	def getExpressionItemsData(self):
		return self.expressionItemsData

	def getExpressionCaptureProcessor(self):
		return self.expressionCaptureProcessor

	def setExpressionCaptureProcessor(self, expressionCaptureProcessor):
		self.expressionCaptureProcessor = expressionCaptureProcessor

	def getActiveNodes(self):
		"""Function just to grab the current ActiveNodes"""
		return self.activeNodes

	def getPercentage(self):
		"""Function to return the percentage that the expression is dialled in on the ExpressionStateNode"""
		return self.percentage

	def setPercentage(self, percentage):
		"""Function to set the percentage, normally driven by the slider on the ExpressionStateNode"""
		self.percentage = percentage
		if self.expressionStateNode:
			self.expressionStateNode.slider.widget().setValue(percentage)

	def matchPercentage(self):
		"""This takes the current percentage value and makes sure that the slider is moved to the correct position to represent that percentage"""
		if self.expressionStateNode:
			self.expressionStateNode.matchPercentagePos(self.percentage)

	def isEffectWholeFace(self):
		return self.effectWholeFace

	def setEffectWholeFace(self, effectWholeFace):
		self.effectWholeFace = effectWholeFace

	def recordState(self):
		"""Function to loop through all the activeNodes and record each one into an ExpressionItemState"""
		self.collectActiveControlNodes() #First of all Collect all the activeNodes on the face
		self.expressionItemsData = [] #clear out our Expression Items

		for node in self.activeNodes: #Loop through all activeNodes recording in an ExpressionItem State and append to expressionItems array
			newExpressionItem = ExpressionItemState(node)
			self.expressionItemsData.append(newExpressionItem)
		self.active = True #A state has been recorded so make this expression an Active One

	def collectActiveControlNodes(self):
		"""Function loops through all wiregroups and superNodegroups in the rigGraphicsView and collects all the appropriate Nodes, and update the dataBundles list"""
		wireGroups = self.rigGraphicsView.getWireGroups()
		superNodegroups = self.rigGraphicsView.getSuperNodeGroups()

		activeNodes = []
		for wG in wireGroups: #loop through the wiregroups adding the nodes to the activeNodes list
			for pin in wG.getPins():
				if pin.isActive(): #If the pin is active then the node is visible and we need to add the node
					activeNodes.append(pin.getNode())
		for sG in superNodegroups: activeNodes.append(sG.getSuperNode()) #loop through all the superNodeGroups adding the nodes to the activeNodes list

		self.activeNodes = activeNodes
		return activeNodes

	def cleanUp(self):
		"""Function to loop through all ExpressionItemStates to check that all the corresponding nodes still exist in the happy face, if not then remove them"""
		self.collectActiveControlNodes() #Create Up to date record of nodes

		newExpressionItemsData = []

		for exp in self.expressionItemsData:
			if self.nodeExists(exp): #found the node, so keep this ExpressionItemState
				newExpressionItemsData.append(exp)

		self.expressionItemsData = newExpressionItemsData #set the new list to be our self.expressionItemsData


	def nodeExists(self, expressionItem):
		"""Function check whether the control Item still exists in the Happy Face using the information on the ExpressionItemState"""
		# self.collectActiveControlNodes() #Update our Node list
		for node in self.activeNodes:
			if node.getIndex() == expressionItem.getIndex(): #Check to see if the both the index and group match up. If they do then the node exists
				if node.getGroupName() == expressionItem.getGroupName():
					print "Found a Node match"
					return True
		return False

	def matchUpNodes(self):
		"""Function for use after read(). It matches up all the nodes in the current rigGraphicsView, to the ExpressionItemStates by checking the index and groupName"""
		self.collectActiveControlNodes()
		
		for node in self.activeNodes:
			for expItem in self.expressionItemsData:
				if node.getIndex() == expItem.getIndex(): #Check to see if the both the index and group match up. If they do then the node is assigned to the ExpressionItemState
					if node.getGroupName() == expItem.getGroupName():
						expItem.setNode(node, recordState = False) #Assign the node, but without recording the details, since they are already loaded in. 

	def clearDeltas(self):
		"""Function to loop through all of the ExpressionItemStates and reset their Deltas"""
		for expItem in self.expressionItemsData:
			expItem.clearDelta()

	def findExpressionItemMatch(self, sampleExpItem):
		"""Function to loop through ExpressionItems and return the one matching the sample Item
		Used for comparing faceSnapShot ExpressionItems to expressionLibrary ExpressionItems
		"""
		for expItem in self.expressionItemsData:
			if sampleExpItem.getGroupName() == expItem.getGroupName(): #If both match then return that Item! 
				if sampleExpItem.getIndex() == expItem.getIndex():
					return expItem
		return None #If there are no matches then return None
	
	def processCombinedExpressions(self):
		"""Function to simply call the same method in the ExpressionCaptureProcessor"""
		self.expressionCaptureProcessor.processCombinedExpressions()

	def setFaceSnapShot(self):
		"""Function to set a faceSnap shot in the ExpressionCaptureProcessor"""
		self.expressionCaptureProcessor.setFaceSnapShot()

	def mapSelected(self):
		"""Function to set a faceSnap shot in the ExpressionCaptureProcessor"""
		self.expressionCaptureProcessor.mapSelected()


class ExpressionItemState(object):
	"""Captures the key data for any Node/SuperNode that has its information collected

	Records all key data such as position, index and groupName, so each each control Item can be identified easily
	"""
	def __init__(self, node):
		self.node = node
		self.index = None
		self.group = None
		self.groupName = None
		self.selected = False
		self.refPos = None
		self.recordState() #Function to record all key information for the Expression State from the Node/SuperNode
		self.delta = (QtCore.QPointF(0,0)) #This is used by the ExpressionCaptureProcessor.faceSnapShot to calculate the position of the Node

	def store(self):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load"""
		expressionItemStateRoot = xml.Element('ExpressionItemState')
		attributes = xml.SubElement(expressionItemStateRoot,'attributes')
		xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
		xml.SubElement(attributes, 'attribute', name = 'groupName', value = str(self.getGroupName()))
		xml.SubElement(attributes, 'attribute', name = 'selected', value = str(self.isSelected()))
		xml.SubElement(attributes, 'attribute', name = 'refPos', value = (str(self.getRefPos().x())) + "," + str(self.getRefPos().y()))
		xml.SubElement(attributes, 'attribute', name = 'delta', value = (str(self.getDelta().x())) + "," + str(self.getDelta().y()))
		return expressionItemStateRoot

	def read(self, expressionItemStateXml):
		"""A function to read in a block of XML and set all major attributes accordingly"""
		# GuideMarkerRoot = expressionItemStateXml.getroot()
		for a in expressionItemStateXml.findall( 'attributes/attribute'):
			if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
			elif a.attrib['name'] == 'groupName': self.setGroupName(str(a.attrib['value']))
			elif a.attrib['name'] == 'selected': self.setIsSelected(str(a.attrib['value']) == 'True')
			elif a.attrib['name'] == 'refPos':
				newPos = a.attrib['value'].split(",")
				self.setRefPos(QtCore.QPointF(float(newPos[0]), float(newPos[1])))
			elif a.attrib['name'] == 'delta':
				delta = a.attrib['value'].split(",")
				self.setDelta(QtCore.QPointF(float(delta[0]), float(delta[1])))

	def getNode(self):
		return self.node

	def setNode(self, node, recordState = True):
		self.node = node
		if recordState: 
			self.recordState() #Update the index,group etc for the new Node

	def getIndex(self):
		return self.index

	def setIndex(self, index):
		"""Function to grab the index from the node"""
		self.index = index

	def setIndexByNode(self, node):
		"""Function to grab the index from the node"""
		self.index = node.getIndex()

	def getGroup(self):
		return self.group

	def setGroup(self, node):
		"""Function to grab the group and groupName from the node"""
		self.group = node.getGroup()
		self.groupName = node.getGroupName()

	def getGroupName(self):
		"""Function to return the name of the group of the node"""
		return self.groupName

	def setGroupName(self, groupName):
		self.groupName = groupName

	def getRefPos(self):
		return self.refPos

	def setRefPos(self, refPos):
		self.refPos = refPos

	def matchRefPos(self, node):
		"""Function to match self.refPos to the position of the node"""
		self.refPos = node.pos()

	def recordState(self):
		"""Function to loop through and grab all the critical information from the Node"""
		if self.node:
			self.setIndexByNode(self.node)
			self.setGroup(self.node)
			self.matchRefPos(self.node)

	def getDelta(self):
		return self.delta

	def setDelta(self, delta):
		self.delta = delta

	def addDelta(self, expressionItem, percentage):
		"""Function to calculate and then add the delta to the current delta, to accumulate the total move for the expressionItem
		Takes a matching ExpressionItem and a percentage that is meant to be moved towards that emotion
		"""
		deltaContribution = percentage*(expressionItem.getRefPos() - self.getRefPos())/100.0
		self.delta += deltaContribution

	def clearDelta(self):
		"""Function to reset Delta back to 0,0"""
		self.delta = (QtCore.QPointF(0,0))

	def setDeltaPos(self):
		"""Function to physically move the control Node to the delta Position"""
		self.node.setPos(self.refPos + self.delta)

	def isSelected(self):
		return self.selected

	def setIsSelected(self, selected):
		"""Function to store whether the node was selected"""
		self.selected = selected