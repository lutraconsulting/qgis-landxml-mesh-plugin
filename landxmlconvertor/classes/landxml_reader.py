import typing
import xml.etree.ElementTree as ET

from . import NS
from .landxml_elements import LandXMLSurface
from .mesh_elements import MeshFace, MeshVertex


# http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd
class LandXMLReader:
    """Class for reading the LandXML file, store individual surfaces."""

    SURFACE_VERTEX_ID_OFFSET = 10_000

    def __init__(self, path: str):
        self.path = path
        self.xml_tree = ET.parse(self.path)

        self.surfaces: typing.List[LandXMLSurface] = []
        self._get_surfaces()

    @property
    def xml_root(self) -> ET.Element:
        return self.xml_tree.getroot()

    @property
    def surface_count(self) -> int:
        return len(self.surfaces)

    def get_surface_points(self, surface_number: int) -> typing.List[MeshVertex]:
        return self.surfaces[surface_number].points

    def get_surface_faces(self, surface_number: int) -> typing.List[MeshFace]:
        return self.surfaces[surface_number].faces

    def _get_surfaces(self) -> None:
        surfaces = self.xml_root.find("landxml:Surfaces", namespaces=NS)
        if surfaces:
            for i, surface in enumerate(surfaces):
                self.surfaces.append(LandXMLSurface(surface, i * self.SURFACE_VERTEX_ID_OFFSET))

    @property
    def all_points(self) -> typing.List[MeshVertex]:
        """Returns points from all surfaces in the file."""
        points = []

        for surface in self.surfaces:
            points.extend(surface.points)

        return points

    @property
    def all_faces(self) -> typing.List[MeshFace]:
        """Returns faces from all surfaces in the file."""
        faces = []

        for surface in self.surfaces:
            faces.extend(surface.faces)

        return faces
