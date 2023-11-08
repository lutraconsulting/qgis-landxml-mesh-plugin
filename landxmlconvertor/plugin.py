from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .provider_landxmlplugin import LandXMLConvertorProvider


class LandXMLConvertorPlugin:
    def __init__(self, iface):
        self.iface: QgisInterface = iface

        self.provider = LandXMLConvertorProvider()

    def initProcessing(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
