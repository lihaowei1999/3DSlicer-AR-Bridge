import numpy as np
from enum import Enum
from LibSlicerUnityConnection.Singleton import singleton
from LibSlicerUnityConnection.UnityConnMsgEncoderFactory import *


class SlicerUnityCommandType(Enum):
    ## model render
    CREATE_MODEL = 0
    CHANGE_MODEL_TRANSFROM = 1
    DELETE_MODEL = 2
    CHANGE_MODEL_VISIBILITY = 3

    ## volume render
    REFRESH_VOLUME_DATA = 10
    SET_VOLUME_DATA_POSE = 11
    DELETE_VOLUME_DATA = 12
    CHANGE_VOLUME_DATA_RENDER_SUB_STAT = 13  # not ready
    CHANGE_VOLUME_VISIBILITY = 14
    CHANGE_VOLUME_PAINTABLE_STAT = 15
    CHANGE_VOLUME_CUTOFF_BOX_NUM = 16
    CHANGE_VOLUME_INTERACT_COLOR = 17
    FORCE_CLEAN_VOLUME_INTERACT_MASK = 18
    CHANGE_VOLUME_COLORMAP = 19
    CHANGE_VOLUME_MASK_DISPLAY_STAT = 1010
    UPDATE_VOLUME_LABEL_MAP = 1011
    GET_VOLUME_LABEL_MAP = 1012
    CHANGE_VOLUME_PRIORITY_MAP_RENDER_STAT = 1013
    UPDATE_VOLUME_PRIORITY_MAP = 1014
    UPDATE_VOLUME_CUTOFF_PRIORITY = 1015

    UPDATE_VOLUME_RENDER_TF1D = 1017
    UPDATE_VOLUME_RENDER_MODE = 1018

    # define where the paint can draw on
    # mode, inside, outside, anywhere, (label id),
    UPDATE_VOLUME_RENDER_INTERACTION_RESTRICTION = 1019

    ## paintable mesh
    CHANGE_MODEL_PAINTABLE_STAT = 20
    CHANGE_PAINTABLE_MODEL_STREAM_STAT = 21

    ## annotation
    CHANGE_ANNOTATION_REFERENCE_MODEL = 50
    CHANGE_ANNOTATION_REFERENCE_VOLUME = 51
    UPDATE_ANNOTATION_FROM_SLICER = 52
    UPDATE_ANNOTATION_FROM_UNITY = 53


