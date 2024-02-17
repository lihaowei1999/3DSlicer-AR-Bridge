from enum import Enum
import numpy as np


class SlicerUnityCommandTemplate:
    def __init__(self, msg):
        self.msg = msg

    def getEncodedData(self):
        return b''


'''
vertexs : n * 3, float 32, input as mm, transfer as m
faces : m * 3, int 32
colors : n * 4, float 32
normals : n * 3, float32
transform : 4 * 4, float 32
name : "string"
attachTool : int
scale : 3 * 1, float 32
'''


class SlicerUnityCommandEncoder_CREATE_MODEL(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        attachNum = self.msg["attachTool"] if "attachTool" in self.msg else -1
        scale = self.msg["scale"].astype("float32")
        vertexs = self.msg["vertexs"].astype("float32") / 1000  # convert
        vertexs[:, 2] = -vertexs[:, 2]
        faces = self.msg["faces"].astype("int32")
        colors = self.msg["colors"].astype("float32")
        normals = self.msg["normals"].astype("float32")
        normals[:, 2] = -normals[:, 2]

        transform = self.msg["transform"].astype("float32")
        transform[0:3, 3] = transform[0:3, 3] / 1000  # right hand, do not ever send left hand side transform
        name = self.msg["name"]

        vertexNum = vertexs.shape[0]
        faceNum = faces.shape[0]
        nameLen = len(name)
        modelName = name.encode("utf-8")

        msg = np.array([vertexNum], dtype='int32').tobytes() + \
              np.array([faceNum], dtype='int32').tobytes() + \
              np.array([nameLen], dtype='int32').tobytes() + \
              vertexs.tobytes() + \
              colors.tobytes() + \
              faces.tobytes() + \
              normals.tobytes() + \
              transform.tobytes() + \
              modelName + \
              np.array([attachNum], dtype='int32').tobytes() + \
              scale.tobytes()

        return msg


'''
name : "string"
transform : 4 * 4, float 32 
scale : 3 * 1, float 32
'''


class SlicerUnityCommandEncoder_CHANGE_MODEL_TRANSFROM(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        transform = self.msg["transform"].astype("float32")
        scale = self.msg["scale"].astype("float32")
        transform[0:3, 3] = transform[0:3, 3] / 1000
        nameLen = len(name)
        modelName = name.encode("utf-8")

        msg = np.array([nameLen], dtype='int32').tobytes() + \
              transform.tobytes() + \
              modelName + \
              scale.tobytes()

        return msg


'''
name : string
'''


class SlicerUnityCommandEncoder_DELETE_MODEL(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        nameLen = len(name)
        modelName = name.encode("utf-8")
        msg = np.array([nameLen], dtype='int32').tobytes() + \
              modelName

        return msg


'''
name : string, 'all' for change the visibility of all the models
stat : bool
'''


class SlicerUnityCommandEncoder_CHANGE_MODEL_VISIBILITY(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        nameLen = len(name)
        modelName = name.encode("utf-8")
        msg = np.array([nameLen], dtype='int32').tobytes() + \
              modelName + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
transform : np.array
scale : 3 * 1, float 32
attachTool : int
'''


class SlicerUnityCommandEncoder_REFRESH_VOLUME_DATA(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        attachNum = self.msg["attachTool"] if "attachTool" in self.msg else -1

        scale = self.msg["scale"].astype("float32")
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        transform = self.msg["transform"].astype("float32")
        transform[0:3, 3] = transform[0:3, 3] / 1000
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              transform.tobytes() + \
              np.array([attachNum], dtype='int32').tobytes() + \
              scale.tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
transform : np.array
scale : 3 * 1, float 32
'''


class SlicerUnityCommandEncoder_SET_VOLUME_DATA_POSE(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        transform = self.msg["transform"].astype("float32")
        transform[0:3, 3] = transform[0:3, 3] / 1000
        scale = self.msg["scale"].astype("float32")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              transform.tobytes() + \
              scale.tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
'''


class SlicerUnityCommandEncoder_DELETE_VOLUME_DATA(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw

        return msg


'''
metaDataLocate : string, also use for name in unity
stat : bool
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_VISIBILITY(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
stat : bool
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_PAINTABLE_STAT(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
num : int
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_CUTOFF_BOX_NUM(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([int(self.msg["num"])], dtype="int32").tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
colorId : int
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_INTERACT_COLOR(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([int(self.msg["colorId"])], dtype="int32").tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
'''


class SlicerUnityCommandEncoder_FORCE_CLEAN_VOLUME_INTERACT_MASK(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw

        return msg


'''
metaDataLocate : string, also use for name in unity
colors : np.array()
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_COLORMAP(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        colors = self.msg["colors"].astype("float32")
        colorLen = colors.shape[0]

        msg = np.array([locateLen], dtype='int32').tobytes() + \
              np.array([colorLen], dtype='int32').tobytes() + \
              locateRaw + \
              colors.tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
stat : bool
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_MASK_DISPLAY_STAT(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
'''


class SlicerUnityCommandEncoder_UPDATE_VOLUME_LABEL_MAP(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw

        return msg


'''
metaDataLocate : string, also use for name in unity
'''


class SlicerUnityCommandEncoder_GET_VOLUME_LABEL_MAP(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw

        return msg


'''
metaDataLocate : string, also use for name in unity
stat : bool
'''


class SlicerUnityCommandEncoder_CHANGE_VOLUME_PRIORITY_MAP_RENDER_STAT(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
'''


class SlicerUnityCommandEncoder_UPDATE_VOLUME_PRIORITY_MAP(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw

        return msg


'''
metaDataLocate : string, also use for name in unity
priority : np.array, len = 8
'''


class SlicerUnityCommandEncoder_UPDATE_VOLUME_CUTOFF_PRIORITY(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        priority = self.msg["priority"].astype("float32")
        prioritySend = np.zeros([8], dtype="float32")
        for i in range(len(priority)):
            if i < 8:
                prioritySend[i] = priority[i]
        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              prioritySend.tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
mode : VolumeRenderMode
'''


class SlicerUnityCommandEncoder_UPDATE_VOLUME_RENDER_MODE(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        mode = self.msg["mode"].value

        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([mode], dtype=np.uint8).tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
num : int
restrictLabel : np.array, int 32, shape = 5
restrictMethod : np.array, int 32, shape = 5
'''


class SlicerUnityCommandEncoder_UPDATE_VOLUME_RENDER_INTERACTION_RESTRICTION(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        num = self.msg["num"]
        restrictLabel = self.msg["restrictLabel"].astype("int32")
        restrictMethod = self.msg["restrictMethod"].astype("int32")

        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([num], dtype="int32").tobytes() + \
              restrictLabel.tobytes() + \
              restrictMethod.tobytes()

        return msg


'''
metaDataLocate : string, also use for name in unity
colors : np.array([]), shape = [2048,4]
minVal : float32
maxVal : float32
'''


class SlicerUnityCommandEncoder_UPDATE_VOLUME_RENDER_TF1D(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        locate = self.msg["metaDataLocate"]
        locateLen = len(locate)
        locateRaw = locate.encode("utf-8")
        colors = self.msg["colors"].astype("float32")
        colorNum = colors.shape[0]
        minVal = self.msg["minVal"]
        maxVal = self.msg["maxVal"]

        msg = np.array([locateLen], dtype='int32').tobytes() + \
              locateRaw + \
              np.array([colorNum], dtype="int32").tobytes() + \
              colors.tobytes() + \
              np.array([minVal], dtype="float32").tobytes() + \
              np.array([maxVal], dtype="float32").tobytes()

        return msg


'''
name : string, also use for name in unity
stat : bool
'''


class SlicerUnityCommandEncoder_CHANGE_MODEL_PAINTABLE_STAT(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        nameLen = len(name)
        modelName = name.encode("utf-8")
        msg = np.array([nameLen], dtype='int32').tobytes() + \
              modelName + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        return msg


'''
name : string, also use for name in unity
stat : bool
port : int
'''


class SlicerUnityCommandEncoder_CHANGE_PAINTABLE_MODEL_STREAM_STAT(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        nameLen = len(name)
        modelName = name.encode("utf-8")
        msg = np.array([nameLen], dtype='int32').tobytes() + \
              modelName + \
              np.array([int(self.msg["stat"])], dtype=np.uint8).tobytes()

        if self.msg["stat"]:
            msg += np.array([int(self.msg["port"])], dtype="int32").tobytes()

        return msg


class SlicerUnityCommandEncoder_CHANGE_ANNOTATION_REFERENCE_MODEL(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        nameLen = len(name)
        modelName = name.encode("utf-8")
        msg = np.array([nameLen], dtype='int32').tobytes() + \
              modelName

        return msg


'''
name : string
'''


class SlicerUnityCommandEncoder_CHANGE_ANNOTATION_REFERENCE_VOLUME(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        name = self.msg["name"]
        nameLen = len(name)
        volumeName = name.encode("utf-8")
        msg = np.array([nameLen], dtype='int32').tobytes() + \
              volumeName

        return msg


'''
type : MarkUpType
data : n * 3 np.array
'''


class SlicerUnityCommandEncoder_UPDATE_ANNOTATION_FROM_SLICER(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        markerType = self.msg["type"]
        data = self.msg["data"].astype("float32")
        msg = np.array([markerType.value], dtype='int32').tobytes() + \
              np.array([data.shape[0]], dtype='int32').tobytes() + \
              data.tobytes()

        return msg


'''
stat : bool
port : int
'''


class SlicerUnityCommandEncoder_UPDATE_ANNOTATION_FROM_UNITY(SlicerUnityCommandTemplate):
    def getEncodedData(self):
        stat = int(self.msg["stat"])
        port = self.msg['port']
        msg = np.array([stat], dtype='int32').tobytes() + \
              np.array([port], dtype='int32').tobytes()
        return msg
