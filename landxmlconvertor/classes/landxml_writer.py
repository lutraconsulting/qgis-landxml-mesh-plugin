import datetime
import typing
import xml.etree.ElementTree as ET

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsMesh,
    QgsMeshLayer,
    QgsProcessingUtils,
    QgsProviderRegistry,
    QgsUnitTypes,
)

from ..text_constants import TextConstants
from ..utils import plugin_author, plugin_repository_url, plugin_version
from . import NS
from .mesh2dm_reader import Mesh2DMReader
from .mesh_elements import MeshFace, MeshVertex
from .xml_formatter import XmlFormatter


class LandXMLWriter:
    """Class for writing the LandXML format from mesh vericies and faces."""

    def __init__(
        self,
        crs: QgsCoordinateReferenceSystem = QgsCoordinateReferenceSystem(),
    ) -> None:
        self.crs = crs

        self.root_element = ET.Element(
            "LandXML",
            attrib={
                "xmlns": "http://www.landxml.org/schema/LandXML-1.2",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://www.landxml.org/schema/LandXML-1.2 http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd",
                "version": "1.2",
                "language": "English",
                "readOnly": "false",
                "date": str(datetime.date.today()),
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
        )

        self.units = ET.SubElement(self.root_element, "Units")
        self.units.append(self.create_unit())
        self.root_element.append(self.create_application())
        self.surfaces_elem = ET.Element("Surfaces")
        self.root_element.append(self.surfaces_elem)

    @property
    def LandXML(self) -> ET.Element:
        return self.root_element

    def create_unit(self) -> ET.Element:
        unit_type = "Metric"
        attr = {}

        if self.crs.isValid():
            distance_unit = self.crs.mapUnits()

            if distance_unit != Qgis.DistanceUnit.Unknown:
                if distance_unit in [
                    Qgis.DistanceUnit.Feet,
                    Qgis.DistanceUnit.Inches,
                    Qgis.DistanceUnit.Miles,
                    Qgis.DistanceUnit.NauticalMiles,
                    Qgis.DistanceUnit.Yards,
                ]:
                    unit_type = "Imperial"

                attr = {
                    "linearUnit": QgsUnitTypes.encodeUnit(distance_unit),
                    "areaUnit": QgsUnitTypes.encodeUnit(QgsUnitTypes.distanceToAreaUnit(distance_unit)),
                    "volumeUnit": QgsUnitTypes.encodeUnit(QgsUnitTypes.distanceToVolumeUnit(distance_unit)),
                    "diameterUnit": "millimeter",
                    "angularUnit": "decimal degrees",
                    "directionUnit": QgsUnitTypes.encodeUnit(distance_unit),
                }

        return ET.Element(unit_type, attrib=attr)

    def create_application(self) -> ET.Element:
        attr = {
            "name": "QGIS",
            "desc": f"QGIS `{TextConstants.PLUGIN_NAME}` plugin",
            "manufacturer": plugin_author(),
            "version": plugin_version(),
            "manufacturerURL": plugin_repository_url(),
            "timeStamp": "",
        }

        return ET.Element("Application", attrib=attr)

    def _create_surface(self, name: str, points: typing.List[MeshVertex], faces: typing.List[MeshFace]) -> ET.Element:
        elem_surface = ET.Element("Surface", attrib={"name": name})

        elem_definition = ET.Element("Definition", attrib={"surfType": "TIN"})
        elem_surface.append(elem_definition)

        elem_pnts = ET.Element("Pnts")
        elem_definition.append(elem_pnts)

        for point in points:
            elem_pnts.append(point.as_landxml_element())

        elem_faces = ET.Element("Faces")
        elem_definition.append(elem_faces)

        for face in faces:
            elem_faces.append(face.as_landxml_element())

        return elem_surface

    def write(self, file_name: str) -> None:
        text = XmlFormatter.elementToPrettyXml(self.LandXML)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(text.decode("utf-8"))

    def add_surface(self, mesh_layer: QgsMeshLayer) -> None:
        mdal_provider_meta = QgsProviderRegistry.instance().providerMetadata("mdal")

        tmp_2dm_file = QgsProcessingUtils.generateTempFilename(f"{mesh_layer.id()}.2dm")

        # create temp 2D file
        mesh = QgsMesh()
        mesh_layer.dataProvider().populateMesh(mesh)

        mdal_provider_meta.createMeshData(mesh=mesh, fileName=tmp_2dm_file, driverName="2DM", crs=mesh_layer.crs())

        # read the file to format, that holds points and faces
        mesh_2dm_reader = Mesh2DMReader(tmp_2dm_file)

        elem_surface = self._create_surface(mesh_layer.name(), mesh_2dm_reader.points, mesh_2dm_reader.faces)

        self.surfaces_elem.append(elem_surface)
