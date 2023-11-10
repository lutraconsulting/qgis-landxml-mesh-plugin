import typing

from .mesh_elements import MeshFace, MeshVertex


class Mesh2DMWriter:
    """Writes 2DM format from list of mesh verticies and list of mesh faces"""

    def __init__(self, points: typing.List[MeshVertex], faces: typing.List[MeshFace]) -> None:
        self.points = points
        self.faces = faces

    def _as_2dm_string(self) -> str:
        str_points = "\n".join([x.as_2dm_element() for x in self.points])
        str_faces = "\n".join([x.as_2dm_element() for x in self.faces])

        return f"MESH2D\n{str_points}\n{str_faces}"

    def write(self, file_name: str) -> None:
        with open(file_name, "w+", encoding="utf-8") as file:
            file.write(self._as_2dm_string())
