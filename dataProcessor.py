##############################################################################################
##dataProcessor - Module to grab positions of the RigGraphicsView Nodes and SuperNodes
##			      and return their positions as useful float data that can be wired into 
##				  Maya scene Control Nodes (Control Curver or Locator) to drive rig movement.
import copy
import xml.etree.ElementTree as xml

from Utilities import readAttribute
# from mayaData import MayaData as SceneData #Importing Maya Data information. This module can be changed if decelopment occurs for other 3D applications


class DataProcessor(object):
	"""This class contains a number of data bundles and performs operations on them to pass out the Node and SuperNode data
	as useful float data for the x and y axis
	"""
	def __init__(self, sceneAppData):
		#LIST OF ATTRIBUTES
		self.appName = sceneAppData.getAppName()
		self.sceneAppData = sceneAppData
		self.sceneControl = None
		self.sampleBundle = DataBundle(self.sceneAppData)
		self.dataBundles = []
		self.activeAttributeConnectors = []
		self.rigGraphicsView = None

	def createSceneControl(self, name):
		"""Function to create the scene controller for the appropriate 3DApp. 
		The function should cycle through all the controls in the Happy Face and add the appropriate attributes to the scene Controller
		Wiring them into the associated data bundles"""
		self.sceneControl = self.sceneAppData.createSceneController(name)
		self.collectActiveControlNodes()

	def collectActiveControlNodes(self):
		"""Function loops through all wiregroups and superNodegroups in the rigGraphicsView and collects all the appropriate Nodes, and update the dataBundles list"""
		wireGroups = self.rigGraphicsView.getWireGroups()
		superNodegroups = self.rigGraphicsView.getSuperNodeGroups()

		activeNodes = []
		for wG in wireGroups: activeNodes += wG.getNodes() #loop through the wiregroups adding the nodes to the activeNodes list
		for sG in superNodegroups: activeNodes.append(sG.getSuperNode()) #loop through all the superNodeGroups adding the nodes to the activeNodes list
		# print "My active Node Count : " + str(len(activeNodes)) + " " + str(activeNodes)
		# for n in activeNodes : print str(n.getDataBundle().getHostName())
		#Now use this list to define the relevant dataBundles
		self.dataBundles = []
		for n in activeNodes: self.dataBundles.append(n.getDataBundle())
		return activeNodes

	def collectActiveAttributeConnectors(self):
		"""A function to run through all of the dataBundles and collect from them all the active AttributeConnectors into an array that can be used to fill the SceneLinkTabW"""
		activeNodes = self.collectActiveControlNodes()
		activeAttributeConnectors = [] 

		for node in activeNodes:
			for att in node.getDataBundle().getAttributeConnectors():
				if att.isActive(): #check if the attributeConnector is active, or whether it has been deativated by the pin/node being deativated 
					activeAttributeConnectors.append(att)
		self.activeAttributeConnectors = list(set(activeAttributeConnectors)) #By converting to a set and the back to a list, we remove duplicates caused by merged Nodes
		self.activeAttributeConnectors.sort(key=lambda att: att.getControllerAttrName()) #Sort the list by the controller attribute Names
		return self.activeAttributeConnectors

	def getActiveAttributeConnectors(self):
		"""Function to return the current list of attributeConnectors as processed by collectActiveAttributeConnectors"""
		return self.activeAttributeConnectors

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

	def returnSelectedObject(self):
		return self.sceneAppData.returnSelectedObject()

	def returnFilteredObjects(self, filterName):
		return self.sceneAppData.returnFilteredObjects(filterName)

	def checkAttributeConnectors(self):
		"""Function to run through all AttributeConnectors and check that the scene Nodes that they are connected to exist"""
		pass

	def objExists(self, objName):
		"""Function to determine whether a node exists in the Maya scene with the name objName"""
		return self.sceneAppData.objExists(objName)

	def listLinkAttrs(self, node):
		"""Function to list all the float connectable, keyable attributes on node"""
		return self.sceneAppData.listLinkAttrs(node)

	def checkSceneNodeLinks(self, attributeConnector):
		"""Function to check that no other attributeConnector has the same node and scene setup. If so, then set attribute to none"""
		for att in self.activeAttributeConnectors:
			if att != attributeConnector:
				if att.getSceneNode() == attributeConnector.getSceneNode(): #we have a matching node, so check to see if there is a matching attribute
					if att.getSceneNodeAttr() == attributeConnector.getSceneNodeAttr(): #We have a matching connection so set the attribute to None
						att.setSceneNodeAttr(None)



