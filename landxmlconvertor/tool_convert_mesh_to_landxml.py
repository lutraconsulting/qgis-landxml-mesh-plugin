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
        return "convertmeshestolandxmlsurfaces"

    def displayName(self):
        return "Convert Meshes to LandXML Surfaces"

    def createInstance(self):
        return ConvertMesh2LandXML()

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(self.INPUT, "Input Mesh Layers", QgsProcessing.SourceType.TypeMesh)
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT, "Output LandXML File", fileFilter="XML File (*.xml)")
        )

    def checkParameterValues(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext
    ) -> typing.Tuple[bool, str]:
        crs = None

        mesh_layers = self.parameterAsLayerList(parameters, self.INPUT, context)

        for mesh_layer in mesh_layers:
            if crs is None:
                crs = mesh_layer.crs()
            if crs != mesh_layer.crs():
                return False, "All input Mesh Layers must have the same CRS."

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        mesh_layers = self.parameterAsLayerList(parameters, self.INPUT, context)

        xml_file = self.parameterAsString(parameters, self.OUTPUT, context)

        landxml_writer = LandXMLWriter(mesh_layers[0].crs())

        for mesh_layer in mesh_layers:
            if feedback.isCanceled():
                break

            feedback.pushCommandInfo(f"Processing layer: {mesh_layer.name()}")

            landxml_writer.add_surface(mesh_layer)

        landxml_writer.write(xml_file)

        return {self.OUTPUT: xml_file}
