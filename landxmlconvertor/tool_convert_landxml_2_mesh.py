import shutil
import typing
import uuid

from qgis.core import (
    QgsFileUtils,
    QgsMesh,
    QgsMeshDriverMetadata,
    QgsMeshLayer,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingUtils,
    QgsProviderRegistry,
)

from .classes.landxml_reader import LandXMLReader
from .classes.mesh2dm_writer import Mesh2DMWriter


class ConvertLandXML2Mesh(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    MESH_FORMAT = "MESH_FORMAT"
    CRS = "CRS"

    mdal_provider_meta = QgsProviderRegistry.instance().providerMetadata("mdal")

    driver_names = []
    driver_suffixes = []

    for driver in mdal_provider_meta.meshDriversMetadata():
        if driver.capabilities() & QgsMeshDriverMetadata.MeshDriverCapability.CanWriteMeshData:
            if driver.name() == "SELAFIN":
                continue
            driver_names.append(driver.name())
            driver_suffixes.append(driver.writeMeshFrameOnFileSuffix())

    def name(self):
        return "convertlandxmlsurfacestomesh"

    def displayName(self):
        return "Convert LandXML Surfaces to Mesh"

    def createInstance(self):
        return ConvertLandXML2Mesh()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT, "Input LandXML File", extension="xml"))

        self.addParameter(QgsProcessingParameterEnum(self.MESH_FORMAT, "Output Format", self.driver_names, False, 0))

        self.addParameter(QgsProcessingParameterCrs(self.CRS, "Mesh CRS"))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT, "Output Mesh File"))

    def processAlgorithm(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        landxml_file = self.parameterAsString(parameters, self.INPUT, context)

        mesh_file = self.parameterAsString(parameters, self.OUTPUT, context)

        mesh_crs = self.parameterAsCrs(parameters, self.CRS, context)

        driverIndex = self.parameterAsEnum(parameters, self.MESH_FORMAT, context)
        mesh_driver = self.driver_names[driverIndex]

        mesh_file = QgsFileUtils.ensureFileNameHasExtension(mesh_file, [self.driver_suffixes[driverIndex]])

        tmp_2dm_file = QgsProcessingUtils.generateTempFilename(f"{uuid.uuid4()}.2dm")

        # create temp 2DM file and load it as layer
        land_xml = LandXMLReader(landxml_file)

        mesh_2dm_writer = Mesh2DMWriter(land_xml.all_points, land_xml.all_faces)

        mesh_2dm_writer.write(tmp_2dm_file)

        feedback.pushInfo(f"Temp 2dm file saved: {tmp_2dm_file}")

        mesh_layer = QgsMeshLayer(tmp_2dm_file, "temp mesh layer", "mdal")

        # if output is 2DM format, just copy
        if mesh_driver == "2DM":
            shutil.copy(tmp_2dm_file, mesh_file)
        # else extract mesh and create new using proper driver
        else:
            mesh = QgsMesh()
            mesh_layer.dataProvider().populateMesh(mesh)

            self.mdal_provider_meta.createMeshData(mesh=mesh, fileName=mesh_file, driverName=mesh_driver, crs=mesh_crs)

        context.addLayerToLoadOnCompletion(
            mesh_file,
            QgsProcessingContext.LayerDetails(
                "LandXML Mesh", context.project(), "LandXML", QgsProcessingUtils.LayerHint.Mesh
            ),
        )

        return {self.OUTPUT: mesh_file}
