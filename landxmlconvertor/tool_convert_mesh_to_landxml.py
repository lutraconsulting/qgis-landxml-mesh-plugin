import typing
import uuid

from qgis.core import (
    QgsMesh,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterMeshLayer,
    QgsProcessingUtils,
    QgsProviderRegistry,
)

from .classes.landxml_writer import LandXMLWriter
from .classes.mesh2dm_reader import Mesh2DMReader


class ConvertMesh2LandXML(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    mdal_provider_meta = QgsProviderRegistry.instance().providerMetadata("mdal")

    def name(self):
        return "convertmeshtolandxmlsurfaces"

    def displayName(self):
        return "Convert Mesh to LandXML Surfaces"

    def createInstance(self):
        return ConvertMesh2LandXML()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMeshLayer(self.INPUT, "Input Mesh Layer"))

        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT, "Output LandXML File", fileFilter="XML File (*.xml)")
        )

    def processAlgorithm(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        mesh_layer = self.parameterAsMeshLayer(parameters, self.INPUT, context)

        xml_file = self.parameterAsString(parameters, self.OUTPUT, context)

        tmp_2dm_file = QgsProcessingUtils.generateTempFilename(f"{uuid.uuid4()}.2dm")

        # create temp 2D file
        mesh = QgsMesh()
        mesh_layer.dataProvider().populateMesh(mesh)

        self.mdal_provider_meta.createMeshData(mesh=mesh, fileName=tmp_2dm_file, driverName="2DM", crs=mesh_layer.crs())

        # read the file to format, that holds points and faces
        mesh_2dm_reader = Mesh2DMReader(tmp_2dm_file)

        # write the points and faces and LandXML
        landxml_writer = LandXMLWriter(mesh_2dm_reader.points, mesh_2dm_reader.faces)
        landxml_writer.write(xml_file)

        return {self.OUTPUT: xml_file}
