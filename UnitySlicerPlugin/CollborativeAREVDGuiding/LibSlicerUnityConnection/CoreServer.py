import zmq, slicer, vtk
import numpy as np
# core
from LibSlicerUnityConnection.UnityConnMsgEncoderInterface import SlicerUnityCommandType

# mesh
from LibSlicerUnityConnection.ModelVisualizeManager import ModelVisualizeManager
from LibSlicerUnityConnection.VertexMeshRender import VertexMeshRender
from LibSlicerUnityConnection.WebVertexInfoServiceZMQ import WebVertexInfoServiceZMQ

# roi, pc
from LibSlicerUnityConnection.PointCloudVisualizeManager import PointCloudVisualizeManager

# volume 
from LibSlicerUnityConnection.VolumeDataSenderMMAP import VolumeDataSenderMMAP


class SlicerUnityMainControllerZMQ:
    def __init__(self, ip, portControl):
        self.ip = ip
        self.portControl = portControl
        self.context = zmq.Context()

    def RequireChange(self, requireType: SlicerUnityCommandType, requireDataByte):
        commandByte = np.array([requireType.value], dtype='int32').tobytes()
        command = commandByte + requireDataByte
        sock = self.context.socket(zmq.REQ)
        sock.setsockopt(zmq.RCVTIMEO, 1000)
        sock.connect("tcp://%s:%s" % (self.ip, self.portControl))
        sock.send(command)
        feedback = sock.recv()
        sock.close()
        # now confirm
        valid = np.frombuffer(feedback, dtype='uint8').reshape([1, 1])[0][0]
        return valid > 0

class SlicerUnityConnServiceNode:
    def __init__(self):
        # main Controller
        self.mainUnityController = SlicerUnityMainControllerZMQ("localhost", 32000)

        self.volumeDataSyncerList = {}  # name -> volume Data Syncer
        self.volumeStatCache = {} # name -> VolumeRenderStatCache

        self.meshVertexColorSyncerList = {}  # name -> WebVertexInfoServiceZMQ


class SlicerUnityConnLocalDataNode:
    def __init__(self):
        ## preoperative planning
        # self.paintableHeadSurface = VertexMeshRender("paintableHeadSkinSurface")
        self.paintableSurfaceList = {}  # name -> VertexMeshRender
        self.paintableSurfaceCache = {} # name -> MeshRenderStatCache

        self.toolList = {} # name -> toolConfig
        self.objectToolAttachCache = [] # type, name, toolName

        ## intraoperative guiding
        self.defaultReconMeshStoreLocate = "xx"  # temp path to store recon result

        self.reconPointCloudVisualizor = PointCloudVisualizeManager()  # point cloud not as a node
        self.reconResultMeshVisualizor = ModelVisualizeManager(nodeName="node")
        self.reconResultMeshVisualizor.SetFileName(self.defaultReconMeshStoreLocate)

def DoForceRender():
    slicer.util.forceRenderAllViews()