class DataServoProcessor(DataProcessor):
	"""This class inherits DataProcessor, and bolts on to it some functionality for processing servos

	"""
	def __init__(self, sceneAppData):
		DataProcessor.__init__(self, sceneAppData) 
		self.sampleBundle = DataServoBundle(sceneAppData) #Load in  the new DataServoBundle to access extra Servo functionality

	def checkUniqueServoChannels(self, attributeConnector, channel):
		"""A function to cycle through all the attributeConnectors and check that no other attributeConnector has the same servoChannel as the input attributeConnector"""
		for att in self.activeAttributeConnectors:
			if att != attributeConnector:
				if att.getServoChannel() == channel: att.setServoChannel(None)

	def setupServoMinMaxAngles(self):
		"""Function to run through all active attributeConnectors and make sure their servo min and max angles are initiated correctly"""
		for att in self.activeAttributeConnectors: att.setupServoMinMaxAngles()


class DataBundle(object):
	"""This class looks at the node or the SuperNode and the associated constraints on that node and 
	from the x and y postions returns some nice float data for us to wire into Maya scene Nodes etc

	SceneControl - The master scene Node that we are using in Maya to load all the float data into


	"""
	def __init__(self, sceneAppData):
		#LIST OF ATTRIBUTES
		self.sceneControl = None
		self.hostName = None
		self.node = None
		self.controllerAttrName = None #The name that the UI Node directional attribute will be associated with
		self.attributeConnectorX = AttributeConnector()
		self.attributeConnectorY = AttributeConnector()
		self.attributeConnectors = [self.attributeConnectorX, self.attributeConnectorY]
		self.sceneAppData = sceneAppData

	def store(self):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load

		Need to record key data, but some data will be supplied by position in the total save XML tree. For example self.node can be set when attribute Connector
		loaded into the appropriate Node. 
		"""
		dataBundleRoot = xml.Element('DataBundle')
		attributes = xml.SubElement(dataBundleRoot,'attributes')
		xml.SubElement(attributes, 'attribute', name = 'controllerAttrName', value = str(self.getControllerAttrName()))
		xml.SubElement(attributes, 'attribute', name = 'hostName', value = str(self.getHostName()))

		#Now we need to store the AttributeConnectors associated with the DataBundle
		attributeConnectorXXml = xml.SubElement(dataBundleRoot,'attributeConnectorX')
		attrConnectXXml = self.attributeConnectorX.store()
		attributeConnectorXXml.append(attrConnectXXml) 

		attributeConnectorYXml = xml.SubElement(dataBundleRoot,'attributeConnectorY')
		attrConnectYXml = self.attributeConnectorY.store()
		attributeConnectorYXml.append(attrConnectYXml)

		return dataBundleRoot

	def read(self, dataBundleXml):
		"""A function to read in a block of XML and set all major attributes accordingly

		node is not supplied here, but it should be set for the DataBundle in the node.read() and should also be passed down to the appropirate AttributeConnectors 
		"""
		for a in dataBundleXml.findall( 'attributes/attribute'):
			if a.attrib['name'] == 'controllerAttrName': self.setControllerAttrName(str(a.attrib['value']))
			elif a.attrib['name'] == 'hostName': self.setHostName(str(a.attrib['value']))

		#Implement the reading and attachment of the attritbute connectors
		attributeConnectorXXml = dataBundleXml.findall('attributeConnectorX')
		attConX = None
		for atConXXML in attributeConnectorXXml[0]:
			attConX = AttributeServoConnector() #Create new X attributeConnector 
			attConX.read(atConXXML) #read in the data
			self.setAttributeConnectorX(attConX)

		attributeConnectorYXml = dataBundleXml.findall('attributeConnectorY')
		attConY = None
		for atConYXml in attributeConnectorYXml[0]:
			attConY = AttributeServoConnector() #Create new X attributeConnector 
			attConY.read(atConYXml) #read in the data
			self.setAttributeConnectorY(attConY)

	def getSceneControl(self):
		return self.sceneControl

	def setSceneControl(self, sceneControl):
		"""Function to take a node selected in the Scene and assign it to the class"""
		self.sceneControl = sceneControl #cycle through all attribute connectors and update sceneControl
		for att in self.attributeConnectors: att.setSceneControl(sceneControl) 

	def getAttributeConnectorX(self):
		return self.attributeConnectorX

	def setAttributeConnectorX(self, attributeConnectorX):
		self.attributeConnectorX = attributeConnectorX
		self.attributeConnectors[0] = self.attributeConnectorX

	def getAttributeConnectorY(self):
		return self.attributeConnectorY

	def setAttributeConnectorY(self, attributeConnectorY):
		self.attributeConnectorY = attributeConnectorY
		self.attributeConnectors[1] = self.attributeConnectorY

	def getAttributeConnectors(self):
		return self.attributeConnectors

	def getHostName(self):
		return self.hostName

	def setHostName(self, hostName):
		"""Function to set the hostName  which is the name of the wiregroup or superNodegroup that the associated node belongs to"""
		self.hostName = str(hostName) #cycle through all attribute connectors and update hostName
		for att in self.attributeConnectors: att.setHostName(str(hostName))

	def getControllerAttrName(self):
		return self.controllerAttrName

	def setControllerAttrName(self, name):
		"""Function to set the standard attribute name, based on the Happy Face Node, we can then add X or Y to define the attributeConnectors"""
		self.controllerAttrName = str(name)
		#Now set the standard X and Y channels for the Data Bundle
		self.attributeConnectorX.setControllerAttrName(name + "X")
		self.attributeConnectorY.setControllerAttrName(name + "Y")

	def getNode(self):
		return self.node

	def setNode(self, node):
		"""Function to set the Node in the dataBundle, but also to pass the node down to the attributeConnectors"""
		self.node = node
		self.attributeConnectorX.setNode(node)
		self.attributeConnectorY.setNode(node)

	def getX(self):
		return self.attributeConnectorX.getValue()

	def getY(self):
		return -self.attributeConnectorY.getValue() #Flip the value to produce a positive 

	def setX(self, x):
		"""Function reaches down into the attributeConnectorX to set the X value"""
		self.attributeConnectorX.setValue(x)
		attValue = self.attributeConnectorX.getValue()
		if self.attributeConnectorX.isSceneNodeActive(): #If active, then we have a valid scene Node and attribute wired into the Node
			self.sceneAppData.setAttr(self.attributeConnectorX.getSceneNode(), self.attributeConnectorX.getSceneNodeAttr(), attValue)
			# print "Moving x to : " + str(attValue)

	def setY(self, y):
		"""Function reaches down into the attributeConnectorY to set the Y value"""
		self.attributeConnectorY.setValue(-y)
		attValue = self.attributeConnectorY.getValue()
		if self.attributeConnectorY.isSceneNodeActive(): #If active, then we have a valid scene Node and attribute wired into the Node
			self.sceneAppData.setAttr(self.attributeConnectorY.getSceneNode(), self.attributeConnectorY.getSceneNodeAttr(), attValue)
			# print "Moving y to : " + str(attValue)

	def getMaxX(self):
		return self.attributeConnectorX.getMaxValue()

	def getMinX(self):
		return self.attributeConnectorX.getMinValue()

	def setMaxX(self, maxX):
		"""Function reaches down into the attributeConnectorX to set the maxX value"""
		self.attributeConnectorX.setMaxValue(float(maxX)) 

	def setMinX(self, minX):
		self.attributeConnectorX.setMinValue(float(minX)) 

	def getMaxY(self):
		return self.attributeConnectorY.getMaxValue()

	def getMinY(self):
		return self.attributeConnectorY.getMinValue()

	def setMaxY(self, maxY):
		"""Function reaches down into the attributeConnectorX to set the maxX value"""
		self.attributeConnectorY.setMaxValue(float(maxY)) 

	def setMinY(self, minY):
		self.attributeConnectorY.setMinValue(float(minY)) 



class DataServoBundle(DataBundle):
	"""This class inherits DataBundle, and bolts on to it some functionality for applying servo numbers and angle limits to those servos

	"""
	def __init__(self, sceneAppData):
		DataBundle.__init__(self, sceneAppData) 
		self.attributeConnectorX = AttributeServoConnector()
		self.attributeConnectorY = AttributeServoConnector()
		self.attributeConnectors = [self.attributeConnectorX, self.attributeConnectorY]



class AttributeConnector(object):
	"""

	"""
	def __init__(self):
		#LIST OF ATTRIBUTES
		self.sceneController = None
		self.node = None
		self.nodeIndex = None 
		self.controllerAttrName = None  #The name that the UI Node directional attribute will be associated with
		self.hostName = None #This is the name of the wiregroup or superNodegroup that the associated node belongs to - Do we just pass a reference to the Node itself?
		self.active = True #check if the attributeConnector is active, or whether it has been deativated by the pin/node being deativated 
		self.value = 0 #The final value delivered to the 3D app Scene Node. Adjusted and scaled by min/maxScale Values
		self.flipOutput = False
		self.minValue = None 
		self.maxValue = None
		self.minScale = 1.0 #attribute to scale the final Min output that goes to the scene Node - Use to change the output range to be other than -1 to 1
		self.maxScale = 1.0 #attribute to scale the final Max output that goes to the scene Node
		self.standardScale = 50.0 #Not currently being stored, since it is not currently being changed at all. Initialise at default
		self.sceneNode = None #string
		self.sceneNodeAttr = None #string
		self.sceneNodeActive = False #Activates when a valid Scene Node and Attribute are found

	def store(self):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load

		Need to record key data, but some data will be supplied by position in the total save XML tree. For example self.node can be set when attribute Connector
		loaded into the appropriate Node. 
		"""
		attributeConnectorRoot = xml.Element('AttributeConnector')
		attributes = xml.SubElement(attributeConnectorRoot,'attributes')
		xml.SubElement(attributes, 'attribute', name = 'nodeIndex', value = str(self.getNodeIndex()))
		xml.SubElement(attributes, 'attribute', name = 'controllerAttrName', value = str(self.getControllerAttrName()))
		xml.SubElement(attributes, 'attribute', name = 'hostName', value = str(self.getHostName()))
		xml.SubElement(attributes, 'attribute', name = 'active', value = str(self.isActive()))
		xml.SubElement(attributes, 'attribute', name = 'flipOutput', value = str(self.isFlipped()))
		xml.SubElement(attributes, 'attribute', name = 'minValue', value = (str(self.getMinValue())))
		xml.SubElement(attributes, 'attribute', name = 'maxValue', value = (str(self.getMaxValue())))
		xml.SubElement(attributes, 'attribute', name = 'minScale', value = (str(self.getMinScale())))
		xml.SubElement(attributes, 'attribute', name = 'maxScale', value = (str(self.getMaxScale())))        
		xml.SubElement(attributes, 'attribute', name = 'sceneNode', value = str(self.getSceneNode()))
		xml.SubElement(attributes, 'attribute', name = 'sceneNodeAttr', value = str(self.getSceneNodeAttr()))
		xml.SubElement(attributes, 'attribute', name = 'sceneNodeActive', value = str(self.isSceneNodeActive()))
		xml.SubElement(attributes, 'attribute', name = 'value', value = str(self.getValue()))

		return attributeConnectorRoot

	def read(self, attributeConnectorXml):
		"""A function to read in a block of XML and set all major attributes accordingly

		For this read, should we be setting things like self.node, and self.sceneController, or should we do that as an
		additional methods call after read?
		"""
		for a in attributeConnectorXml.findall( 'attributes/attribute'):
			if a.attrib['name'] == 'nodeIndex': self.setNodeIndex(int(a.attrib['value']))
			elif a.attrib['name'] == 'controllerAttrName': self.setControllerAttrName(str(a.attrib['value']))
			elif a.attrib['name'] == 'hostName': self.setHostName(str(a.attrib['value']))
			elif a.attrib['name'] == 'active': self.setActive(str(a.attrib['value']) == 'True')
			elif a.attrib['name'] == 'flipOutput': self.setFlipped(str(a.attrib['value']) == 'True')
			elif a.attrib['name'] == 'minValue': self.setMinValue(readAttribute(a.attrib['value']))
			elif a.attrib['name'] == 'maxValue': self.setMaxValue(readAttribute(a.attrib['value']))
			elif a.attrib['name'] == 'minScale': self.setMinScale(readAttribute(a.attrib['value']))
			elif a.attrib['name'] == 'maxScale': self.setMaxScale(readAttribute(a.attrib['value']))
			elif a.attrib['name'] == 'sceneNode': self.setSceneNode(str(a.attrib['value']))
			elif a.attrib['name'] == 'sceneNodeAttr': self.setSceneNodeAttr(str(a.attrib['value']))
			elif a.attrib['name'] == 'sceneNodeActive': self.setSceneNodeActive(str(a.attrib['value']) == 'True')
			elif a.attrib['name'] == 'value': self.setValue(readAttribute(a.attrib['value']))
		print "wscene Node : " + str(self.getSceneNode())
		print "scene Attr : " + str(self.getSceneNodeAttr())            

	def getSceneControl(self):
		return self.sceneControl

	def setSceneControl(self, sceneControl):
		"""Function to take a node selected in the Scene and assign it to the class"""
		self.sceneControl = sceneControl

	def getValue(self):
		"""Function to return the value of the attributeConnector. Flip is used to invert the input if needed"""
		if self.flipOutput:
			return -self.value
		else:
			return self.value

	def setValue(self, value):
		pValue = value
		if self.maxValue:
			if pValue > self.maxValue:
				pValue = self.maxValue
		if self.minValue:
			if pValue < self.minValue:
				pValue = self.minValue

		#Now calculate the proportion from -1 -> 0 -> 1 that we should be returning
		if pValue > 0:
			if self.maxValue:
				self.value = self.maxScale * round(float(pValue)/float(self.maxValue),3)
			else: 
				self.value = self.maxScale * round(float(pValue)/self.standardScale,3)
		else:
			if self.minValue:
				self.value = self.minScale * -round(float(pValue)/float(self.minValue),3)
			else: 
				self.value = self.minScale * round(float(pValue)/self.standardScale,3)

	def getMaxValue(self):
		return self.maxValue

	def getMinValue(self):
		return self.minValue

	def setMaxValue(self, maxValue):
		if maxValue: self.maxValue = float(maxValue)

	def setMinValue(self, minValue):
		if minValue: self.minValue = float(minValue)

	def getMinScale(self):
		return self.minScale

	def setMinScale(self, minScale):
		if minScale: self.minScale = minScale

	def getMaxScale(self):
		return self.maxScale

	def setMaxScale(self, maxScale):
		if maxScale: self.maxScale = maxScale

	def getControllerAttrName(self):
		"""Function to get name of the attribute that will be setup on the Scene Controller to represent the movement in that attribute of the Node"""
		return self.controllerAttrName

	def setControllerAttrName(self, name):
		"""Function to set name of the attribute that will be setup on the Scene Controller to represent the movement in that attribute of the Node"""
		self.controllerAttrName = str(name)

	def getNode(self):
		return self.node

	def setNode(self, node):
		self.node = node
		self.nodeIndex = node.getIndex()

	def getNodeIndex(self):
		return self.nodeIndex

	def setNodeIndex(self, index):
		self.nodeIndex = index

	def getHostName(self):
		return self.hostName

	def setHostName(self, hostName):
		"""Function to set the hostName which is the name of the wiregroup or superNodegroup that the associated node belongs to"""
		self.hostName = str(hostName)

	def isActive(self):
		"""Function to query is the AttributeConnector is active. AttributeConnectors can be deactivated if the pin/Node they are tied to is deactiveated"""
		return self.active

	def setActive(self, active):
		self.active = active

	def isFlipped(self):
		return self.flipOutput

	def setFlipped(self, flipped):
		self.flipOutput = flipped

	def getSceneNode(self):
		"""Function to get the name of the 3D app scene Node that the attributeConnector is looking to control"""
		return self.sceneNode

	def setSceneNode(self, sceneNode):
		"""Function to set the name of the 3D app scene Node that the attributeConnector is looking to control"""
		self.sceneNode = sceneNode

	def getSceneNodeAttr(self):
		"""Function to get the name of the 3D app scene Node attribute that the attributeConnector is looking to control"""
		return self.sceneNodeAttr

	def setSceneNodeAttr(self, sceneNodeAttr):
		"""Function to set the name of the 3D app scene Node attribute that the attributeConnector is looking to control"""
		if sceneNodeAttr == None: 
			self.sceneNodeActive = False
		else:
			self.sceneNodeActive = True
		self.sceneNodeAttr = sceneNodeAttr

	def isSceneNodeActive(self):
		return self.sceneNodeActive

	def setSceneNodeActive(self, active):
		self.sceneNodeActive = active



