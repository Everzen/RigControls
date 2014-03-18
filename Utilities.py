import sys
from PySide import QtCore, QtGui
import numpy as np

#######STANDARD LIBRARY FUNCTIONS THAT SHOULD PROBABLY BE IN A CENTRALISED LIBRARY SOMEWHERE##############################


def norm(vec):
    """function to normalise a vector - creating the unit vector"""
    return vec/np.linalg.norm(vec)

def npVec(vec):
    """Converts a list/QPoint into an np array"""
    vec = np.array([vec.x(),vec.y()])
    # print "This is Vec : " + str(vec)
    return vec

def QPVec(npVec):
    """Converts an np array into a QPointF"""
    return QtCore.QPointF(npVec[0], npVec[1])

def readAttribute(attribute):
	"""Function to read an attribute as a string and return a float or None as appropriate"""
	try:
		float(attribute)
		return float(attribute)
	except ValueError:
		return None