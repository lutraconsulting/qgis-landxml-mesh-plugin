import xml.etree.ElementTree as ET

import pytest
from qgis.core import QgsCoordinateReferenceSystem

from landxmlconvertor.classes.landxml_elements import LandXMLSurface
from landxmlconvertor.classes.landxml_reader import LandXMLReader
from landxmlconvertor.classes.mesh_elements import MeshFace, MeshVertex


@pytest.mark.parametrize(
    "filename",
    [
        ("Example_Clean.xml"),
        ("Example_Clean_without_schema.xml"),
    ],
)
def test_clean_data(test_data_folder, filename):
    current_filename = test_data_folder / filename

    land_xml = LandXMLReader(current_filename.as_posix())

    assert land_xml.path == current_filename.as_posix()
    assert isinstance(land_xml.xml_tree, ET.ElementTree)

    assert isinstance(land_xml.xml_root, ET.Element)
    assert "LandXML" in land_xml.xml_root.tag

    assert land_xml.crs() == QgsCoordinateReferenceSystem()

    assert land_xml.surface_count == 3

    assert all([isinstance(x, LandXMLSurface) for x in land_xml.surfaces])

    assert len(land_xml.get_surface_points(0)) == 29
    assert len(land_xml.get_surface_faces(0)) == 45

    assert len(land_xml.get_surface_points(1)) == 92
    assert len(land_xml.get_surface_faces(1)) == 138

    assert len(land_xml.get_surface_points(2)) == 143
    assert len(land_xml.get_surface_faces(2)) == 179

    assert all([isinstance(x, MeshVertex) for x in land_xml.get_surface_points(0)])
    assert all([isinstance(x, MeshFace) for x in land_xml.get_surface_faces(0)])

    assert len(land_xml.all_points) == 29 + 92 + 143
    assert len(land_xml.all_faces) == 45 + 138 + 179


def test_non_existing_file():
    with pytest.raises(FileNotFoundError, match="No such file"):
        LandXMLReader("file_that_does_not_exist.xml")


def test_non_LandXML_file(test_data_folder):
    filename = test_data_folder / "just_xml.xml"
    with pytest.raises(ValueError, match="Not a valid LandXML file"):
        LandXMLReader(filename.as_posix())


def test_LandXML_without_surface_1(test_data_folder):
    filename = test_data_folder / "land_xml_no_surface.xml"

    land_xml = LandXMLReader(filename.as_posix())

    assert land_xml.surface_count == 0


def test_LandXML_without_surface_2(test_data_folder):
    filename = test_data_folder / "land_xml_empty_surface.xml"

    land_xml = LandXMLReader(filename.as_posix())

    assert land_xml.surface_count == 1
    assert land_xml.surfaces[0].empty()


def test_LandXML_unsupported_schema(test_data_folder):
    filename = test_data_folder / "land_xml_with_unsupported_schema.xml"

    with pytest.raises(ValueError, match="Unsupported namespace: "):
        LandXMLReader(filename.as_posix())


def test_data_1(test_data_folder):
    filename = test_data_folder / "Total topp.xml"

    landxml_reader = LandXMLReader(filename.as_posix())

    assert landxml_reader.crs() == QgsCoordinateReferenceSystem()
    assert landxml_reader.surface_count == 1
    assert len(landxml_reader.all_faces) == 36093
    assert len(landxml_reader.all_points) == 22273


def test_data_2(test_data_folder):
    filename = test_data_folder / "3D_modell_underlag_skyfall_20230915.xml"

    landxml_reader = LandXMLReader(filename.as_posix())

    assert landxml_reader.crs() == QgsCoordinateReferenceSystem("EPSG:3007")
    assert landxml_reader.surface_count == 1
    assert len(landxml_reader.all_faces) == 6448
    assert len(landxml_reader.all_points) == 3330
