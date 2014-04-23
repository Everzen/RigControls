

class ExpressionCaptureProcessor(object):
  """Manages the total calculation of all recorded expressions on the Happy Face

  Takes the current referenceExpression (self.expressionReference) and compares any contributions from the ExpressionFaceStates in the
  library self.expressionLibrary
  """
  def __init__(self):
  	self.rigGraphicsView = None
  	self.faceSnapShot = None #This is the state of the HappyFace to which all the expressions are compared
  	self.expressionLibrary = []

  def getRigGraphicsView(self):
  	return self.rigGraphicsView

  def setRigGraphicsView(self, rigGraphicsView):
  	self.rigGraphicsView = rigGraphicsView

  def getFaceSnapShot(self):
  	return self.faceSnapShot

  def setFaceSnapShot(self):
  	if self.faceSnapShot: #We already have a snapshot, so update it. 
  		self.faceSnapShot.recordState()
  	else:
  		self.faceSnapShot = ExpressionFaceState(self.rigGraphicsView)
  		self.faceSnapShot.recordState()
  	#Also needs to reset all ExpressionStateNode Sliders to ensure that all expressions are initially dialled off

  def addExpression(self, name):
  	"""Function to create a new ExpressionFaceState and store it, corresponding to the appropirate ExpressionStateNode"""
  	newExpression = ExpressionFaceState(self.rigGraphicsView) #Create a new ExpressionFaceState, capture the current Face and name it
  	newExpression.setName(name)
  	newExpression.recordState()
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

  def isNameUnique(self, expressionName):
  	"""Cycle through all expressions in the Expression Library and check that this name is unique"""
	unique = True
	for exp in self.expressionLibrary: 
		if expressionName == exp.getName(): unique = False
	return unique

class ExpressionFaceState(object):
	"""Captures all the data for the Happy Face in a set position

	Does this by looping through all ControlItems that are active and recording their positions
	"""
	def __init__(self, rigGraphicsView):
		self.rigGraphicsView = rigGraphicsView
		self.name = "Expression" #This is the name given to the expression - Take this from the ExpressionStateNode
		self.expressionItemsData = []
		self.activeNodes = []
		self.expressionStateNode = None #This is the rigGraphicsView ExpressionStateNode that this ExpressionFaceState is linked to.
		self.percentage = 0.0
		self.init()

	def init(self):
		"""As soon as the Face State is built then record the position of the current face"""
		self.recordState()

	def getName(self):
		return self.name

	def setName(self, name):
		self.name = name

	def getExpressionStateNode(self):
		return self.expressionStateNode

	def setExpressionStateNode(self, expressionStateNode):
		self.expressionStateNode = expressionStateNode

	def getPercentage(self):
		"""Function to return the percentage that the expression is dialled in on the ExpressionStateNode"""
		return self.percentage

	def setPercentage(self, percentage):
		"""Function to set the percentage, normally driven by the slider on the ExpressionStateNode"""
		self.percentage = percentage

	def recordState(self):
		"""Function to loop through all the activeNodes and record each one into an ExpressionItemState"""
		self.collectActiveControlNodes() #First of all Collect all the activeNodes on the face
		self.expressionItemsData = [] #clear out our Expression Items

		for node in self.activeNodes: #Loop through all activeNodes recording in an ExpressionItem State and append to expressionItems array
			newExpressionItem = ExpressionItemState(node)
			self.expressionItemsData.append(newExpressionItem)

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


class ExpressionItemState(object):
	"""Captures the key data for any Node/SuperNode that has its information collected

	Records all key data such as position, index and groupName, so each each control Item can be identified easily
	"""
	def __init__(self, node):
		self.node = node
		self.index = None
		self.group = None
		self.groupName = None
		self.refPos = None
		self.recordState() #Function to record all key information for the Expression State from the Node/SuperNode

	def getIndex(self):
		return self.index

	def setIndex(self, node):
		"""Function to grab the index from the node"""
		self.index = node.getIndex()

	def getGroup(self):
		return self.group

	def setGroup(self, node):
		"""Function to grab the group and groupName from the node"""
		self.group = node.getGroup()
		self.groupName = node.getGroupName()

	def getGroupName(self,index):
		"""Function to return the name of the group of the node"""
		return self.groupName

	def getRefPos(self):
		return self.refPos

	def setRefPos(self, node):
		self.refPos = node.pos()

	def recordState(self):
		"""Function to loop through and grab all the critical information from the Node"""
		if self.node:
			self.setIndex(self.node)
			self.setGroup(self.node)
			self.setRefPos(self.node)
