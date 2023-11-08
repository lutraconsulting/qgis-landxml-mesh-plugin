from qgis.core import QgsProcessingProvider

from .text_constants import TextConstants
from .tool_convert_landxml_2_mesh import ConvertLandXML2Mesh
from .tool_convert_mesh_to_landxml import ConvertMesh2LandXML


class LandXMLConvertorProvider(QgsProcessingProvider):
    def load(self) -> bool:
        self.refreshAlgorithms()

        return True

    def loadAlgorithms(self):
        self.addAlgorithm(ConvertLandXML2Mesh())
        self.addAlgorithm(ConvertMesh2LandXML())

    def id(self):
        return TextConstants.PLUGIN_PROVIDER_ID

    def name(self):
        return TextConstants.PLUGIN_PROVIDER_NAME

    def longName(self):
        return self.name()
