from enum import Enum
import slicer
import numpy as np
import cv2, qt, copy, zmq


class MarkUpType(Enum):
    Point = 1
    Curve = 2
    Distance = 3
    Angle = 4
    ROI = 5


def GetDataFromMarkerNode(node):
    point_positions = np.zeros((node.GetNumberOfControlPoints(), 3))
    for i in range(node.GetNumberOfControlPoints()):
        node.GetNthControlPointPosition(i, point_positions[i])
        
    return point_positions


def CreateNodeFromData(nodeTypeName, data):
    node = slicer.mrmlScene.AddNewNodeByClass(nodeTypeName)
    for point in data:
        node.AddControlPoint(point[0], point[1], point[2])


class MarkerReceiverOneTime:
    def __init__(self, port, topic, interv, ip="localhost"):
        # web conn
        self.ip = ip
        self.port = port
        self.sock = None
        self.topic = topic

        self.interv = interv
        self.callBacks = {}
        self.callBacktoRemove = []

        self.inited = False
        self.shouldTerminate = False

        self.vertexNum = 0

    def RegisCallBack(self, regisName, callback):
        self.callBacks[regisName] = callback

    def RemoveCallBack(self, regisName):
        self.callBacktoRemove.append(regisName)

    def Start(self):
        if self.inited:
            return

        self.shouldTerminate = False
        self.__Loop()

    def Stop(self):
        if not self.inited:
            return

        self.shouldTerminate = True

    def __DoRemove(self, regisName):
        try:
            self.callBacks.pop(regisName)
        except Exception as e:
            return

    # Only Do Change to following functions.
    def __DoProcess(self, data):
        dataLen = len(data)
        dataPointer = 0
        while dataPointer < dataLen - 1:
            markerType = MarkUpType(np.frombuffer(data[dataPointer: dataPointer + 4], dtype="int32").reshape([1, 1])[0, 0])
            dataPointer += 4
            pointNum = np.frombuffer(data[dataPointer: dataPointer + 4], dtype="int32").reshape([1, 1])[0, 0]
            dataPointer += 4
            markers = np.zeros([pointNum, 3], dtype="float32")
            for i in range(pointNum):
                markers[i, 0] = np.frombuffer(data[dataPointer: dataPointer + 4], dtype="float32").reshape([1, 1])[0, 0]
                dataPointer += 4
                markers[i, 1] = np.frombuffer(data[dataPointer: dataPointer + 4], dtype="float32").reshape([1, 1])[0, 0]
                dataPointer += 4
                markers[i, 2] = np.frombuffer(data[dataPointer: dataPointer + 4], dtype="float32").reshape([1, 1])[0, 0]
                dataPointer += 4

            if markerType == MarkUpType.Point:
                CreateNodeFromData("vtkMRMLMarkupsFiducialNode", markers)
                continue

            if markerType == MarkUpType.Curve:
                CreateNodeFromData("vtkMRMLMarkupsCurveNode", markers)
                continue

            if markerType == MarkUpType.Distance:
                if markers.shape[0] != 2:
                    continue

                CreateNodeFromData("vtkMRMLMarkupsLineNode", markers)
                continue

            if markerType == MarkUpType.Angle:
                if markers.shape[0] != 3:
                    continue

                CreateNodeFromData("vtkMRMLMarkupsAngleNode", markers)
                continue

    def __Action(self, data):
        self.__DoProcess(data)

        for regisName in self.callBacks:
            self.callBacks[regisName]()

    def __InitResource(self):
        context = zmq.Context()
        self.sock = context.socket(zmq.SUB)
        self.sock.setsockopt(zmq.RCVHWM, 1)
        self.sock.connect("tcp://%s:%s" % (self.ip, self.port))
        self.sock.setsockopt(zmq.SUBSCRIBE, self.topic)

    def __ReleaseResource(self):
        self.sock.close()
        self.sock = None

    def __Loop(self):
        if self.shouldTerminate:
            if self.inited:
                self.__ReleaseResource()
                self.inited = False
            return


        if not self.inited:
            self.__InitResource()
            self.inited = True

        try:
            topic, data = self.sock.recv_multipart(zmq.DONTWAIT)
            self.__Action(data)
            self.shouldTerminate = True

        except Exception as e:
            pass

        qt.QTimer.singleShot(self.interv + 1, self.__Loop)