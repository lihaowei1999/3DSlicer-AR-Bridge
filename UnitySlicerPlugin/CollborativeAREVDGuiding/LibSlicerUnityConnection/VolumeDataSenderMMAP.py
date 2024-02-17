import numpy as np
import mmap
import vtk, slicer
import math
import copy
from enum import Enum


class MainVolumeType(Enum):
    Intensity = 0
    RGB = 1


class VolumeMetaData:
    def __init__(self):
        self.id = 0
        self.d = 0
        self.w = 0
        self.h = 0
        self.dw = 0
        self.dh = 0
        self.dd = 0
        self.origin_x = 0
        self.origin_y = 0
        self.origin_z = 0
        self.mainVolumeType = MainVolumeType.Intensity
        self.rawLocate = ""
        self.rawLocate_r = ""
        self.rawLocate_g = ""
        self.rawLocate_b = ""
        self.diffLocate = ""
        self.labelLocate = ""
        self.priorityLocate = ""

        self.axisOrder = [0, 1, 2]

    def ToBuffer(self, blockSize=0):
        msg = b''
        msg += np.array([self.id], dtype='int32').tobytes()
        msg += np.array([self.w], dtype='int32').tobytes()
        msg += np.array([self.h], dtype='int32').tobytes()
        msg += np.array([self.d], dtype='int32').tobytes()
        msg += np.array([self.dw], dtype='float64').tobytes()
        msg += np.array([self.dh], dtype='float64').tobytes()
        msg += np.array([self.dd], dtype='float64').tobytes()
        msg += np.array([self.origin_x], dtype='float64').tobytes()
        msg += np.array([self.origin_y], dtype='float64').tobytes()
        msg += np.array([self.origin_z], dtype='float64').tobytes()
        msg += np.array([self.mainVolumeType.value], dtype='int32').tobytes()
        if self.mainVolumeType == MainVolumeType.Intensity:
            msg += np.array([len(self.rawLocate)], dtype='int32').tobytes()
            msg += self.rawLocate.encode("utf-8")
        elif self.mainVolumeType == MainVolumeType.RGB:
            msg += np.array([len(self.rawLocate_r)], dtype='int32').tobytes()
            msg += self.rawLocate_r.encode("utf-8")
            msg += np.array([len(self.rawLocate_g)], dtype='int32').tobytes()
            msg += self.rawLocate_g.encode("utf-8")
            msg += np.array([len(self.rawLocate_b)], dtype='int32').tobytes()
            msg += self.rawLocate_b.encode("utf-8")
        msg += np.array([len(self.diffLocate)], dtype='int32').tobytes()
        msg += self.diffLocate.encode("utf-8")
        msg += np.array([len(self.labelLocate)], dtype='int32').tobytes()
        msg += self.labelLocate.encode("utf-8")
        msg += np.array([len(self.priorityLocate)], dtype='int32').tobytes()
        msg += self.priorityLocate.encode("utf-8")
        msg += b'0' * (blockSize - len(msg))
        return msg

    def GetSpace(self):
        return self.w * self.d * self.h * 4


