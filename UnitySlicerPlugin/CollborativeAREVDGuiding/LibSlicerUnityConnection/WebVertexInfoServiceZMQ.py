import cv2, qt, copy, zmq
import numpy as np
import time


class WebVertexInfoServiceZMQ:
    def __init__(self, port, topic, interv, ip="localhost"):
        # web conn
        self.ip = ip
        self.port = port
        self.topic = topic
        self.sock = None

        # loop and functions
        self.interv = interv
        self.callBacks = {}
        # should be locked, but anyway, possiblity is extremely low
        self.callBacktoRemove = []

        # stat
        self.inited = False
        self.shouldTerminate = False

        self.vertexNum = 0

    def RegisCallBack(self, regisName, callback):
        self.callBacks[regisName] = callback

    def RemoveCallBack(self, regisName):
        self.waitForRemove.append(regisName)

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
            self.callBacksWhenAcquire.pop(regisName)
        except Exception as e:
            return

    # Only Do Change to following functions.
    def __DoProcess(self, data):
        vertexColors = (np.frombuffer(data, dtype="float32").reshape([self.vertexNum, 4])[:, 0:3] * 255).astype(
            np.uint8)
        return vertexColors

    def __Action(self, data):
        for name in self.callBacktoRemove:
            if name in self.callBacks:
                self.DoRemove(name)

        self.callBacktoRemove = []

        if len(self.callBacks) > 0:
            vertexColors = self.__DoProcess(data)
            # operate
            for regisName in self.callBacks:
                self.callBacks[regisName](vertexColors)

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
            topic, vertexNum, data = self.sock.recv_multipart(zmq.DONTWAIT)
            self.vertexNum = np.frombuffer(vertexNum, dtype="int32")[0]
            self.__Action(data)

        except Exception as e:
            pass

        qt.QTimer.singleShot(self.interv + 1, self.__Loop)
