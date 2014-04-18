
from PySide import QtCore, QtGui
import FileControl
import xml.etree.ElementTree as xml

#######Project python imports################################################
from ControlItems import *

#################################CLASSES & FUNCTIONS FOR DATA STORAGE AND READING##################################################################################


class FaceGVCapture():
    """This class captures all the information contained within the RigGraphics View

    The data is captured including the relationships between items (ex. Pins and Nodes)
    Skinning data for SuperNodes is also captured

    Everything is written out into a huge scene XML Tree using the "capture" methods in the
    main "store()" method

    This data is then saved to a specified XML file and can be loaded back in to rebuild the 
    graphics view by using the "read()" method
    """
    def __init__(self, faceGView, messageLogger, dataProcessor):
        """Class to capture all of the information out of the Graphics View"""
        self.view = faceGView
        self.dataProcessor = dataProcessor
        self.scene = self.view.scene()
        self.viewXML = None
        self.xMLFile = None

        self.messageLogger = messageLogger

    def setXMLFile(self,xMLFile):
        self.xMLFile = xMLFile
        self.setTree()

    def setTree(self):
        self.viewXML = FileControl.XMLMan()
        self.viewXML.setLoad(self.xMLFile)        

    def store(self):

        if not self.xMLFile:
            self.messageLogger.error("Invalid filename for saving: '%s'" % self.xMLFile)
            return

        self.viewXML = FileControl.XMLMan()
        self.viewXML.tree = xml.Element('faceRigGraphicsView')
        self.dataProcessorSettings = xml.SubElement(self.viewXML.tree,'dataProcessorSettings')
        self.viewSettings = xml.SubElement(self.viewXML.tree,'viewSettings')
        self.sceneItems = xml.SubElement(self.viewXML.tree,'sceneItems')

        self.captureDataProcessor() # Record the main DataProcessor for the scene. This mainly is about capturing what the SceneControl Node is
        self.captureBackgroundImage() #Record the background Image
        self.captureViewSettings() # Capture remainng View settings
        self.captureReflectionLine()
        self.captureMarkers()
        self.captureWireGroups()
        self.captureSuperNodeGroups()

        #Now we have captured everything into a super giant XML tree we need to save this out.
        self.viewXML.setFile(self.xMLFile)
        self.viewXML.save()

    def read(self):
        
        if not self.viewXML:
            self.messageLogger.error("Invalid filename for reading: '%s'" % self.viewXML)
            return

        # Clear the entire Graphics View, including reflection Line
        self.view.clear(isReflectionLine = False)

        self.readDataProcessor()
        self.readBackgroundImage()
        self.readViewSettings()
        self.readRelectionLine()
        self.readMarkers()
        self.readWireGroups()
        self.readSuperNodeGroups()

        # Updating a full draw for the whole scene
        scene = self.view.scene()
        scene.update(0,0,self.view.width,self.view.height)
        self.dataProcessor.manageAttributeConnections() #Now that the final wireGroup has been created, we have to align it with the sceneControl Attributes
        self.dataProcessor.setServoAppData() #Run through passing down the correct servoAppData to all levels

    def captureDataProcessor(self):
        """Function to process store the DataProcessor"""
        dataProcessorXml = self.dataProcessor.store()
        self.dataProcessorSettings.append(dataProcessorXml)

    def readDataProcessor(self):
        """A Function to load in the settings for main dataProcessor"""
        scene = self.view.scene()
        dataProcessorXML = self.viewXML.findBranch("DataProcessor")
        self.dataProcessor.read(dataProcessorXML[0]) #Read first element, because there will only ever be one element recorded
        print "My Processor Name is : " + str(self.dataProcessor.getSceneControl())
        self.dataProcessor.isSceneControllerActive()

    def captureBackgroundImage(self):
        """Function to process background Image into XML"""
        backgroundImage = xml.SubElement(self.viewSettings, 'attribute', name = 'backgroundImage', value = str(self.view.getBackgroundImage()))

    def readBackgroundImage(self):
        """Function to process background Image from XML"""
        viewSettings = self.viewXML.findBranch("viewSettings")[0]
        for a in viewSettings.findall( 'attribute'):
            if a.attrib['name'] == 'backgroundImage': self.view.setBackgroundImage(str(a.attrib['value']))
        self.view.setupBackground(remap = False) # Do not remap the reflection Line since it does not exist yet! 

    def captureViewSettings(self):
        """Function to process View Settings into XML"""
        markerCount = xml.SubElement(self.viewSettings, 'attribute', name = 'markerCount', value = str(self.view.getMarkerCount()))
        markerScale = xml.SubElement(self.viewSettings, 'attribute', name = 'markerScale', value = str(self.view.getMarkerScale()))

    def readViewSettings(self):
        """Function to process view Settings from XML"""
        viewSettings = self.viewXML.findBranch("viewSettings")[0]
        for a in viewSettings.findall( 'attribute'):
            if a.attrib['name'] == 'markerCount': self.view.setMarkerCount(int(a.attrib['value']))
            elif a.attrib['name'] == 'markerScale': self.view.setMarkerScale(float(a.attrib['value']))

    def captureReflectionLine(self):
        """Function to process Reflection Line into XML"""
        reflectionLine = self.view.getReflectionLine()
        reflectionLineXml = reflectionLine.store()
        self.sceneItems.append(reflectionLineXml)

    def readRelectionLine(self):
        scene = self.view.scene()
        reflectionLineXml = self.viewXML.findBranch("ReflectionLine")
        if len(reflectionLineXml) ==  1: #We have found a single Correct Reflection Line
            newReflectionLine = ReflectionLine(20,20)  #Initialise Reflection line with arbitary width and height that we can over ride immediately with read method
            newReflectionLine.read(reflectionLineXml[0])
            scene.addItem(newReflectionLine)
            self.view.setReflectionLine(newReflectionLine)
        else: print "WARNING : REFLECTION LINE ERROR : NO REFLECTION LINES OR MULTIPLE REFLECTIONS LINES WERE LOADED"

    def captureMarkers(self):
        """Function to process Markers into XML"""
        markers = self.view.getMarkerList()
        for m in markers:
            markerXML = m.store()
            self.sceneItems.append(markerXML)

    def readMarkers(self):
        scene = self.view.scene()
        markers = self.viewXML.findBranch("GuideMarker")
        for m in markers:
            newMarker = GuideMarker()
            newMarker.read(m)
            scene.addItem(newMarker)
            self.view.markerList.append(newMarker) #Add Marker to marker List
            if newMarker.getActive(): self.view.markerActiveList.append(newMarker)
        self.view.markerActiveList.sort(key=lambda x: x.getActiveIndex())
        self.view.processMarkerActiveIndex()  #Update all active states 

    def captureWireGroups(self):
        """Function to process WireGroups into XML"""
        wireGroups = self.view.getWireGroups()
        for w in wireGroups:
            wireXml = w.store()
            self.sceneItems.append(wireXml)
    
    def readWireGroups(self):
        """A Function to generate WireGroups from XML

        Broken down into first of all building all native nodes/pins in the wireGroups.
        Then resolving all the references of Nodes/pins that exist between wiregroups.
        Then building the required curves.
        """
        scene = self.view.scene()
        wireGroups = self.viewXML.findBranch("WireGroup")
        for w in wireGroups:
            newWireGroup = WireGroup(self.view, self.dataProcessor)
            newWireGroup.read(w)
            self.view.wireGroups.append(newWireGroup)
        # Now we have built all the nodes and pins we need to resolve references within the rigGView and build the curves
        for wireGroup in self.view.wireGroups:
            wireGroup.resolveReferences()
            wireGroup.createCurve()

    def captureSuperNodeGroups(self):
        """Function to process SuperNodeGroups into XML"""
        superNodeGroups = self.view.getSuperNodeGroups()
        for s in superNodeGroups:
            superNodeXml = s.store()
            self.sceneItems.append(superNodeXml)

    def readSuperNodeGroups(self):
        """A Function to generate SuperNodeGroups from XML"""
        scene = self.view.scene()
        superNodeGroups = self.viewXML.findBranch("SuperNodeGroup")
        for s in superNodeGroups:
            newSuperNodeGroup = SuperNodeGroup(QtCore.QPointF(0,0), "Arrow_4Point", self.view, self.dataProcessor) # Create SuperGroup with Arbitrary starting values
            newSuperNodeGroup.read(s)
            self.view.superNodeGroups.append(newSuperNodeGroup)
