import re
import typing
import xml.etree.ElementTree as ET


class MeshVertex:
    """Mesh Vertext that has x, y and z coordinate and unique id."""

    def __init__(self, vertex_id: int, x: float, y: float, z: float = 0):
        self.id = vertex_id
        self.x = x
        self.y = y
        self.z = z

    def as_2dm_element(self) -> str:
        """Convert to 2DM format of vertex."""
        return f"ND {self.id} {self.x} {self.y} {self.z}"

    def as_landxml_element(self) -> ET.Element:
        """Convert to LandXML format of vertex."""
        elem = ET.Element("P", attrib={"id": str(self.id)})
        elem.text = f"{self.y} {self.x} {self.z}"
        return elem

    @classmethod
    def from_xml_element(cls, element: ET.Element):
        """Read from LandXML element."""

        vertex_id = int(element.attrib["id"])

        y, x, z = element.text.split(" ")

        x = float(x)
        y = float(y)
        z = float(z)

        return cls(vertex_id, x, y, z)

    @classmethod
    def from_2dm_line(cls, line: str):
        """Read from 2DM line."""
        elements = re.split(r"\s", line)
        return cls(int(elements[1]), float(elements[2]), float(elements[3]), float(elements[4]))


class MeshFace:
    """Mesh face that is defined by unique id and list of ids of mesh verticies."""

    def __init__(self, face_id: int, points_ids: typing.List[int]) -> None:
        self.id = face_id
        self.points_ids = points_ids

    def as_2dm_element(self) -> str:
        """Convert to 2DM format of face."""
        if len(self.points_ids) == 3:
            return f"E3T {self.id} {self.points_ids[0]} {self.points_ids[1]} {self.points_ids[2]} 1"

        elif len(self.points_ids) == 4:
            return (
                f"E4Q {self.id} {self.points_ids[0]} {self.points_ids[1]} {self.points_ids[2]} {self.points_ids[3]} 1"
            )

        return ""

    def as_landxml_element(self) -> ET.Element:
        """Convert to LandXML format."""
        elem = ET.Element("F")
        vertex_ids = " ".join([str(x) for x in self.points_ids])
        elem.text = f"{vertex_ids}"
        return elem

    @classmethod
    def from_xml_element(cls, face_id: int, face_element: ET.Element):
        """Read from LandXML element."""

        face_id = face_id
        points_ids_text = face_element.text.split(" ")

        point_ids: typing.List[int] = []

        for point_id in points_ids_text:
            point_ids.append(int(point_id))

        return cls(face_id, point_ids)

    @classmethod
    def from_2dm_line(cls, line: str):
        """Read from 2DM line."""
        elements = re.split(r"\s", line)

        if line.startswith("E3T"):
            return cls(int(elements[1]), [int(elements[2]), int(elements[3]), int(elements[4])])
        elif line.startswith("E4Q"):
            return cls(int(elements[1]), [int(elements[2]), int(elements[3]), int(elements[4]), int(elements[5])])