@singleton
class SlicerUnityCommandEncoderFactory:
    def __init__(self):
        self.__encoderMapping = {
            # model
            SlicerUnityCommandType.CREATE_MODEL: SlicerUnityCommandEncoder_CREATE_MODEL,
            SlicerUnityCommandType.CHANGE_MODEL_TRANSFROM: SlicerUnityCommandEncoder_CHANGE_MODEL_TRANSFROM,
            SlicerUnityCommandType.DELETE_MODEL: SlicerUnityCommandEncoder_DELETE_MODEL,
            SlicerUnityCommandType.CHANGE_MODEL_VISIBILITY: SlicerUnityCommandEncoder_CHANGE_MODEL_VISIBILITY,

            # volume
            SlicerUnityCommandType.REFRESH_VOLUME_DATA: SlicerUnityCommandEncoder_REFRESH_VOLUME_DATA,
            SlicerUnityCommandType.SET_VOLUME_DATA_POSE: SlicerUnityCommandEncoder_SET_VOLUME_DATA_POSE,
            SlicerUnityCommandType.DELETE_VOLUME_DATA: SlicerUnityCommandEncoder_DELETE_VOLUME_DATA,
            SlicerUnityCommandType.CHANGE_VOLUME_VISIBILITY: SlicerUnityCommandEncoder_CHANGE_VOLUME_VISIBILITY,
            SlicerUnityCommandType.CHANGE_VOLUME_PAINTABLE_STAT: SlicerUnityCommandEncoder_CHANGE_VOLUME_PAINTABLE_STAT,
            SlicerUnityCommandType.CHANGE_VOLUME_CUTOFF_BOX_NUM: SlicerUnityCommandEncoder_CHANGE_VOLUME_CUTOFF_BOX_NUM,
            SlicerUnityCommandType.CHANGE_VOLUME_INTERACT_COLOR: SlicerUnityCommandEncoder_CHANGE_VOLUME_INTERACT_COLOR,
            SlicerUnityCommandType.FORCE_CLEAN_VOLUME_INTERACT_MASK: SlicerUnityCommandEncoder_FORCE_CLEAN_VOLUME_INTERACT_MASK,
            SlicerUnityCommandType.CHANGE_VOLUME_COLORMAP: SlicerUnityCommandEncoder_CHANGE_VOLUME_COLORMAP,
            SlicerUnityCommandType.CHANGE_VOLUME_MASK_DISPLAY_STAT: SlicerUnityCommandEncoder_CHANGE_VOLUME_MASK_DISPLAY_STAT,
            SlicerUnityCommandType.UPDATE_VOLUME_LABEL_MAP: SlicerUnityCommandEncoder_UPDATE_VOLUME_LABEL_MAP,
            SlicerUnityCommandType.GET_VOLUME_LABEL_MAP: SlicerUnityCommandEncoder_GET_VOLUME_LABEL_MAP,
            SlicerUnityCommandType.CHANGE_VOLUME_PRIORITY_MAP_RENDER_STAT: SlicerUnityCommandEncoder_CHANGE_VOLUME_PRIORITY_MAP_RENDER_STAT,
            SlicerUnityCommandType.UPDATE_VOLUME_PRIORITY_MAP: SlicerUnityCommandEncoder_UPDATE_VOLUME_PRIORITY_MAP,
            SlicerUnityCommandType.UPDATE_VOLUME_CUTOFF_PRIORITY: SlicerUnityCommandEncoder_UPDATE_VOLUME_CUTOFF_PRIORITY,
            SlicerUnityCommandType.UPDATE_VOLUME_RENDER_TF1D: SlicerUnityCommandEncoder_UPDATE_VOLUME_RENDER_TF1D,
            SlicerUnityCommandType.UPDATE_VOLUME_RENDER_MODE: SlicerUnityCommandEncoder_UPDATE_VOLUME_RENDER_MODE,
            SlicerUnityCommandType.UPDATE_VOLUME_RENDER_INTERACTION_RESTRICTION: SlicerUnityCommandEncoder_UPDATE_VOLUME_RENDER_INTERACTION_RESTRICTION,

            # paint
            SlicerUnityCommandType.CHANGE_MODEL_PAINTABLE_STAT: SlicerUnityCommandEncoder_CHANGE_MODEL_PAINTABLE_STAT,
            SlicerUnityCommandType.CHANGE_PAINTABLE_MODEL_STREAM_STAT: SlicerUnityCommandEncoder_CHANGE_PAINTABLE_MODEL_STREAM_STAT,

            SlicerUnityCommandType.CHANGE_ANNOTATION_REFERENCE_MODEL: SlicerUnityCommandEncoder_CHANGE_ANNOTATION_REFERENCE_MODEL,
            SlicerUnityCommandType.CHANGE_ANNOTATION_REFERENCE_VOLUME: SlicerUnityCommandEncoder_CHANGE_ANNOTATION_REFERENCE_VOLUME,
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_SLICER: SlicerUnityCommandEncoder_UPDATE_ANNOTATION_FROM_SLICER,
            SlicerUnityCommandType.UPDATE_ANNOTATION_FROM_UNITY: SlicerUnityCommandEncoder_UPDATE_ANNOTATION_FROM_UNITY,
        }

    def getEncoder(self, commandType: SlicerUnityCommandType):
        return self.__encoderMapping[commandType]
