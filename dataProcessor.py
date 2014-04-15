##############################################################################################
##dataProcessor - Module to grab positions of the RigGraphicsView Nodes and SuperNodes
##			      and return their positions as useful float data that can be wired into 
##				  Maya scene Control Nodes (Control Curver or Locator) to drive rig movement.
from PySide import QtGui, QtCore
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
		self.mainWindow = None
		self.appName = sceneAppData.getAppName()
		self.sceneAppData = sceneAppData
		self.sceneControl = None
		self.sampleBundle = DataBundle(self.sceneAppData)
		self.dataBundles = []
		self.activeAttributeConnectors = []
		self.activeServoDataConnectors = []
		self.rigGraphicsView = None

	def setWindow(self, window):
		self.mainWindow = window

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
		for wG in wireGroups: #loop through the wiregroups adding the nodes to the activeNodes list
			for pin in wG.getPins():
				if pin.isActive(): #If the pin is active then the node is visible and we need to add the node
					activeNodes.append(pin.getNode())
		for sG in superNodegroups: activeNodes.append(sG.getSuperNode()) #loop through all the superNodeGroups adding the nodes to the activeNodes list

		#Now use this list to define the relevant dataBundles
		self.dataBundles = []
		# print "My newly collected active Nodes are " + str(len(activeNodes)) + " " + str(activeNodes)
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
		# print "My newly collected attCons are " + str(len(self.activeAttributeConnectors)) + " " + str(self.activeAttributeConnectors)
		return self.activeAttributeConnectors

	def collectActiveServoDataConnectors(self):
		"""Function that simply takes all the activeAttributeConnectors and loops through them to find all the associated active ServoDataConnectors"""
		self.activeServoDataConnectors = [] # clear out activeServoDataConnectors
		self.collectActiveAttributeConnectors() #Make sure the ActiveAttributeConnectors are uptodate
		for attCon in self.getActiveAttributeConnectors():
			for servoDataCon in attCon.getServoDataConnectors():
				self.activeServoDataConnectors.append(servoDataCon)
		return self.activeServoDataConnectors

	def getActiveAttributeConnectors(self):
		"""Function to return the current list of attributeConnectors as processed by collectActiveAttributeConnectors"""
		return self.activeAttributeConnectors

	def getActiveServoDataConnectors(self):
		"""Function to return the current list of ServoDataConnectors as processed by collectActiveServoDataConnectors"""
		return self.activeServoDataConnectors

	def getSceneControl(self):
		return self.sceneControl

	def setSceneControl(self, sceneControl):
		"""Function to take a node selected in the Scene and assign it to the class"""
		self.sceneControl = sceneControl

	def attachBundle(self, item):
		"""Takes a DataBundle and adds it to the list, assigning the Maya control along the way"""
		newBundle = copy.deepcopy(self.sampleBundle)
		print "Attaching Bundle - my dataProcessor SceneControl is : " + str(self.getSceneControl()) 
		newBundle.setDataProcessor(self)
		# newBundle.setSceneControl(self.sceneControl)
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

	def isSceneControllerActive(self):
		"""Function to check that the SceneControl is Active, if it isnt, then it builds a new SceneControl.
		A widget needs to be passed to the check for the pqSide dialogues... hacky
		"""
		#Basic Check - Expand to include checking whether the Node has been deleted from the scene
		if self.sceneControl:
			if self.objExists(self.sceneControl):
				return True
			else: #The controller name does not exist in the scene, so set to None
				self.sceneControl = None
		#There is not scene Controller so we neen to create one.
		sceneControllerName, ok = QtGui.QInputDialog.getText(
		        self.mainWindow, self.getAppName() + ' Scene Controller Name',
		        'Your ' + self.getAppName() + ' scene currently has now Scene Controller. To create one, please enter a unique Scene Controller Name:'
		        )
		while not self.isSceneControllerNameUnique(sceneControllerName):
		    sceneControllerName, ok = QtGui.QInputDialog.getText(
		            self.mainWindow, self.getAppName() + ' Scene Controller Name',
		            'Sadly that name already exists in the current Scene. Please enter a unique Scene Controller Name:'
		            )
		if ok: #We have a Unique Name so continue to build the controller
			self.createSceneControl(sceneControllerName)
			self.setSceneControl(sceneControllerName)
			print "dataProcessor : SceneControlName set to : " + str(self.sceneControl)

	def getAppName(self):
		"""Returns the 3D application Name which is specified upon creation of the DataProcessor"""
		return self.appName

	def isSceneControllerNameUnique(self, name):
		"""Function to test whether the suggested SceneControl name is unique in the 3D app scene"""
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

	def manageAttributeConnections(self):
		"""Function to run through all of the attribute Connections and check that their names are represented as attributes on the SceneControl"""
		self.collectActiveControlNodes() #This updates our dataBundles
		for bundle in self.dataBundles:
			bundle.setDataProcessor(self) #Ensure that the data Processor is up to date
			bundle.addTitleAttr() #First Add a Title 
			for attCon in bundle.getAttributeConnectors(): #Now loop through and add all the scene Control Attributes
				attCon.addSceneControlAttr()




