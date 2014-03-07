##############################################################################################
##dataProcessor - Module to grab positions of the RigGraphicsView Nodes and SuperNodes
##			      and return their positions as useful float data that can be wired into 
##				  Maya scene Control Nodes (Control Curver or Locator) to drive rig movement.
import copy
# from mayaData import MayaData as SceneData #Importing Maya Data information. This module can be changed if decelopment occurs for other 3D applications


class DataProcessor(object):
	"""This class contains a number of data bundles and performs operations on them to pass out the Node and SuperNode data
	as useful float data for the x and y axis
	"""
	def __init__(self, sampleBundle, sceneAppData):
		#LIST OF ATTRIBUTES
		self.appName = sceneAppData.getAppName()
		self.sceneAppData = sceneAppData
		self.sceneControl = None
		self.sampleBundle = sampleBundle
		self.dataBundles = []
		self.rigGraphicsView = None

	def createSceneControl(self, name):
		"""Function to create the scene controller for the appropriate 3DApp. 
		The function should cycle through all the controls in the Happy Face and add the appropriate attributes to the scene Controller
		Wiring them into the associated data bundles"""
		self.sceneControl = self.sceneAppData.createSceneController(name)
		self.collectActiveControlNodes()

	def collectActiveControlNodes(self):
		"""Function loops through all wiregroups and superNodegroups in the rigGraphicsView and collects all the appropriateNodes"""
		wireGroups = self.rigGraphicsView.getWireGroups()
		superNodegroups = self.rigGraphicsView.getSuperNodeGroups()

		activeNodes = []
		for wG in wireGroups: activeNodes += wG.getNodes() #loop through the wiregroups adding the nodes to the activeNodes list
		for sG in superNodegroups: activeNodes.append(sG.getSuperNode()) #loop through all the superNodeGroups adding the nodes to the activeNodes list
		print "My active Node Count : " + str(len(activeNodes)) + " " + str(activeNodes)
		for n in activeNodes : print str(n.getDataBundle().getHostName())
		return activeNodes

	def addSceneControlAttributes(self):
		"""Function loops through the rigGraphicsView and picks out all the wiregroups and superNodegroups and makes attributes for them"""
		pass

	def updatedDataBundles(self):
		"""Function loops through controls in rigGraphicsView and checks them for consistency against the current dataBundle list"""
		newSampleBundles = []
		pass

	def getSceneControl(self):
		return self.sceneControl

	def setSceneControl(self, sceneControl):
		"""Function to take a node selected in the Scene and assign it to the class"""
		self.sceneControl = sceneControl

	def attachBundle(self, item):
		"""Takes a DataBundle and adds it to the list, assigning the Maya control along the way"""
		newBundle = copy.deepcopy(self.sampleBundle)
		newBundle.setSceneControl(self.sceneControl)
		item.setDataBundle(newBundle)
		self.dataBundles.append(newBundle)

	def removeBundle(self, bundle):
		if type(bundle) == dataBundle:
			for b in self.dataBundles: 
				if bundle == b:
					#If the bundle is removed then we need to check for the attribute on the mayaControl and remove that too! 
					self.dataBundles.remove(bundle)
					return True
		return False

	def isControllerActive(self):
		"""Function to check that the Controller is Active"""
		#Basic Check - Expand to include checking whether the Node has been deleted from the scene
		if self.sceneControl: return True
		else: return false

	def getAppName(self):
		"""Returns the 3D application Name which is specified upon creation of the DataProcessor"""
		return self.appName

	def isSceneControllerNameUnique(self, name):
		return self.sceneAppData.isNameUnique(name)

	def sceneControllerExists(self):
		return not self.sceneAppData.isNameUnique(self.sceneControl)

	def getRigGraphicsView(self):
		return self.rigGraphicsView

	def setRigGraphicsView(self, rigGraphicsView):
		"""Function to pass the main rigGraphicsView to the dataprocessor, so we can always keep track of exactly which controls are drawn and active"""
		self.rigGraphicsView = rigGraphicsView



