from .mesh_elements import MeshFace, MeshVertex


# https://www.xmswiki.com/wiki/SMS:2D_Mesh_Files_*.2dm
class Mesh2DMReader:
    """Class for reading points and faces from 2DM format."""

    def __init__(self, file_name: str) -> None:
        with open(file_name, "r", encoding="utf-8") as file:
            self.lines = file.readlines()

        self.points = []
        self.faces = []

        for line in self.lines:
            if line.startswith("ND"):
                self.points.append(MeshVertex.from_2dm_line(line))
            elif line.startswith("E3T") or line.startswith("E4Q"):
                self.faces.append(MeshFace.from_2dm_line(line))
