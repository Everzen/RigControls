#################################################################################################
##3DFRAMEWORK - Developed by Richard Jones
#
##PACKAGE:      3DFRAMEWORK
##SUB-MODULE:   FILECONTROL 
#
##VERSION:       1.0
##
##NOTES:  functions: export types and object list, import filepath file type, 
#################################################################################################


#################################################################################################
##IMPORTS 

import os
import xml.etree.ElementTree as xml


#################################################################################################
##CLASSES, FUNCTIONS AND DATA


class FileMan():
	"""A class to cover basic file tests, managing exporting, managing importing"""
	#Data
	fileName = None
	
	#Methods
	def __init__(self, userFileString):
		"""function to initialise class with correct file data"""
		self.fileName = userFileString
		
	def setFile(self,newFileName):
		"""Function to set the fileName data for the class"""
		self.fileName = newFileName
	
	def getFile(self):
		"""Function to get the fileName data for the class"""
		return (self.fileName)
	
	def exists(self):
		"""Function to determine if a file or directory exists"""
		if self.fileName == None:
			print "TError: File is not defined and therefore does not exist"
			return False
		else:
			fExist = os.path.exists(self.fileName)
			return fExist
	
	def createDir(self):
		"""This function tries to create a directory for the given filename"""
		if self.fileName != None:
			os.mkdir(self.fileName)
		else:
			print "TError: The filename is not defined so the directory cannot be created"
	

class XMLMan():
	#"""Class to simply the loading and procesing methods for XML"""
	#Data
	fileLoc = None
	tree = None
	markedBranches = []
	
	#Methods
	def setFile(self, fileName):
		"""Function to set the XML file location"""
		self.fileLoc = fileName
	
	def getFile(self):
		"""Function to get the XML file location"""
		return (self.fileLoc)
	
	def setTree(self,xmlTree):
		"""A function used to directly set the tree. Most often used when a file is not being loaded in"""
		self.tree = xmlTree
		return self.tree
	
	def getTree(self):
		return self.tree

	def getMarkedBranches(self):
		"""Function to get the Marked Branches"""
		return self.markedBranches
	
	def setMarkedBranches(self, branchArr):
		"""Function to set the Marked Branches"""
		self.markedBranches = branchArr

	def load(self):
		xmlTest = FileMan(self.fileLoc)
		if xmlTest.exists():
			xmlparse = xml.parse(self.fileLoc)
			self.tree = xmlparse.getroot()
		else:
			print "TError: The xml file name does not exist, so it cannot be loaded"

	def setLoad(self, fileName):
		"""Function to set and load the XML file from the set file location"""
		self.setFile(fileName)
		xmlTest = FileMan(self.fileLoc)
		if xmlTest.exists():
			xmlparse = xml.parse(self.fileLoc)
			self.tree = xmlparse.getroot()
		else:
			print "TError: The xml file name does not exist, so it cannot be loaded"
	
	def save(self):
		"""Function that will attempt to save out tree to the given file path"""
		xmlFile = open(self.fileLoc, 'w')
		xml.ElementTree(self.tree).write(xmlFile)
		xmlFile.close
	
	def iterFindBranch(self, branch, tName):
		"""Function to iteratively target branches of a given name"""
		targetbranch = branch.findall(tName)
		if len(targetbranch) != 0:
			for b in targetbranch:
		    		self.markedBranches.append(b)
		else:
			for child in branch:
		   		self.iterFindBranch(child, tName)

	def findBranch(self, tName):
		"""Function to return any elements with the target name"""
		self.setMarkedBranches([])
		if self.tree != None:
			self.iterFindBranch(self.tree, tName)
		else:
			print "TError: The xml tree was not defined, so no search is possible"
		return self.markedBranches

		



"""
#######################################################################################################################
#Reading in the XML Tree

import xml.etree.ElementTree as xml

#Feed in the Tree
tree = xml.parse("D:/UniversityofBolton/Modules/CG_DynamicsAndMotion/PythonSetup/XML_PythonTest/test.xml")

#Grab the Root of the Tree
rootElement = tree.getroot()

#Find all the tree Root children with a identified with a certain name
rChild = rootElement.findall('SystemPath')

#Loop through the resulting array and strip out whatever information is needed
for El in rChild
	print ((El.attrib.get('name')) + " can be found at " + (El.attrib.get('path')))

	
	def load(self):
		xmlTest = FileMan(fileLoc)
		if xmlTest.exists():
			self.tree = xml.parse(self.fileLoc)
		else:
			print "TError: The xml file name does not exist, so it cannot be loaded"






"""
