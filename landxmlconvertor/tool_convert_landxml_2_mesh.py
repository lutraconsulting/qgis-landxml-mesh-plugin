import os
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
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
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
    UNION_SURFACES = "UNION_SURFACES"

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
        return "convertlandxmlsurfacestomeshes"

    def displayName(self):
        return "Convert LandXML Surfaces to Meshes"

    def createInstance(self):
        return ConvertLandXML2Mesh()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT, "Input LandXML File", extension="xml"))

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UNION_SURFACES,
                "Merge Surfaces into single Mesh (this should not be done if the surfaces overlap)",
                False,
            )
        )

        self.addParameter(QgsProcessingParameterEnum(self.MESH_FORMAT, "Output Format", self.driver_names, False, 0))

        self.addParameter(QgsProcessingParameterCrs(self.CRS, "Mesh CRS", optional=True))

        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT, "Output Folder for Mesh files"))

    def checkParameterValues(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext
    ) -> typing.Tuple[bool, str]:
        user_provided_crs = self.parameterAsCrs(parameters, self.CRS, context)

        landxml_file = self.parameterAsString(parameters, self.INPUT, context)

        try:
            land_xml = LandXMLReader(landxml_file)
        except ValueError:
            return False, "The provided file is not a valid LandXML file."

        if land_xml.surface_count == 0:
            return False, "No surfaces in the LandXML file. Nothing to extract."

        if all([x.empty() for x in land_xml.surfaces]):
            return False, "All surfaces in the LandXML file are empty."

        land_xml_crs = land_xml.crs()

        if user_provided_crs.isValid() and land_xml_crs.isValid():
            if user_provided_crs != land_xml_crs:
                return (
                    False,
                    f"User provided CRS `{user_provided_crs.authid()}` differs from LandXML specified CRS `{land_xml_crs.authid()}`.",
                )

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(
        self, parameters: typing.Dict[str, typing.Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        merge_surfaces = self.parameterAsBoolean(parameters, self.UNION_SURFACES, context)

        landxml_file = self.parameterAsString(parameters, self.INPUT, context)

        mesh_folder = self.parameterAsString(parameters, self.OUTPUT, context)

        mesh_crs = self.parameterAsCrs(parameters, self.CRS, context)

        driverIndex = self.parameterAsEnum(parameters, self.MESH_FORMAT, context)
        mesh_driver = self.driver_names[driverIndex]

        land_xml = LandXMLReader(landxml_file)

        land_xml_crs = land_xml.crs()

        # if user inputed CRS is not valid (empty CRS) use CRS from LandXML
        if land_xml_crs.isValid() and not mesh_crs.isValid():
            mesh_crs = land_xml_crs

        feedback.pushInfo(f"Using CRS: `{mesh_crs.authid()}`.")

        if merge_surfaces:
            name, _ = os.path.splitext(landxml_file)
            mesh_file = QgsFileUtils.ensureFileNameHasExtension(name, [self.driver_suffixes[driverIndex]])

            mesh_file = os.path.join(mesh_folder, mesh_file)

            tmp_2dm_file = QgsProcessingUtils.generateTempFilename(f"{uuid.uuid4()}.2dm")

            # create temp 2DM file and load it as layer

            mesh_2dm_writer = Mesh2DMWriter(land_xml.all_points, land_xml.all_faces)

            mesh_2dm_writer.write(tmp_2dm_file)

            feedback.pushInfo(f"Temp 2dm file saved: {tmp_2dm_file}")

            mesh_layer = QgsMeshLayer(tmp_2dm_file, "temp mesh layer", "mdal")

            # if output is 2DM format, just copy
            if mesh_driver == "2DM":
                dir_name = os.path.dirname(mesh_file)
                if not os.path.exists(dir_name):
                    os.mkdir(os.path.dirname(mesh_file))
                shutil.copy(tmp_2dm_file, mesh_file)
            # else extract mesh and create new using proper driver
            else:
                mesh = QgsMesh()
                mesh_layer.dataProvider().populateMesh(mesh)

                self.mdal_provider_meta.createMeshData(
                    mesh=mesh, fileName=mesh_file, driverName=mesh_driver, crs=mesh_crs
                )

            context.addLayerToLoadOnCompletion(
                mesh_file,
                QgsProcessingContext.LayerDetails(name, context.project(), name, QgsProcessingUtils.LayerHint.Mesh),
            )

        else:
            for surface in land_xml.surfaces:
                mesh_file = QgsFileUtils.ensureFileNameHasExtension(surface.name, [self.driver_suffixes[driverIndex]])

                mesh_file = os.path.join(mesh_folder, mesh_file)

                tmp_2dm_file = QgsProcessingUtils.generateTempFilename(f"{uuid.uuid4()}.2dm")

                # create temp 2DM file and load it as layer

                mesh_2dm_writer = Mesh2DMWriter(surface.points(), surface.faces())

                mesh_2dm_writer.write(tmp_2dm_file)

                feedback.pushInfo(f"Temp 2dm file saved: {tmp_2dm_file}")

                mesh_layer = QgsMeshLayer(tmp_2dm_file, "temp mesh layer", "mdal")

                # if output is 2DM format, just copy
                if mesh_driver == "2DM":
                    dir_name = os.path.dirname(mesh_file)
                    if not os.path.exists(dir_name):
                        os.mkdir(os.path.dirname(mesh_file))
                    shutil.copy(tmp_2dm_file, mesh_file)
                # else extract mesh and create new using proper driver
                else:
                    mesh = QgsMesh()
                    mesh_layer.dataProvider().populateMesh(mesh)

                    self.mdal_provider_meta.createMeshData(
                        mesh=mesh, fileName=mesh_file, driverName=mesh_driver, crs=mesh_crs
                    )

                context.addLayerToLoadOnCompletion(
                    mesh_file,
                    QgsProcessingContext.LayerDetails(
                        surface.name, context.project(), surface.name, QgsProcessingUtils.LayerHint.Mesh
                    ),
                )

        return {self.OUTPUT: mesh_folder}
