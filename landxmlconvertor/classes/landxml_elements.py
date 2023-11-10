import typing
import xml.etree.ElementTree as ET

from . import NS
from .mesh_elements import MeshFace, MeshVertex


class LandXMLSurface:
    """Class for reading individual surface from LandXML"""

    def __init__(self, surface: ET.Element, surface_number: int, id_prefix: int = 0) -> None:
        self.name = ""

        self.surface = surface
        self.name = self.surface.attrib["name"]

        if not self.name:
            self.name = f"Surface_{surface_number}"

        self.id_prefix = int(id_prefix)

        self.points: typing.List[MeshVertex] = []
        self._get_points()

        self.faces: typing.List[MeshFace] = []
        self._get_faces()

    @property
    def _definition(self) -> ET.Element:
        return self.surface.find("landxml:Definition", namespaces=NS)

    def _get_points(self) -> None:
        if not self._definition:
            return

        points = self._definition.find("landxml:Pnts", namespaces=NS)

        if not points:
            return

        for point_element in points.findall("landxml:P", namespaces=NS):
            self.points.append(MeshVertex.from_xml_element(point_element, self.id_prefix))

    def _get_faces(self) -> None:
        if not self._definition:
            return

        faces = self._definition.find("landxml:Faces", namespaces=NS)

        if not faces:
            return

        for i, face_element in enumerate(faces.findall("landxml:F", namespaces=NS)):
            self.faces.append(MeshFace.from_xml_element(i + 1, face_element, self.id_prefix))

    def points_as_2dm(self) -> str:
        return "\n".join([x.as_2dm_element() for x in self.points])

    def faces_as_2dm(self) -> str:
        return "\n".join([x.as_2dm_element() for x in self.faces])

    def as_2dm(self) -> str:
        return f"MESH2D\n{self.points_as_2dm()}\n{self.faces_as_2dm()}"
