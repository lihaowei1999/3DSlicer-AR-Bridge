import vtk, slicer
import numpy as np
import vtk.util.numpy_support as ns


class VertexMeshRender:
    def __init__(self, nodeName):
        self.nodeName = nodeName
        self.meshNode = None
        self.meshTransformNode = None
        self.vtk_vertices = None
        self.vtk_faces = None
        self.vtk_colors = None
        self.vertexNum = 0
        self.faceNum = 0
        self.mesh = None
        self.colors = None
        self.vertexArray = None
        self.faceArray = None
        self.colorArray = None
        self.TryGetNode()

    def TryGetNode(self):
        try:
            node = slicer.util.getNode(self.nodeName)
            self.meshNode = node
        except Exception as e:
            self.meshNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", self.nodeName)

        try:
            transformNode = slicer.util.getNode(self.nodeName + "_Transform")
            self.meshTransformNode = transformNode
        except:
            self.meshTransformNode = slicer.vtkMRMLLinearTransformNode()
            self.meshTransformNode.SetName(self.nodeName + "_Transform")
            slicer.mrmlScene.AddNode(self.meshTransformNode)

            initTransformNp = np.diag([1., 1., 1., 1.])
            initTransformvtk = vtk.vtkMatrix4x4()
            for i in range(4):
                for j in range(4):
                    initTransformvtk.SetElement(i, j, initTransformNp[i][j])

            self.meshTransformNode.SetMatrixTransformToParent(initTransformvtk)
            self.meshNode.SetAndObserveTransformNodeID(self.meshTransformNode.GetID())

    def Initiate(self, vertexs, faces, colors):
        self.TryGetNode()
        self.vertexNum = vertexs.shape[0]
        self.faceNum = faces.shape[0]

        self.vtk_vertices = vtk.vtkPoints()
        self.vtk_vertices.SetData(ns.numpy_to_vtk(vertexs.astype("float32")))

        faces = faces.astype("int64")
        self.vtk_faces = vtk.vtkCellArray()
        for face in faces:
            vtk_face = vtk.vtkTriangle()
            for i, idx in enumerate(face):
                vtk_face.GetPointIds().SetId(i, idx)
            self.vtk_faces.InsertNextCell(vtk_face)

        self.colors = colors.astype(np.uint8)
        self.vtk_colors = vtk.vtkUnsignedCharArray()
        self.vtk_colors.SetNumberOfComponents(3)
        self.vtk_colors.SetName("Colors")
        self.vtk_colors.SetArray(ns.numpy_to_vtk(self.colors), self.vertexNum * 3, 1)

        self.mesh = vtk.vtkPolyData()
        self.mesh.SetPoints(self.vtk_vertices)
        self.mesh.SetPolys(self.vtk_faces)
        self.mesh.GetPointData().SetScalars(self.vtk_colors)

        self.meshNode.SetAndObservePolyData(self.mesh)
        self.meshNode.CreateDefaultDisplayNodes()
        self.meshNode.GetDisplayNode().SetBackfaceCulling(0)
        self.vertexArray = vertexs
        self.faceArray = faces
        self.colorArray = colors

    def GetMeshInformation(self):
        return self.vertexArray, self.faceArray, self.colors

    def ChangeVertexColor(self, colors):
        self.colors = colors.astype(np.uint8)
        self.vtk_colors = vtk.vtkUnsignedCharArray()
        self.vtk_colors.SetNumberOfComponents(3)
        self.vtk_colors.SetName("Colors")
        self.vtk_colors.SetArray(ns.numpy_to_vtk(self.colors), self.vertexNum * 3, 1)
        self.mesh.GetPointData().SetScalars(self.vtk_colors)
        self.meshNode.SetAndObservePolyData(self.mesh)
        self.meshNode.CreateDefaultDisplayNodes()
        self.meshNode.GetDisplayNode().SetBackfaceCulling(0)

    def InitiateFromModelNode(self, inputModelNode):
        self.TryGetNode()
        polydata = inputModelNode.GetPolyData()
        points = polydata.GetPoints()
        numPoints = points.GetNumberOfPoints()
        colors = inputModelNode.GetDisplayNode().GetOutputPolyData().GetPointData().GetScalars()
        if colors is None:
            ambient_color = inputModelNode.GetDisplayNode().GetColor()
            ambient_color_np = np.array(ambient_color)
            color_array = (ambient_color_np.reshape([1, 3]).repeat(numPoints, axis=0) * 255).astype("uint8")
        else:
            color_array = ns.vtk_to_numpy(colors)

        faces = polydata.GetPolys()
        vertex_array = ns.vtk_to_numpy(points.GetData()).astype("float32")
        face_array = ns.vtk_to_numpy(faces.GetData()).astype("int64")
        face_array = face_array.reshape(-1, face_array[0] + 1)[::, 1:]

        transform_node = inputModelNode.GetParentTransformNode()

        if transform_node:
            transform_matrix = vtk.vtkMatrix4x4()
            transform_node.GetMatrixTransformToWorld(transform_matrix)
            transformNP = np.array([transform_matrix.GetElement(i, j) for i in range(4) for j in range(4)]).reshape(
                [4, 4])
        else:
            transformNP = np.diag([1., 1., 1., 1.]).astype('float64')

        # do init
        self.Initiate(vertex_array, face_array, color_array)

        transformvtk = vtk.vtkMatrix4x4()
        for i in range(4):
            for j in range(4):
                transformvtk.SetElement(i, j, transformNP[i][j])

        self.meshTransformNode.SetMatrixTransformToParent(transformvtk)
        self.meshNode.SetAndObserveTransformNodeID(self.meshTransformNode.GetID())

        # set visibility
        # originVisNode = inputModelNode.GetDisplayNode()
        # originVisNode.SetVisibility(False)
        #
        # newVisNode = self.meshNode.GetDisplayNode()
        # newVisNode.SetVisibility(True)

    def SetOpacity(self, sigma):
        self.meshNode.GetDisplayNode().SetOpacity(sigma)
