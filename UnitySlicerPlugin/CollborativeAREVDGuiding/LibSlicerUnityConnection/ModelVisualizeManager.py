import vtk
import slicer
import vtk.util.numpy_support as ns


class ModelVisualizeManager:
    def __init__(self,nodeName):
        self.reader = None
        self.modelNode = None
        self.nodeName = nodeName
        self.modelDisplayNode = None
        self.fileName = None

    def SetFileName(self, name):
        self.fileName = name

    def SetStat(self, stat):
        if not stat:
            slicer.mrmlScene.RemoveNode(self.modelNode)
        else:
            self.reader = vtk.vtkPLYReader()
            self.reader.SetFileName(self.fileName)
            self.reader.Update()
            self.modelNode = slicer.vtkMRMLModelNode()
            self.modelNode.SetName(self.nodeName)
            self.modelNode.SetAndObservePolyData(self.reader.GetOutput())
            self.modelNode.SetScene(slicer.mrmlScene)
            self.modelNode.CreateDefaultDisplayNodes()
            self.modelDisplayNode = self.modelNode.GetDisplayNode()
            self.modelDisplayNode.SetVisibility2D(False)
            self.modelDisplayNode.SetVisibility(True)
            self.modelDisplayNode.SetOpacity(0.5)

            slicer.mrmlScene.AddNode(self.modelNode)