class VolumeDataSenderMMAP:
    def __init__(self, mainName, mainVolumeType=MainVolumeType.Intensity):
        self.lastVolumeName = ""
        self.metaData = VolumeMetaData()
        self.metaSize = 4096

        # should ensure the volume is no larger than this size
        self.volumeStaticSize = 1024 * 1024 * 500 * 4

        self.mapMain = None
        self.mapRaw = None
        self.mapRaw_r = None
        self.mapRaw_g = None
        self.mapRaw_b = None
        self.mapDiff = None
        self.mapLabel = None
        self.mapLabelr = None
        self.mapPriority = None

        self.tempVolumeData = None
        self.mainName = mainName
        self.metaData.mainVolumeType = mainVolumeType
        if self.metaData.mainVolumeType == MainVolumeType.Intensity:
            self.metaData.rawLocate = mainName + "_raw"
        else:
            self.metaData.rawLocate_r = mainName + "_raw_r"
            self.metaData.rawLocate_g = mainName + "_raw_g"
            self.metaData.rawLocate_b = mainName + "_raw_b"

        self.metaData.diffLocate = mainName + "_diff"
        self.metaData.labelLocate = mainName + "_label"
        self.metaData.priorityLocate = mainName + "_priority"

        self.minValue = 0
        self.maxValue = 0

        self.AllocateSpace()

    def AllocateSpace(self):
        self.mapMain = mmap.mmap(0, self.metaSize, self.mainName, mmap.ACCESS_WRITE)
        if self.metaData.mainVolumeType == MainVolumeType.Intensity:
            self.mapRaw = mmap.mmap(0, self.volumeStaticSize, self.metaData.rawLocate, mmap.ACCESS_WRITE)
        else:
            self.mapRaw_r = mmap.mmap(0, self.volumeStaticSize, self.metaData.rawLocate_r, mmap.ACCESS_WRITE)
            self.mapRaw_g = mmap.mmap(0, self.volumeStaticSize, self.metaData.rawLocate_g, mmap.ACCESS_WRITE)
            self.mapRaw_b = mmap.mmap(0, self.volumeStaticSize, self.metaData.rawLocate_b, mmap.ACCESS_WRITE)

        self.mapDiff = mmap.mmap(0, self.volumeStaticSize, self.metaData.diffLocate, mmap.ACCESS_WRITE)
        self.mapLabel = mmap.mmap(0, self.volumeStaticSize, self.metaData.labelLocate, mmap.ACCESS_WRITE)
        self.mapLabelr = mmap.mmap(0, self.volumeStaticSize, self.metaData.labelLocate, mmap.ACCESS_READ)
        self.mapPriority = mmap.mmap(0, self.volumeStaticSize, self.metaData.priorityLocate, mmap.ACCESS_WRITE)

        # write a invalid space
        self.mapMain.seek(0)
        self.mapMain.write(self.metaData.ToBuffer(self.metaSize))

    def StreamVolume(self, volumeNode):
        if not self.metaData.mainVolumeType == MainVolumeType.Intensity:
            print("wrong volume type")
            return

        self.UpdateConfigFromVolume(volumeNode)
        print(self.metaData.__dict__)

        # write
        self.tempVolumeData = slicer.util.arrayFromVolume(volumeNode)
        self.metaData.id += 1  # require id > 1

        ord = self.metaData.axisOrder
        ## do normalize
        sendVolume = copy.deepcopy(self.tempVolumeData).transpose([2 - ord[2], 2 - ord[1], 2 - ord[0]]).astype(
            "float32")

        self.minValue = sendVolume.min()
        self.maxValue = sendVolume.max()

        sendVolume = (sendVolume - sendVolume.min()) / (sendVolume.max() - sendVolume.min())

        self.mapRaw.seek(0)
        self.mapRaw.write(sendVolume.tobytes())

        # update the meta data after update all the volume
        self.mapMain.seek(0)
        self.mapMain.write(self.metaData.ToBuffer(self.metaSize))

    def StreamVolumeRGB(self, volumeNode_r, volumeNode_g, volumeNode_b):
        if not self.metaData.mainVolumeType == MainVolumeType.RGB:
            print("wrong volume type")
            return

        self.UpdateConfigFromVolume(volumeNode_r)
        print(self.metaData.__dict__)

        self.metaData.id += 1  # require id > 1
        ord = self.metaData.axisOrder

        volumeData_r = copy.deepcopy(
            slicer.util.arrayFromVolume(volumeNode_r).transpose([2 - ord[2], 2 - ord[1], 2 - ord[0]])).astype(
            "float32") / 256

        self.mapRaw_r.seek(0)
        self.mapRaw_r.write(volumeData_r.tobytes())

        volumeData_g = copy.deepcopy(
            slicer.util.arrayFromVolume(volumeNode_g).transpose([2 - ord[2], 2 - ord[1], 2 - ord[0]])).astype(
            "float32") / 256

        self.mapRaw_g.seek(0)
        self.mapRaw_g.write(volumeData_g.tobytes())

        volumeData_b = copy.deepcopy(
            slicer.util.arrayFromVolume(volumeNode_b).transpose([2 - ord[2], 2 - ord[1], 2 - ord[0]])).astype(
            "float32") / 256

        self.mapRaw_b.seek(0)
        self.mapRaw_b.write(volumeData_b.tobytes())

        self.mapMain.seek(0)
        self.mapMain.write(self.metaData.ToBuffer(self.metaSize))

    def GetValueBoundary(self):
        return self.minValue, self.maxValue

    def StreamLabel(self, labelMap: np.array):
        ord = self.metaData.axisOrder
        sendLabel = labelMap.transpose([2 - ord[2], 2 - ord[1], 2 - ord[0]]).astype("float32")
        self.mapLabel.seek(0)
        self.mapLabel.write(sendLabel.tobytes())
        return

    def RetrieveLabel(self):
        ord = self.metaData.axisOrder
        self.mapLabelr.seek(0)
        labelRaw = self.mapLabelr.read(
            self.metaData.w * \
            self.metaData.d * \
            self.metaData.h * 4
        )

        reverseOrd = [0, 1, 2]
        reverseOrd[2 - ord[2]] = 0
        reverseOrd[2 - ord[1]] = 1
        reverseOrd[2 - ord[0]] = 2

        labelReturn = np.frombuffer(labelRaw, dtype="float32").reshape([
            self.metaData.w,
            self.metaData.h,
            self.metaData.d
        ]).astype("int16").transpose(reverseOrd)

        return labelReturn

    def StreamPriorityLabel(self, priority):
        ord = self.metaData.axisOrder
        sendPriority = priority.transpose([2 - ord[2], 2 - ord[1], 2 - ord[0]]).astype("float32")
        self.mapPriority.seek(0)
        self.mapPriority.write(sendPriority.tobytes())
        return

    def UpdateConfigFromVolume(self, volumeNode):
        currentName = volumeNode.GetName()
        currentVolume = slicer.util.arrayFromVolume(volumeNode)
        currentVolumeShape = currentVolume.shape
        spacing = volumeNode.GetSpacing()
        if self.mainName != currentName or \
                self.metaData.w != currentVolumeShape[0] or \
                self.metaData.h != currentVolumeShape[1] or \
                self.metaData.d != currentVolumeShape[2] or \
                abs(self.metaData.dw - spacing[0]) > 1e-8 or \
                abs(self.metaData.dh - spacing[1]) > 1e-8 or \
                abs(self.metaData.dd - spacing[2]) > 1e-8:

            self.mainName = currentName

            origin = volumeNode.GetOrigin()
            self.metaData.origin_x = origin[0]
            self.metaData.origin_y = origin[1]
            self.metaData.origin_z = origin[2]

            ijkToRASMatrix = vtk.vtkMatrix4x4()
            volumeNode.GetIJKToRASDirectionMatrix(ijkToRASMatrix)
            ijkToRASDirections = np.array(
                [ijkToRASMatrix.GetElement(i, j) for i in range(3) for j in range(3)]).reshape([3, 3])
            order = [0, 1, 2]
            sgn = [1, 1, 1]
            for i in range(3):
                order[i] = np.where(np.abs(np.squeeze(ijkToRASDirections[i, :])) > 0.5)[0][0]
                if ijkToRASDirections[i, order[i]] < 0:
                    sgn[i] = -1

            # spacing ~ ijk
            self.metaData.dd = spacing[order[0]] * sgn[0]
            self.metaData.dh = spacing[order[1]] * sgn[1]
            self.metaData.dw = spacing[order[2]] * sgn[2]

            # shape ~ kji
            self.metaData.d = currentVolumeShape[2 - order[0]]
            self.metaData.h = currentVolumeShape[2 - order[1]]
            self.metaData.w = currentVolumeShape[2 - order[2]]

            self.metaData.axisOrder = order