class DataServoProcessor(DataProcessor):
	"""This class inherits DataProcessor, and bolts on to it some functionality for processing servos

	"""
	def __init__(self, sceneAppData):
		DataProcessor.__init__(self, sceneAppData)
		self.sampleBundle = DataServoBundle(sceneAppData) #Load in  the new DataServoBundle to access extra Servo functionality

	def checkUniqueServoChannels(self, dataServoConnector, channel):
		"""A function to cycle through all the dataServoConnectors and check that no other dataServoConnector has the same servoChannel as the input dataServoConnector"""
		for sDC in self.activeServoDataConnectors:
			if sDC != dataServoConnector:
				if sDC.getServoChannel() == channel: sDC.setServoChannel(None)

	def setupServoMinMaxAngles(self):
		"""Function to run through all active attributeConnectors and make sure their servo min and max angles are initiated correctly"""
		for sDC in self.activeServoDataConnectors: sDC.setupServoMinMaxAngles()


class DataBundle(object):
	"""This class looks at the node or the SuperNode and the associated constraints on that node and 
	from the x and y postions returns some nice float data for us to wire into Maya scene Nodes etc

	SceneControl - The master scene Node that we are using in Maya to load all the float data into


	"""
	def __init__(self, sceneAppData):
		#LIST OF ATTRIBUTES
		self.sceneAppData = sceneAppData
		self.dataProcessor = None 
		self.sceneControl = None
		self.hostName = None
		self.node = None
		self.controllerAttrName = None #The name that the UI Node directional attribute will be associated with
		self.attributeConnectorX = AttributeConnector(self.sceneAppData)
		self.attributeConnectorY = AttributeConnector(self.sceneAppData)
		self.attributeConnectors = [self.attributeConnectorX, self.attributeConnectorY]

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
			attConX = AttributeServoConnector(self.sceneAppData) #Create new X attributeConnector 
			attConX.read(atConXXML) #read in the data
			self.setAttributeConnectorX(attConX)

		attributeConnectorYXml = dataBundleXml.findall('attributeConnectorY')
		attConY = None
		for atConYXml in attributeConnectorYXml[0]:
			attConY = AttributeServoConnector(self.sceneAppData) #Create new X attributeConnector 
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

	def getDataProcessor(self):
		return self.dataProcessor

	def setDataProcessor(self, dataProcessor):
		"""Function to set Data Processor and ensure all attributeConnectors have it correctly set too"""
		self.dataProcessor = dataProcessor
		self.sceneControl = dataProcessor.getSceneControl()
		print "In the DataBundle the sceneControl is : " + str(self.sceneControl)
		for att in self.attributeConnectors:
			print "Updating DataProcessor in att : " + str(att)
			att.setDataProcessor(dataProcessor)

	def addTitleAttr(self):
		"""Function to add a locked off Bool Attribute to represent the DataBundle of AttributeConnector attribtues on the sceneControl"""
		if self.dataProcessor:
			if self.dataProcessor.sceneControllerExists(): #Check the sceneControl Exists
				print "Whn adding Title to DataBundle the sceneControl is : " + str(self.sceneControl)
				if self.sceneAppData.attExists(self.sceneControl , self.controllerAttrName):
					print "No Action : The following SceneControl attribute already exists - " + str(self.controllerAttrName)
				else: #Attribute does not already exist so add it: 
					self.sceneAppData.addTitleAttr(self.sceneControl , self.controllerAttrName)
			else: 
				print "SceneController didnt exist for Title"
		

class DataServoBundle(DataBundle):
	"""This class inherits DataBundle, and bolts on to it some functionality for applying servo numbers and angle limits to those servos

	"""
	def __init__(self, sceneAppData):
		DataBundle.__init__(self, sceneAppData) 
		self.sceneAppData = sceneAppData
		self.attributeConnectorX = AttributeServoConnector(sceneAppData)
		self.attributeConnectorY = AttributeServoConnector(sceneAppData)
		self.attributeConnectors = [self.attributeConnectorX, self.attributeConnectorY]



