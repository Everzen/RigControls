##############################################################################################
##dataProcessor - Module to grab positions of the RigGraphicsView Nodes and SuperNodes
##			      and return their positions as useful float data that can be wired into 
##				  Maya scene Control Nodes (Control Curver or Locator) to drive rig movement.



class DataProcessor(object):
	"""This class contains a number of data bundles and performs operations on them to pass out the Node and SuperNode data
	as useful float data for the x and y axis
	"""
	def __init__(self):
		#LIST OF ATTRIBUTES
		self.mayaControl = None
		self.dataBundles = []

	def getMayaControl(self):
		return self.mayaControl

	def setMayaControl(self, mayaControl):
		"""Function to take a node selected in the Maya Scene and assign it to the class"""
		self.MayaControl = mayaControl

	def addBundle(self, bundle):
		"""Takes a DataBundle and adds it to the list, assigning the Maya control along the way"""
		if type(bundle) == dataBundle:
			self.dataBundles.append(bundle)
			bundle.setMayaControl(self.mayaControl)

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
		self.standardScale= 50.0

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
		if posX > self.maxX:
			posX = self.maxX
		elif posX < self.minX:
			posX = self.minX
		#Now calculate the proportion from -1 -> 0 -> 1 that we should be returning
		if posX > 0:
			self.x = float(posX)/float(self.maxX)
		else:
			self.x = -float(posX)/float(self.minX)

	def setY(self, y):
		posY = y
		if posY > self.maxY:
			posY = self.maxY
		elif posY < self.minY:
			posY = self.minY
		#Now calculate the proportion from -1 -> 0 -> 1 that we should be returning
		if posY > 0:
			self.y = float(posY)/float(self.maxY)
		else:
			self.y = -float(posY)/float(self.minY)

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