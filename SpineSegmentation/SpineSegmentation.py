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

    #Create the 'parameters' drop down in the module
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #Create the input selector for input volume
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = False
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = True
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene(slicer.mrmlScene)
    self.inputSelector.setToolTip("Select the input.")
    parametersFormLayout.addRow("Input Image Volume: ", self.inputSelector)

    #Create the output selector for output volume
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.outputSelector.setToolTip("Select the output.")
    parametersFormLayout.addRow("Output Image Volume: ", self.outputSelector)

    #Create a slider that allows user to set threshold
    self.ThresholdSlider = ctk.ctkRangeWidget()
    self.ThresholdSlider.singleStep = 1
    self.ThresholdSlider.minimum = -100
    self.ThresholdSlider.maximum = 100
    self.ThresholdSlider.setToolTip(
      "Set the minimum and maximum threshold for use with BinaryThreshold")
    parametersFormLayout.addRow("Threshold", self.ThresholdSlider)

    #Create a combo box to let the user select the image filter
    self.filterSelector = qt.QComboBox()
    parametersFormLayout.addRow("Image Filter:", self.filterSelector)
    self.filterSelector.addItem('No Additional Filter')
    self.filterSelector.addItem('Smoothing Recursive Gaussian')
    self.filterSelector.addItem('Discrete Gaussian')
    self.filterSelector.addItem('Shot Noise')
    self.filterSelector.addItem('Curvature Flow (Very Slow)')

    #Create the apply button
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.filterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()


  def cleanup(self):
    pass


  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    #Create logic instance
    logic = SpineSegmentationLogic()

    #Check to make sure input volume is not the same as output volume
    #This will fix the user error of when the volumes change after clicking apply, then applying the same volume
    properVolume = logic.checkInput(self.inputSelector.currentNodeID, self.outputSelector.currentNodeID)

    if properVolume:
      #When apply button is hit, get the threshold value
      minValue = self.ThresholdSlider.minimumValue
      maxValue = self.ThresholdSlider.maximumValue
      #Get the filter that was selected
      imageFilter = self.filterSelector.currentText

      #print threshold to console
      print("Threshold has been set to: Min: " + str(minValue) + ", Max: " + str(maxValue))
      #print filter to console
      print("Image filter has been set to: " + str(imageFilter))

      #Call the logic run() with the selectors and threshold
      logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), minValue, maxValue, imageFilter)

    else: #The volumes are the same
      print("ERROR: The input volume and output volume are the same. Please change this to continue.")


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

  def addFilterToImage(self, inputImage, outputName, filterName):
    '''
    :param image, outputName: The image that requires a filter and the output name
    :return: None, adds the filter and adds to slicer
    '''

    #Pull it from slicer
    image = sitkUtils.PullFromSlicer(inputImage)

    #Check which option the user chose.
    if filterName == "Smoothing Recursive Gaussian":
      imageFilter = SimpleITK.SmoothingRecursiveGaussianImageFilter()
    elif filterName == "Discrete Gaussian":
      imageFilter = SimpleITK.DiscreteGaussianImageFilter()
    elif filterName == "Shot Noise":
      imageFilter = SimpleITK.ShotNoiseImageFilter()
    elif filterName == "Curvature Flow":
      imageFilter = SimpleITK.CurvatureFlowImageFilter()
    else:
      print("ERROR: Filter was not properly set. Using Smoothing Recursive Gaussian.")
      imageFilter = SimpleITK.SmoothingRecursiveGaussianImageFilter()

    #Execute the filter on the image
    smoothedImage = imageFilter.Execute(image)
    #print("The " + filterName + " filter has been applied.")
    #Add it to slicer, overwrite the current node
    #True means overwrite the outputName instead of creating a new one
    sitkUtils.PushToSlicer(smoothedImage, outputName, 0, True)


  def thresholdImage(self, inputImage, outputName, minValue=0, maxValue=100):
    '''
    :param image, outputName, threshold values: image that requires threshold, output name, and threshold values
    Executes a threshold filter on the image and pushes it back to slicer.
    '''

    #Pull it from slicer
    image = sitkUtils.PullFromSlicer(inputImage)
    #Set the filter
    thresholdFilter = SimpleITK.BinaryThresholdImageFilter()
    #Set the value for something inside the threshold to be 1
    thresholdFilter.SetInsideValue(1)
    #Set the value for something outside the threshold to be 0
    thresholdFilter.SetOutsideValue(0)
    #Set the max and min threshold values
    thresholdFilter.SetLowerThreshold(minValue)
    thresholdFilter.SetUpperThreshold(maxValue)
    #execute the filter on the image
    thresholdedImage = thresholdFilter.Execute(image)
    #push it to slicer, overwrite current output node
    sitkUtils.PushToSlicer(thresholdedImage, outputName, 0, True)

  def checkInput(self, inputVolume, outputVolume):
    '''
    :param inputVolume: the input volume node
    :param outputVolume: the output volume node
    :return: boolean if the nodes are the same or not.
    '''
    if inputVolume == outputVolume:
      return False
    else:
      return True

  def run(self, inputVolume, outputVolume, minValue, maxValue, imageFilter):
    '''
    :param inputVolume: the input image volume
    :param outputVolume: the output image volume
    :param minValue: the min threshold selected by user
    :param maxValue: the max threshold select by user

    Gets the inputVolume name, pulls the image from slicer, adds the filter and threshold
    based on the user defined variables
    '''
    #Get the input image name
    inputImage = inputVolume.GetName()

    # Threshold the image with user-set threshold values
    self.thresholdImage(inputImage, outputVolume.GetName(), minValue, maxValue)

    #Check the selected filter to see if no filter option was chosen
    if imageFilter != "No Additional Filter":
      #Add the filter to the image
      self.addFilterToImage(inputImage, outputVolume.GetName(), imageFilter)
    print("\n")




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
    return imageName

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

  def test_SpineSegmentation1(self):
    """
    test_SpineSegmentation1 is a test that will load an image from a file path, display the image, and run a filter
    on the image to smooth it out.
    """
    #Setup logic
    logic = SpineSegmentationLogic()

    self.delayDisplay("Running test to load and smooth image.")
    #Load the image
    testImage = self.loadImage("/Users/Justin/GitHub/CISC472_SpineSegmentation/SpineData/007.CTDC.nrrd")
    #Add the filter
    logic.addFilterToImage(testImage, "Smoothed Image")
    self.delayDisplay("Thresholding image.")
    #Add threshold
    logic.thresholdImage("Smoothed Image", "Smoothed and Threshold Image")
    self.delayDisplay("Testing complete.")