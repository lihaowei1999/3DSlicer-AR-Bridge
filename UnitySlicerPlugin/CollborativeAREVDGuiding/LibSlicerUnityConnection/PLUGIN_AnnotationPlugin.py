import logging
import os

import numpy as np
import vtk

import slicer
from slicer import util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import open3d as o3d
from LibSlicerUnityConnection.CoreServer import *
from LibSlicerUnityConnection.VolumeRenderController import *
from LibSlicerUnityConnection.VolumeRenderController import VolumeRenderMode
from LibSlicerUnityConnection.VolumeDataSenderMMAP import *
from LibSlicerUnityConnection.UnityConnMsgEncoderInterface import *
from LibSlicerUnityConnection.VertexMeshRender import *
from LibSlicerUnityConnection.AnnotationUtility import *
from LibSlicerUnityConnection.WebVertexInfoServiceZMQ import *
from LibSlicerUnityConnection.MeshRenderController import *
from LibSlicerUnityConnection.NetUtility import *
from LibSlicerUnityConnection.TrackingInterface import *
import qt
import time


class CollaborativeAREVDGuidingPlugin_Annotation_Widget:
    def __init__(self, mainWidget, connService, localDataNode):
        self.mainWidget = mainWidget
        self.logic = CollaborativeAREVDGuidingPlugin_Annotation_Logic(connService, localDataNode)
        self.InitSubUIComponents()

    def InitSubUIComponents(self):
        self.mainWidget.ui.planning_Annotation_VolumeReferenceComboBox.nodeTypes = ("vtkMRMLScalarVolumeNode", "")
        self.mainWidget.ui.planning_Annotation_VolumeReferenceComboBox.setMRMLScene(slicer.mrmlScene)

        self.mainWidget.ui.planning_Annotation_MeshReferenceComboBox.nodeTypes = ("vtkMRMLModelNode", "")
        self.mainWidget.ui.planning_Annotation_MeshReferenceComboBox.setMRMLScene(slicer.mrmlScene)

        self.mainWidget.ui.planning_Annotation_PointListMarkerComboBox.nodeTypes = ("vtkMRMLMarkupsFiducialNode", "")
        self.mainWidget.ui.planning_Annotation_PointListMarkerComboBox.setMRMLScene(slicer.mrmlScene)

        self.mainWidget.ui.planning_Annotation_CurveMarkerComboBox.nodeTypes = ("vtkMRMLMarkupsCurveNode", "")
        self.mainWidget.ui.planning_Annotation_CurveMarkerComboBox.setMRMLScene(slicer.mrmlScene)

        self.mainWidget.ui.planning_Annotation_DistanceMarkerComboBox.nodeTypes = ("vtkMRMLMarkupsLineNode", "")
        self.mainWidget.ui.planning_Annotation_DistanceMarkerComboBox.setMRMLScene(slicer.mrmlScene)

        self.mainWidget.ui.planning_Annotation_AngleMarkerComboBox.nodeTypes = ("vtkMRMLMarkupsAngleNode", "")
        self.mainWidget.ui.planning_Annotation_AngleMarkerComboBox.setMRMLScene(slicer.mrmlScene)

        self.mainWidget.ui.planning_Annotation_SetVolumeRefButton.connect('clicked(bool)', self.OnSetVolumeRef)
        self.mainWidget.ui.planning_Annotation_SetMeshRefButton.connect('clicked(bool)', self.OnSetMeshRef)
        self.mainWidget.ui.planning_Annotation_SyncPointListMarkerButton.connect('clicked(bool)', self.OnSyncPointList)
        self.mainWidget.ui.planning_Annotation_SyncCurveMarkerButton.connect('clicked(bool)', self.OnSyncCurve)
        self.mainWidget.ui.planning_Annotation_SyncDistanceMarkerButton.connect('clicked(bool)', self.OnSyncDistance)
        self.mainWidget.ui.planning_Annotation_SyncAngleMarkerButton.connect('clicked(bool)', self.OnSyncAngle)
        self.mainWidget.ui.planning_Annotation_GetMarkerBackButton.connect('clicked(bool)', self.OnGetAnnotationBack)

    def OnSetMeshRef(self):
        node = self.mainWidget.ui.planning_Annotation_MeshReferenceComboBox.currentNode()
        if node is None:
            return

        self.logic.SetMeshRef(node)

    def OnSetVolumeRef(self):
        node = self.mainWidget.ui.planning_Annotation_VolumeReferenceComboBox.currentNode()
        if node is None:
            return

        self.logic.SetVolumeRef(node)

    def OnSyncPointList(self):
        node = self.mainWidget.ui.planning_Annotation_PointListMarkerComboBox.currentNode()
        if node is None:
            return

        self.logic.SyncPointList(node)

    def OnSyncCurve(self):
        node = self.mainWidget.ui.planning_Annotation_CurveMarkerComboBox.currentNode()
        if node is None:
            return

        self.logic.SyncCurve(node)

    def OnSyncDistance(self):
        node = self.mainWidget.ui.planning_Annotation_DistanceMarkerComboBox.currentNode()
        if node is None:
            return

        self.logic.SyncDistance(node)

    def OnSyncAngle(self):
        node = self.mainWidget.ui.planning_Annotation_AngleMarkerComboBox.currentNode()
        if node is None:
            return

        self.logic.SyncAngle(node)

    def OnGetAnnotationBack(self):
        self.logic.GetAnnotation()


