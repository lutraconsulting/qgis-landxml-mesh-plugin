import re
import typing
import xml.etree.ElementTree as ET


def get_namespace(root_element: ET.Element) -> typing.Tuple[str, typing.Dict[str, str]]:
    """Extracts namespace based on root element of XML Document. Currently only LandXML 1.2 is supported.
    Returns namespace name and its definition to be used used find `ET.Element.find*()`."""
    namespace_name = ""

    namespace_landxml_element = re.match(r"\{(.+)\}", root_element.tag)

    if namespace_landxml_element:
        namespace_name = namespace_landxml_element.group(1)

    if namespace_name:
        if namespace_name == "http://www.landxml.org/schema/LandXML-1.2":
            # namespace for LandXML 1.2
            return ("LandXML-1.2", {"LandXML-1.2": "http://www.landxml.org/schema/LandXML-1.2"})
        else:
            raise ValueError(f"Unsupported namespace: `{namespace_name}`.")

    # if no schema is specified try using empty values - it might not be specifed in the XML
    return ("", {"": ""})
