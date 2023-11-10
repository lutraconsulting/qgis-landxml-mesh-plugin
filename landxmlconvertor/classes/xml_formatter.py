import xml.etree.ElementTree as ET
from xml.dom import minidom


class XmlFormatter:
    """Class for formatting XML."""

    @staticmethod
    def elementToDocument(element: ET.Element) -> minidom.Document:
        xml_string = ET.tostring(element, short_empty_elements=False)

        return minidom.parseString(xml_string)

    @staticmethod
    def elementToPrettyXml(element: ET.Element, indent: str = "    ") -> bytes:
        document = XmlFormatter.elementToDocument(element)

        text_pretiffied = document.toprettyxml(indent=indent, encoding="utf-8")

        return text_pretiffied
