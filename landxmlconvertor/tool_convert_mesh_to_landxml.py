import typing

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterMeshLayer,
    QgsProcessingParameterMultipleLayers,
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
        self.addParameter(
            QgsProcessingParameterMultipleLayers(self.INPUT, "Input Mesh Layers", QgsProcessing.SourceType.TypeMesh)
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT, "Output LandXML File", fileFilter="XML File (*.xml)")
        )

    def processAlgorithm(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        mesh_layers = self.parameterAsLayerList(parameters, self.INPUT, context)

        xml_file = self.parameterAsString(parameters, self.OUTPUT, context)

        landxml_writer = LandXMLWriter()

        for mesh_layer in mesh_layers:
            landxml_writer.add_surface(mesh_layer)

        landxml_writer.write(xml_file)

        return {self.OUTPUT: xml_file}
