import typing
import xml.etree.ElementTree as ET

from qgis.core import QgsCoordinateReferenceSystem

from . import get_namespace
from .landxml_elements import LandXMLSurface
from .mesh_elements import MeshFace, MeshVertex


# http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd
class LandXMLReader:
    """Class for reading the LandXML file, store individual surfaces."""

    # different surfaces may use same vertex ids, we need to differentiate so surfaces are offset from each other by this value
    SURFACE_VERTEX_ID_OFFSET = 10_000

    def __init__(self, path: str):
        self.path = path

        self.xml_tree = ET.parse(self.path)

        if not "LandXML".lower() in self.xml_root.tag.lower():
            raise ValueError("Not a valid LandXML file.")

        namespace_name, self.namespace = get_namespace(self.xml_root)
        self.namespace_prefix = ""
        if namespace_name:
            self.namespace_prefix = f"{namespace_name}:"

        self.surfaces: typing.List[LandXMLSurface] = []
        self._get_surfaces()

    def crs(self) -> QgsCoordinateReferenceSystem:
        crs_element = self.xml_root.find(f"{self.namespace_prefix}CoordinateSystem", namespaces=self.namespace)

        crs = QgsCoordinateReferenceSystem()

        if isinstance(crs_element, ET.Element):
            attrs = crs_element.attrib
            if "epsgCode" in attrs.keys():
                crs = QgsCoordinateReferenceSystem(f"EPSG:{attrs['epsgCode']}")
            if "ogcWktCode" in attrs.keys():
                crs.fromWkt(attrs["ogcWktCode"])

        return crs

    @property
    def xml_root(self) -> ET.Element:
        return self.xml_tree.getroot()

    @property
    def surface_count(self) -> int:
        return len(self.surfaces)

    def get_surface_points(self, surface_number: int) -> typing.List[MeshVertex]:
        return self.surfaces[surface_number].points()

    def get_surface_faces(self, surface_number: int) -> typing.List[MeshFace]:
        return self.surfaces[surface_number].faces()

    def _get_surfaces(self) -> None:
        surfaces = self.xml_root.find(f"{self.namespace_prefix}Surfaces", namespaces=self.namespace)
        if surfaces:
            for i, surface in enumerate(surfaces):
                self.surfaces.append(
                    LandXMLSurface(surface, i, i * self.SURFACE_VERTEX_ID_OFFSET, self.namespace_prefix, self.namespace)
                )

    @property
    def all_points(self) -> typing.List[MeshVertex]:
        """Returns points from all surfaces in the file."""
        points = []

        for surface in self.surfaces:
            points.extend(surface.points(True))

        return points

    @property
    def all_faces(self) -> typing.List[MeshFace]:
        """Returns faces from all surfaces in the file."""
        faces = []

        for surface in self.surfaces:
            faces.extend(surface.faces(True))

        return faces
