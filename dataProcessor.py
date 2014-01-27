##############################################################################################
##dataProcessor - Module to grab positions of the RigGraphicsView Nodes and SuperNodes
##			      and return their positions as useful float data that can be wired into 
##				  Maya scene Control Nodes (Control Curver or Locator) to drive rig movement.
import copy


class DataProcessor(object):
	"""This class contains a number of data bundles and performs operations on them to pass out the Node and SuperNode data
	as useful float data for the x and y axis
	"""
	def __init__(self, sampleBundle):
		#LIST OF ATTRIBUTES
		self.mayaControl = None
		self.sampleBundle = sampleBundle
		self.dataBundles = []


	def getMayaControl(self):
		return self.mayaControl

	def setMayaControl(self, mayaControl):
		"""Function to take a node selected in the Maya Scene and assign it to the class"""
		self.MayaControl = mayaControl

	def attachBundle(self, item):
		"""Takes a DataBundle and adds it to the list, assigning the Maya control along the way"""
		newBundle = copy.deepcopy(self.sampleBundle)
		newBundle.setMayaControl(self.mayaControl)
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



class DataBundle(object):
	"""This class looks at the node or the SuperNode and the associated constraints on that node and 
	from the x and y postions returns some nice float data for us to wire into Maya scene Nodes etc

	mayaControl - The master scene Node that we are using in Maya to load all the float data into
	mayaAttribute - The attribute on the mayaControl that refers to this dataBundle
	node - is the Node or the SuperNode whose data we are trying to convert out data for

	"""
	def __init__(self):
		#LIST OF ATTRIBUTES
		self.mayaControl = None
		self.mayaAttribute = None
		self.node = None
		self.active = True
		self.x = 0
		self.y = 0
		self.maxX = None
		self.maxY = None
		self.minX = None 
		self.minY = None
		self.standardScale = 50.0

	def getMayaControl(self):
		return self.mayaControl

	def setMayaControl(self, mayaControl):
		"""Function to take a node selected in the Maya Scene and assign it to the class"""
		self.MayaControl = mayaControl

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
