import datetime
import typing
import xml.etree.ElementTree as ET

from .mesh_elements import MeshFace, MeshVertex
from .xml_formatter import XmlFormatter


class LandXMLWriter:
    """Class for writing the LandXML format from mesh vericies and faces."""

    def __init__(self, points: typing.List[MeshVertex], faces: typing.List[MeshFace]) -> None:
        self.points = points
        self.faces = faces

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
        atrr = {
            "areaUnit": "squareMeter",
            "linearUnit": "meter",
            "volumeUnit": "cubicMeter",
            "temperatureUnit": "celsius",
            "pressureUnit": "milliBars",
            "diameterUnit": "millimeter",
            "angularUnit": "decimal degrees",
            "directionUnit": "decimal degrees",
        }

        return ET.Element("Metric", attrib=atrr)

    def create_application(self) -> ET.Element:
        attr = {
            "name": "Autodesk Civil 3D",
            "desc": "Civil 3D",
            "manufacturer": "Autodesk, Inc.",
            "version": "2023",
            "manufacturerURL": "www.autodesk.com/civil",
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