class CollaborativeAREVDGuidingPlugin_Annotation_Logic:
    def __init__(self, connServices, localDataNode):
        self.connServices = connServices
        self.localDataNode = localDataNode

    def SetMeshRef(self, meshNode):
        MSG = {
            "name": meshNode.GetName()
        }

        self.UpdateMsg(
            SlicerUnityCommandType.CHANGE_ANNOTATION_REFERENCE_MODEL,
            MSG
        )

    def SetVolumeRef(self, volumeNode):
        MSG = {
            "name": volumeNode.GetName()
        }

        self.UpdateMsg(
            SlicerUnityCommandType.CHANGE_ANNOTATION_REFERENCE_VOLUME,
            MSG
        )

    def SyncPointList(self, pointListNode):
        data = GetDataFromMarkerNode(pointListNode)
        MSG = {
            "type": MarkUpType.Point,
            "data": data
        }

        self.UpdateMsg(
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_SLICER,
            MSG
        )

    def SyncCurve(self, curveNode):
        data = GetDataFromMarkerNode(curveNode)
        MSG = {
            "type": MarkUpType.Curve,
            "data": data
        }

        self.UpdateMsg(
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_SLICER,
            MSG
        )

    def SyncDistance(self, distanceNode):
        data = GetDataFromMarkerNode(distanceNode)
        MSG = {
            "type": MarkUpType.Distance,
            "data": data
        }

        self.UpdateMsg(
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_SLICER,
            MSG
        )

    def SyncAngle(self, angleNode):
        data = GetDataFromMarkerNode(angleNode)
        MSG = {
            "type": MarkUpType.Angle,
            "data": data
        }

        self.UpdateMsg(
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_SLICER,
            MSG
        )

    def GetAnnotation(self):
        port = next_free_port()
        markerReceiver = MarkerReceiverOneTime(port, b'marker', 20, "localhost")

        def TerminateCallBack():
            MSGTerminate = {
                "stat": False,
                "port": port
            }

            self.UpdateMsg(
                SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_UNITY,
                MSGTerminate
            )

        markerReceiver.RegisCallBack("call", TerminateCallBack)

        markerReceiver.Start()
        MSG = {
            "stat": True,
            "port": port
        }

        self.UpdateMsg(
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_UNITY,
            MSG
        )

    def UpdateMsg(self, msgType: SlicerUnityCommandType, msg):
        self.connServices.mainUnityController.RequireChange(
            msgType,
            SlicerUnityCommandEncoderFactory().getEncoder(
                msgType
            )(msg).getEncodedData()
        )

