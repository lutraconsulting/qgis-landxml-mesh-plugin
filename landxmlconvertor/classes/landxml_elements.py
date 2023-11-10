import copy
import typing
import xml.etree.ElementTree as ET

from . import NS
from .mesh_elements import MeshFace, MeshVertex


class LandXMLSurface:
    """Class for reading individual surface from LandXML"""

    def __init__(self, surface: ET.Element, surface_number: int, id_offset: int = 0) -> None:
        self.name = ""

        self.surface = surface
        self.name = self.surface.attrib["name"]

        if not self.name:
            self.name = f"Surface_{surface_number}"

        self.id_offset = int(id_offset)

        self._points: typing.List[MeshVertex] = []
        self._get_points()

        self._faces: typing.List[MeshFace] = []
        self._get_faces()

    @property
    def _definition(self) -> ET.Element:
        return self.surface.find("landxml:Definition", namespaces=NS)

    def points(self, add_id_offset: bool = False) -> typing.List[MeshVertex]:
        """Returns deep copy of the vertices"""
        points = copy.deepcopy(self._points)
        if add_id_offset is False:
            return points
        else:
            for point in points:
                point.apply_id_offset(self.id_offset)
            return points

    def faces(self, add_id_offset: bool = False) -> typing.List[MeshFace]:
        """Returns deep copy of the faces"""
        faces = copy.deepcopy(self._faces)
        if add_id_offset is False:
            return faces
        else:
            for face in faces:
                face.apply_vertices_id_offset(self.id_offset)
            return faces

    def _get_points(self) -> None:
        if not self._definition:
            return

        points = self._definition.find("landxml:Pnts", namespaces=NS)

        if not points:
            return

        for point_element in points.findall("landxml:P", namespaces=NS):
            self._points.append(MeshVertex.from_xml_element(point_element))

    def _get_faces(self) -> None:
        if not self._definition:
            return

        faces = self._definition.find("landxml:Faces", namespaces=NS)

        if not faces:
            return

        for i, face_element in enumerate(faces.findall("landxml:F", namespaces=NS)):
            self._faces.append(MeshFace.from_xml_element(i + 1, face_element))