class AttributeConnector(object):
	"""

	"""
	def __init__(self, sceneAppData):
		#LIST OF ATTRIBUTES
		self.sceneAppData = sceneAppData
		self.dataProcessor = None
		self.sceneControl = None
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

	def getSceneControl(self):
		return self.sceneControl

	def setSceneControl(self, sceneControl):
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

	def addSceneControlAttr(self):
		"""Function to grab the scene control from the dataProcessor and add the appropriate attribute"""
		if self.dataProcessor:
			if self.dataProcessor.sceneControllerExists(): #Check the sceneControl Exists
				if self.sceneAppData.attExists(self.sceneControl , self.controllerAttrName):
					print "No Action : The following SceneControl attribute already exists - " + str(self.controllerAttrName)
				else: #Attribute does not already exist so add it: 
					self.sceneAppData.addAttr(self.sceneControl , self.controllerAttrName)
			else: 
				print "SceneController didnt exist"

	def getDataProcessor(self):
		return self.dataProcessor

	def setDataProcessor(self, dataProcessor):
		"""Function to set Data Processor and ensure all attributeConnectors have it correctly set too"""
		self.dataProcessor = dataProcessor
		if self.dataProcessor:
			self.sceneControl = dataProcessor.getSceneControl()


class AttributeServoConnector(AttributeConnector):
	"""This class inherits AttributeConnector, and bolts on to it some functionality for applying servo numbers and angle limits to those servos
	Servos are bolted on by adding ServoDataConnector objects, each of which describe a relationship out to a different servo

	"""
	def __init__(self, sceneAppData):
		AttributeConnector.__init__(self,sceneAppData)
		self.sceneAppData = sceneAppData
		self.servoDataConnectors = [ServoDataConnector(sceneAppData,0,self)] #intialise the list of servoDataConnectors with a single connector with ID 0

	def store(self):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load. 
		"""
		attributeServoConnectorRoot = xml.Element('AttributeServoConnector')
		attributes = xml.SubElement(attributeServoConnectorRoot,'attributes')
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

		# Now record the xml for the servoDataConnectors - there are possibly more than one
		servoDataConnectorsXml = xml.SubElement(attributeServoConnectorRoot,'ServoDataConnectors')
		for sDC in self.servoDataConnectors:
		    sDCXml = sDC.store()
		    servoDataConnectorsXml.append(sDCXml)

		return attributeServoConnectorRoot

	def read(self, attributeServoConnectorXml):
		"""A function to read in a block of XML and set all major attributes accordingly
		"""
		for a in attributeServoConnectorXml.findall( 'attributes/attribute'):
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

		#Now we have to load in the servoDataConnector information.
		servoDataConnectors = attributeServoConnectorXml.findall('ServoDataConnectors/ServoDataConnector')
		self.clearServoDataConnectors() #clear out all the base initialsed servodataconnectors in order to read the new ones in.
		for index, sDCXml in enumerate(servoDataConnectors):
			newServoDataConnector = self.addServoDataConnector() #add a new servoDataConnector, and store to a variable so we can read in data
			newServoDataConnector.read(sDCXml)

	def getServoDataConnectors(self):
		return self.servoDataConnectors

	def addServoDataConnector(self):
		"""Function to add a new ServoDataConnector to the end of the ServoDataConnectors list. Adds the appropirate ID from the ServoDataConnectors list length"""
		self.sortServoDataConnectors() #Sort all the current ServoDataConnectors
		newIndex = len(self.servoDataConnectors)
		newServoDataConnector = ServoDataConnector(self.sceneAppData,newIndex,self)
		self.servoDataConnectors.append(newServoDataConnector)
		return newServoDataConnector

	def removeServoDataConnector(self, index):
		"""Function to add a new ServoDataConnector to the end of the ServoDataConnectors list. Adds the appropirate ID from the ServoDataConnectors list length"""
		IDServoConnector = None
		servoNewList = []
		# print "My remove ID is " + str(ID)
		for sC in self.servoDataConnectors:
			if sC.getIndex() != index:
				servoNewList.append(sC) #If it is not equally to the ID number then we add it to the new servoList
		self.servoDataConnectors = servoNewList #This should remove the IDServoConnector from the main list
		self.sortServoDataConnectors() #Now neatly sort the remaining IDs

	def sortServoDataConnectors(self):
		"""Function update the IDs of the ServoDataConnector to fall in line with their positions in the servoDataConnectors list"""
		for index, connector in enumerate(self.servoDataConnectors):
			connector.setIndex(index)

	def clearServoDataConnectors(self):
		self.servoDataConnectors = []

	def getDataProcessor(self):
		return self.dataProcessor

	def setDataProcessor(self, dataProcessor):
		"""Function to set Data Processor and ensure all attributeConnectors have it correctly set too"""
		self.dataProcessor = dataProcessor
		if self.dataProcessor:
			self.sceneControl = self.dataProcessor.getSceneControl()
		print "Setting the Attibute Connector data Processor info : " + str(self.sceneControl)
		for sDC in self.servoDataConnectors:
			sDC.setDataProcessor(dataProcessor)




class ServoDataConnector(object):
	"""
	Class to describe the basic connection between the AttributeServoConnector data and how that maps out from the position of the Node/SuperNode to the correct servoChannel and servo angle etc.
	"""
	def __init__(self, sceneAppData, index, attributeServoConnector):
		#LIST OF ATTRIBUTES
		self.sceneAppData = sceneAppData
		self.dataProcessor = None
		self.sceneControl = None
		self.index = index
		self.attributeServoConnector = attributeServoConnector #Passing the paretn ServoDataConnector down, so it can be identified
		self.servoChannel = None
		self.servoMinAngle = None
		self.servoMaxAngle = None
		self.servoAttrName = None
		self.servoCurveName = None

	def store(self):
		"""Function to write out a block of XML that records all the major attributes that will be needed for save/load 
		"""
		servoDataConnectorRoot = xml.Element('ServoDataConnector')
		attributes = xml.SubElement(servoDataConnectorRoot,'attributes')
		xml.SubElement(attributes, 'attribute', name = 'index', value = str(self.getIndex()))
		xml.SubElement(attributes, 'attribute', name = 'servoChannel', value = str(self.getServoChannel()))
		xml.SubElement(attributes, 'attribute', name = 'servoMinAngle', value = str(self.getServoMinAngle()))
		xml.SubElement(attributes, 'attribute', name = 'servoMaxAngle', value = str(self.getServoMaxAngle()))

		return servoDataConnectorRoot

	def read(self, servoDataConnectorXml):
		"""A function to read in a block of XML and set all major attributes accordingly
		"""
		for a in servoDataConnectorXml.findall( 'attributes/attribute'):
			if a.attrib['name'] == 'index': self.setIndex(int(a.attrib['value']))
			elif a.attrib['name'] == 'servoChannel': self.setServoChannel(readAttribute(a.attrib['value']))
			elif a.attrib['name'] == 'servoMinAngle': self.setServoMinAngle(readAttribute(a.attrib['value']))
			elif a.attrib['name'] == 'servoMaxAngle': self.setServoMaxAngle(readAttribute(a.attrib['value']))

	def getIndex(self):
		return self.index

	def setIndex(self, index):
		self.index = index

	def getAttributeServoConnector(self):
		return self.attributeServoConnector

	def setAttributeServoConnector(self, attributeServoConnector):
		self.attributeServoConnector = attributeServoConnector

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
			if self.servoMinAngle == None: self.servoMinAngle = 0.0
			if self.servoMaxAngle == None: self.servoMaxAngle = 180.0

	def getServoAttrName(self):
		return self.servoAttrName

	def getServoCurveName(self):
		return self.servoCurveName

	def setServoAttrName(self):
		self.servoAttrName = self.attributeConnector.getHostName() + "_Servo" + str(self.index)
		self.setServoCurveName()

	def setServoCurveName(self):
		"""Function that sets the servoCurveName from the attributeConnector Name and servoDataConnector index"""
		self.servoCurveName = self.servoAttrName + "_animCurve"

	def createServoCurveNode(self):
		"""Function to create the appropriate curve Node name, using 3D app info"""
		if not self.sceneAppData.objExists(self.servoCurveName): #A curveNode of this name does not exist so we can go ahead and create it
			return self.sceneAppData.createNode(self.servoCurveName,'animCurveUU')
		else:
			print "WARNING : animCurveNode called : " + str(self.servoCurveName) + " already exists in the scene"
		return False

	def deleteServoCurveNode(self):
		"""Function to create the appropriate curve Node name, using 3D app info"""
		#find the 3D app curve Node and delete it
		if self.sceneAppData.objExists(self.servoCurveName):
			print "Deleting Existing AnimCurveNode : " + self.servoCurveName
			self.sceneAppData.deleteNode(self.servoCurveName)

	# def addSceneControlAttr(self):
	# 	"""Function to grab the scene control from the dataProcessor and add the appropriate attribute"""
	# 	if self.dataProcessor.sceneControllerExists(): #Check the sceneControl Exists
	# 		if self.sceneAppData.attExists(self.sceneControl , self.servoAttrName):
	# 			print "No Action : The following SceneControl attribute already exists - " + str(self.servoAttrName)
	# 		else: #Attribute does not already exist so add it: 
	# 			self.sceneAppData.addAttr(self.sceneControl , self.servoAttrName)

	def getDataProcessor(self):
		return self.dataProcessor

	def setDataProcessor(self, dataProcessor):
		"""Function make sure the dataProcessor is uptodate"""
		self.dataProcessor = dataProcessor
		self.sceneControl = self.dataProcessor.getSceneControl()