import serial
import sys

class MaestroSerialServo(object):
  """This class contains the instruction calls to test and make changes to the Maya scene
  """
  def __init__(self):
    self.serial = None
    self.active = False
    self.servoSystem = "Pololu Maestro Servo"
    self.init() #Call initialisation function

  def init(self):
    try:
      self.serial = serial.Serial(2) #Setup standard serial connection to Maestro Com. Setup Serial port for action
      self.serial.baudrate = 9600
      self.setActive(True)
      print "SERIAL INITIALISED :" + self.getServoSystem() + " detected."
    except:
      self.serial = None
      self.setActive(False)
      print "SERIAL ERROR : The Serial Port could not be opened properly. There will be no communication with the Pololu Maestro servo"

  def isActive(self):
    return self.active

  def setActive(self, active):
    self.active = bool(active)

  def getServoSystem(self):
    """Function to return the name of the servo system"""
    return self.servoSystem

  def setServo(self, n, angle, minAngle, maxAngle):
    #Quick check that things are in range
    servoAngle = angle
    if servoAngle > maxAngle:
      servoAngle = maxAngle
    elif servoAngle < minAngle:
      servoAngle = minAngle

    byteone=int(254*servoAngle/180) #calculate byte packet for angle signal
    # byteone = 254
    #Move to an absolute position in 8-bit mode (0x04 for the mode, 0 for the servo, 0-255 for the position (spread over two bytes))
    bud=chr(0xFF)+chr(n)+chr(byteone) 
    self.serial.write(bud) #Write out to serial to control server

  def close(self):
    """Function to check and close down the serial connection if one exists"""
    if self.active: #We have an active connection so lets close down
      self.serial.close()
      print "CLOSED SERIAL CONNECTION : Goodbye " + self.getServoSystem()