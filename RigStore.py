
from PyQt4 import QtCore, QtGui
import FileControl
import xml.etree.ElementTree as xml

#######Project python imports################################################
from ControlItems import *

#################################CLASSES & FUNCTIONS FOR DATA STORAGE AND READING##################################################################################


class FaceGVCapture():
    def __init__(self, faceGView):
        """Class to capture all of the information out of the Graphics View"""
        self.view = faceGView
        self.scene = self.view.scene()
        self.viewXML = None
        self.xMLFile = None

    def setXMLFile(self,xMLFile):
        self.xMLFile = xMLFile
        self.setTree()

    def setTree(self):
        self.viewXML = FileControl.XMLMan()
        self.viewXML.setLoad(self.xMLFile)        

    def store(self):
        if self.xMLFile:
            self.viewXML = FileControl.XMLMan()
            self.viewXML.tree = xml.Element('faceRigGraphicsView')
            self.viewSettings = xml.SubElement(self.viewXML.tree,'viewSettings')
            self.sceneItems = xml.SubElement(self.viewXML.tree,'sceneItems')

            self.captureBackgroundImage() #Record the background Image
            self.captureViewSettings() # Capture remainng View settings
            self.captureReflectionLine()
            self.captureMarkers()
            self.captureWireGroups()

            #Now we have captured everything into a super giant XML tree we need to save this out.
            self.viewXML.setFile(self.xMLFile)
            self.viewXML.save()
        else: print "WARNING : COULD NOT SAVE FACE RIG TO FILE, SINCE A VALID FILE NAME WAS NOT SUPPLIED"

    def read(self):
        if self.viewXML:
            scene = self.view.scene()
            self.view.clear(isReflectionLine = False) #Clear the entire Graphics View, including reflection Line

            self.readBackgroundImage()
            self.readViewSettings()
            self.readRelectionLine()
            self.readMarkers()
            self.readWireGroups()
        else: print "WARNING : COULD NOT LOAD FACE RIG, SINCE A VALID FILE NAME WAS NOT SUPPLIED"

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
        """A Function to generate WireGroups from XML"""
        scene = self.view.scene()
        wireGroups = self.viewXML.findBranch("WireGroup")
        for w in wireGroups:
            newWireGroup = WireGroup(self.view)
            newWireGroup.read(w)
            self.view.wireGroups.append(newWireGroup)