class DataBundle(object):
	"""This class looks at the node or the SuperNode and the associated constraints on that node and 
	from the x and y postions returns some nice float data for us to wire into Maya scene Nodes etc

	SceneControl - The master scene Node that we are using in Maya to load all the float data into
	SceneAttribute - The attribute on the Scene Control that refers to this dataBundle
	node - is the Node or the SuperNode whose data we are trying to convert out data for

	"""
	def __init__(self):
		#LIST OF ATTRIBUTES
		self.sceneControl = None
		self.controlAttribute = None
		self.connectedNode = None
		self.attrName = None
		self.hostName = None #This is the name of the wiregroup or superNodegroup that the associated node belongs to - Do we just pass a reference to the Node itself?
		self.active = True
		self.x = 0
		self.y = 0
		self.maxX = None
		self.maxY = None
		self.minX = None 
		self.minY = None
		self.standardScale = 50.0

	def getSceneControl(self):
		return self.sceneControl

	def setSceneControl(self, sceneControl):
		"""Function to take a node selected in the Scene and assign it to the class"""
		self.sceneControl = sceneControl

	def getX(self):
		return self.x

	def getY(self):
		return self.y

	def setX(self, x):
		posX = x
		if self.maxX:
			if posX > self.maxX:
				posX = self.maxX
		if self.minX:
			if posX < self.minX:
				posX = self.minX

		#Now calculate the proportion from -1 -> 0 -> 1 that we should be returning
		if posX > 0:
			if self.maxX:
				self.x = round(float(posX)/float(self.maxX),3)
			else: 
				self.x = round(float(posX)/self.standardScale,3)
		else:
			if self.minX:
				self.x = -round(float(posX)/float(self.minX),3)
			else: 
				self.x = round(float(posX)/self.standardScale,3)

	def setY(self, y):
		posY = y
		if self.maxY:
			if posY > self.maxY:
				posY = self.maxY
		if self.minY:
			if posY < self.minY:
				posY = self.minY
		#Now calculate the proportion from -1 -> 0 -> 1 that we should be returning
		if posY > 0:
			if self.maxY:
				self.y = -round(float(posY)/float(self.maxY),3)
			else: 
				self.y = -round(float(posY)/self.standardScale,3)
		else:
			if self.minY:
				self.y = round(float(posY)/float(self.minY),3)
			else: 
				self.y = -round(float(posY)/self.standardScale,3)

	def getMaxX(self):
		return self.maxX

	def getminX(self):
		return self.minX

	def getMaxY(self):
		return self.maxY

	def getminY(self):
		return self.minY

	def setMaxX(self, maxX):
		self.maxX = float(maxX)

	def setMinX(self, minX):
		self.minX = float(minX)

	def setMaxY(self, maxY):
		self.maxY = float(maxY)

	def setMinY(self, minY):
		self.minY = float(minY)

	def isActive(self):
		return self.active

	def setActive(self, active):
		self.active = bool(active)
		if active:
			pass #Make sure that the Maya attribute is unlocked and shown in the scene
		else:
			pass #Make sure that the Maya attribute is locked and hidden in the scene, animation is deleted and the node is return to rest position

	def getAttrName(self):
		return self.attrName

	def setAttrName(self, name):
		self.attrName = str(name)

	def getHostName(self):
		return self.hostName

	def setHostName(self, hostName):
		"""Function to set the hostName which is the name of the wiregroup or superNodegroup that the associated node belongs to"""
		self.hostName = str(hostName)



class DataServoBundle(DataBundle):
	"""This class inherits DataBundle, and bolts on to it some functionality for applying servo numbers and angle limits to those servos

	"""
	def __init__(self):
		DataBundle.__init__(self) 
		self.xServoNo = None
		self.yServoNo = None
		self.minXServoAngle = 0
		self.maxXServoAngle = 180
		self.minYServoAngle = 0
		self.maxYServoAngle = 180

	def getMinXServoAngle(self):
		return self.minXServoAngle

	def getMaxXServoAngle(self):
		return self.maxXServoAngle

	def setMinXServoAngle(self, angle):
		self.minXServoAngle = angle

	def setMaxXServoAngle(self, angle):
		self.maxXServoAngle = angle

	def getMinYServoAngle(self):
		return self.minYServoAngle

	def getMaxYServoAngle(self):
		return self.maxYServoAngle

	def setMinYServoAngle(self, angle):
		self.minXServoAngle = angle

	def setMaxYServoAngle(self, angle):
		self.maxXServoAngle = angle