class AttributeServoConnector(AttributeConnector):
	"""This class inherits AttributeConnector, and bolts on to it some functionality for applying servo numbers and angle limits to those servos

	"""
	def __init__(self):
		AttributeConnector.__init__(self) 
		self.servoChannel = None
		self.servoMinAngle = None
		self.servoMaxAngle = None
		self.servoActive = None

	def getServoChannel(self):
		return self.servoChannel

	def setServoChannel(self, channel):
		if channel == None:
			self.servoChannel = None
		else:
			if channel > 24 or channel < 0:
				self.servoChannel = None
			else:
				self.servoChannel = int(channel)


	def getServoMinAngle(self):
		return self.servoMinAngle

	def setServoMinAngle(self, angle):
		self.servoMinAngle = angle
		return self.servoMinAngle

	def getServoMaxAngle(self):
		return self.servoMaxAngle

	def setServoMaxAngle(self, angle):
		self.servoMaxAngle = angle
		return self.servoMaxAngle

	def setupServoMinMaxAngles(self):
		if self.servoChannel == None: #The servo channel has been shut down, so set Min Max Angles to None
			self.servoMinAngle = None
			self.servoMaxAngle = None
		else: #ServoChannel has been initialised with an channel number
			if self.servoMinAngle == None: self.servoMinAngle = 0
			if self.servoMaxAngle == None: self.servoMaxAngle = 180

