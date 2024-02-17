import vtk
import slicer
import numpy as np
import vtk.util.numpy_support as ns


class PointCloudVisualizeManager:
    def __init__(self):
        self.polydata = vtk.vtkPolyData()

        self.sphere = vtk.vtkSphereSource()
        self.sphere.SetRadius(1)
        self.glyph = vtk.vtkGlyph3D()
        self.glyph.SetInputData(self.polydata)
        self.glyph.SetSourceConnection(self.sphere.GetOutputPort())

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.glyph.GetOutputPort())
        self.actorPointCloud = vtk.vtkActor()
        self.actorPointCloud.SetMapper(self.mapper)

        self.hasData = False
        self.renderCenter = np.array([0, 0, 0])
        self.renderRadius = 300

    def SetRenderParameters(self, center, radius):
        self.renderRadius = radius
        self.renderCenter = center

    def SetPCData(self, data):
        pointsPC = vtk.vtkPoints()
        for p in data:
            if np.linalg.norm(p - self.renderCenter) < self.renderRadius:
                pointsPC.InsertNextPoint(p)

        self.polydata.SetPoints(pointsPC)
        self.hasData = True

    def SetStat(self, stat):
        if not self.hasData:
            return

        if not stat:
            renderer = slicer.app.layoutManager().threeDWidget(
                0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
            renderer.RemoveActor(self.actorPointCloud)
            slicer.util.forceRenderAllViews()
        else:
            renderer = slicer.app.layoutManager().threeDWidget(
                0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
            renderer.AddActor(self.actorPointCloud)
            slicer.util.forceRenderAllViews()