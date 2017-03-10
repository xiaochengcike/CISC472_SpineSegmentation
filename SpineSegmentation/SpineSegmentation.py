import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import sitkUtils
import SimpleITK

"""
Justin Gerolami - 10160479
Cisc 472 Project - Spine Segmentation

This is a module for 3DSlicer which will segment the spine of children with scoliosis.
"""

class SpineSegmentation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SpineSegmentation"
    self.parent.categories = ["Cisc472"]
    self.parent.dependencies = []
    self.parent.contributors = ["Justin Gerolami (Queen's University)"]
    self.parent.helpText = """
    This is a project for CISC 472. This project performs spine segmentation
    on children with scoliosis.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Justin Gerolami as a 
    CISC472 - Medical Informatics Project.
    """ 

#
# SpineSegmentationWidget
#

class SpineSegmentationWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

  def cleanup(self):
    pass

  def onSelect(self):
    pass

  def onApplyButton(self):
    pass

#
# SpineSegmentationLogic
#

class SpineSegmentationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


#
#SpineSegmentationTest
#

class SpineSegmentationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SpineSegmentation1()

  def getImageFileName(self, imagePath):
    """
    :param imagePath: a path to the image
    :return: the image name with extension
    """
    #Loop through the reverse string, check if /
    for i in range(len(imagePath)-1, -1, -1):
      #if its '/' then return everything to the right (the file name)
      if imagePath[i] == '/':
        return imagePath[i:]
    #There is no '/' so the imagePath should just be the file name.
    return imagePath

  def getImageName(self, imageName):
    '''
    :param imageName: The name of the image with extension and maybe starting '/'
    :return: The name of just the image
    '''
    #Check if there is a leading '/' and remove it
    if imageName[0] == '/':
      imageName = imageName[1:]
    #Get the location of the first '.' ex. testImage.nrrd would return location of '.'
    periodLocation = imageName.find(".")
    #If we found a '.'
    if periodLocation != -1:
      #return the name from beginning to the '.' ex. testImage.nrrd returns testImage
      return imageName[:periodLocation]
    else:
      #returns the image name if no '.' was found
      return imageName


  def loadImage(self, imagePath):
    """
    :param imagePah: takes the image path as a parameter.
    :return: the image pulled from slicer
    """
    #Load the image from a hard-coded path
    #Future updates can allow the user to change this
    slicer.util.loadVolume(imagePath)
    #Get the file name and extension
    imageName = self.getImageFileName(imagePath)
    #Now we want just the filename
    imageName = self.getImageName(imageName)
    #We want to get the image name, which is after the last '/'
    #Now that we have the image loaded, pull the name from slicer.
    loadedImage = sitkUtils.PullFromSlicer(imageName)
    return loadedImage


  def addFilterToImage(self, image):
    '''
    :param image: The image that requires a filter
    :return: None, adds the filter and adds to slicer
    '''
    #Use the gaussian image filter for smoothing
    #https://itk.org/SimpleITKDoxygen/html/classitk_1_1simple_1_1SmoothingRecursiveGaussianImageFilter.html#details

    #Will experiment with others later
    imageFilter = SimpleITK.SmoothingRecursiveGaussianImageFilter()
    #Execute the filter on the image
    smoothedImage = imageFilter.Execute(image)
    #Add it to slicer
    sitkUtils.PushToSlicer(smoothedImage, 'Smoothed Image')


  def test_SpineSegmentation1(self):
    """
    test_SpineSegmentation1 is a test that will load an image from a file path, display the image, and run a filter
    on the image to smooth it out.
    """

    self.delayDisplay("Running test to load and smooth image.")
    #Load the image
    testImage = self.loadImage("/Users/Justin/GitHub/CISC472_SpineSegmentation/SpineData/007.CTDC.nrrd")
    #Add the filter
    self.addFilterToImage(testImage)
    self.delayDisplay("Testing complete.")

    