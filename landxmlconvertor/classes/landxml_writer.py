import datetime
import typing
import xml.etree.ElementTree as ET

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsUnitTypes

from ..text_constants import TextConstants
from ..utils import plugin_author, plugin_repository_url, plugin_version
from .mesh_elements import MeshFace, MeshVertex
from .xml_formatter import XmlFormatter


class LandXMLWriter:
    """Class for writing the LandXML format from mesh vericies and faces."""

    def __init__(
        self,
        points: typing.List[MeshVertex],
        faces: typing.List[MeshFace],
        crs: QgsCoordinateReferenceSystem = QgsCoordinateReferenceSystem(),
    ) -> None:
        self.points = points
        self.faces = faces

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
        self.root_element.append(self.create_surfaces())

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

    def create_surfaces(self) -> ET.Element:
        elem = ET.Element("Surfaces")

        elem.append(self.create_surface())

        return elem

    def create_surface(self) -> ET.Element:
        elem_surface = ET.Element("Surface", attrib={"name": "A"})

        elem_definition = ET.Element("Definition", attrib={"surfType": "TIN"})
        elem_surface.append(elem_definition)

        elem_pnts = ET.Element("Pnts")
        elem_definition.append(elem_pnts)

        for point in self.points:
            elem_pnts.append(point.as_landxml_element())

        elem_faces = ET.Element("Faces")
        elem_definition.append(elem_faces)

        for face in self.faces:
            elem_faces.append(face.as_landxml_element())

        return elem_surface

    def write(self, file_name: str) -> None:
        text = XmlFormatter.elementToPrettyXml(self.LandXML)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(text.decode("utf-8"))
