import tempfile
from pathlib import Path

import pytest
from qgis.core import QgsCoordinateReferenceSystem, QgsMeshLayer

from landxmlconvertor.classes.landxml_reader import LandXMLReader
from landxmlconvertor.classes.landxml_writer import LandXMLWriter
from landxmlconvertor.classes.mesh2dm_writer import Mesh2DMWriter


@pytest.mark.parametrize(
    "filename",
    [
        ("Example_Clean.xml"),
        ("Example_Clean_without_schema.xml"),
    ],
)
def test_landxml_to_2dm(test_data_folder, filename):
    current_filename = test_data_folder / filename

    land_xml = LandXMLReader(current_filename.as_posix())

    mesh_2dm_writer = Mesh2DMWriter(land_xml.all_points, land_xml.all_faces)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_2dm_file = Path(tmpdir) / "file.2dm"

        mesh_2dm_writer.write(tmp_2dm_file.as_posix())

        mesh = QgsMeshLayer(tmp_2dm_file.as_posix(), "layer", "mdal")

        assert mesh.dataProvider().vertexCount() == 264
        assert mesh.dataProvider().faceCount() == 362


def test_2dm_to_landxml(test_data_folder):
    current_filename = test_data_folder / "mesh.2dm"

    mesh_2dm = QgsMeshLayer(current_filename.as_posix(), "layer", "mdal")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_landxml_file = Path(tmpdir) / "file.xml"

        landxml_writer = LandXMLWriter()
        landxml_writer.add_surface(mesh_2dm)
        landxml_writer.write(tmp_landxml_file.as_posix())

        landxml_reader = LandXMLReader(tmp_landxml_file.as_posix())

        assert landxml_reader.namespace_prefix == "LandXML-1.2:"
        assert landxml_reader.crs() == QgsCoordinateReferenceSystem()
        assert landxml_reader.surface_count == 1
        assert len(landxml_reader.all_faces) == 45
        assert len(landxml_reader.all_points) == 29
