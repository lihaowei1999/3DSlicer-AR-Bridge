import numpy as np
from scipy.interpolate import interp1d
import slicer
from enum import Enum


def GetVolumeRenderTransferFunctionFromVolumeNode(volumeNode, textureLen=1024):
    texture = np.zeros([textureLen, 4], dtype="float32")
    volumeData = slicer.util.arrayFromVolume(volumeNode)
    minVal = volumeData.min()
    maxVal = volumeData.max()
    volumeRenderingDisplayNode = None

    for node in slicer.mrmlScene.GetNodesByClass('vtkMRMLVolumeRenderingDisplayNode'):
        if node.GetVolumeNodeID() == volumeNode.GetID():
            volumeRenderingDisplayNode = node
            break

    opacityMap = volumeRenderingDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    colorMap = volumeRenderingDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()
    steps = np.linspace(minVal, maxVal, num=textureLen)

    for i in range(len(steps)):
        texture[i, 0:3] = colorMap.GetColor(steps[i])[:]
        texture[i, 3] = opacityMap.GetValue(steps[i])

    ptr = 0
    for i in range(textureLen):
        if texture[i, 3] < 1e-6:
            ptr = i
        else:
            break

    opaLimMin = ptr / textureLen
    opaLimMax = 1

    return texture, opaLimMin, opaLimMax


class VolumeRenderMode(Enum):
    DirectVolumeRendering = 0
    MaximumIntensityProjection = 1
    IsoSurfaceRendering = 2


class VolumeRenderStatCache:
    def __init__(self):
        self.displayVolume = True
        self.displayLabel = False
        self.displayPriority = False
        self.interactable = False

        self.segmentationNode = None
        self.segmentationLabelNode = None

        self.prioritySegNode = None
        self.prioritySegLabelNode = None

        self.segmentationColors = None
        self.interactLabels = None

        ## interaction renstrictions
        self.MAX_VOLUME_INTERACTION_RESTRICT_RULE_NUMS = 5
        self.currentRestrictNums = 0
        self.restrictLabels = np.zeros([self.MAX_VOLUME_INTERACTION_RESTRICT_RULE_NUMS]).astype("int32")
        self.restrictInside = np.zeros([self.MAX_VOLUME_INTERACTION_RESTRICT_RULE_NUMS]).astype("int32")




