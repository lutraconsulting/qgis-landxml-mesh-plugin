from .plugin import LandXMLConvertorPlugin


# noinspection PyPep8Naming
def classFactory(iface):
    return LandXMLConvertorPlugin(iface)
