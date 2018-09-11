# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name: Layer Package Generator
# Purpose: Finds existing layers in a project, generates them if they are missing and their base exists, and then puts
# them into a layer package
#
# Author: Braden Anderson
# Created on: 14 June 2018
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import arcpy
import os
from SupportingFunctions import findFolder, findAvailableNum, makeFolder, makeLayer


def main(output_folder, layer_package_name):
    """
    Generates a layer package from a BRAT project
    :param output_folder: What output folder we want to use for our layer package
    :param layer_package_name: What we want to name our layer package
    :return:
    """
    projectFolder = os.path.dirname(output_folder)
    inputsFolder = findFolder(projectFolder, "Inputs")
    intermediatesFolder = os.path.join(output_folder, "01_Intermediates")
    analysesFolder = os.path.join(output_folder, "02_Analyses")

    tribCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(tribCodeFolder, 'BRATSymbology')

    checkForLayers(intermediatesFolder, analysesFolder, inputsFolder, symbologyFolder)

    makeLayerPackage(output_folder, intermediatesFolder, analysesFolder, inputsFolder, symbologyFolder, layer_package_name)


def checkForLayers(intermediatesFolder, analysesFolder, inputsFolder, symbologyFolder):
    """
    Checks for what layers exist, and creates them if they do not exist
    :param intermediatesFolder: Where our intermediates are kept
    :param analysesFolder: Where our analyses are kept
    :param inputsFolder: Where our inputs are kept
    :param symbologyFolder: Where we pull symbology from
    :return:
    """
    checkIntermediates(intermediatesFolder, symbologyFolder)
    checkAnalyses(analysesFolder, symbologyFolder)
    checkInputs(inputsFolder, symbologyFolder)


def checkIntermediates(intermediates_folder, symbologyFolder):
    """
    Checks for all the intermediate layers
    :param intermediates_folder: Where our intermediates are kept
    :param symbologyFolder: Where we pull symbology from
    :return:
    """
    brat_table_file = find_BRAT_table_output(intermediates_folder)
    if brat_table_file == "":
        arcpy.AddMessage("Could not find BRAT Table output in intermediates, so could not generate layers for them")
        return

    check_buffer_layers(intermediates_folder, symbologyFolder)

    check_intermediate_layer(intermediates_folder, symbologyFolder, "Drainage_Area_Feature_Class.lyr", brat_table_file, "TopographicMetrics", "Drainage Area", "iGeo_DA")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Slope_Feature_Class.lyr", brat_table_file, "TopographicMetrics", "Reach Slope", "iGeo_Slope")

    check_intermediate_layer(intermediates_folder, symbologyFolder, "Land_Use_Intensity.lyr", brat_table_file, "HumanBeaverConflict", "Land Use Intensity", "iPC_LU")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Canal", "iPC_Canal")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Closest Infrastructure", "oPC_Dist")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Railroad", "iPC_Rail")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Railroad in Valley Bottom", "iPC_RailVB")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Road Crossing", "iPC_RoadX")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Road", "iPC_Road")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Distance_To_Infrastructure.lyr", brat_table_file, "HumanBeaverConflict", "Distance to Road in Valley Bottom", "iPC_RoadVB")

    check_intermediate_layer(intermediates_folder, symbologyFolder, "Mainstems.lyr", brat_table_file, "AnabranchHandler", "Anabranch Type", "IsMainCh")

    check_intermediate_layer(intermediates_folder, symbologyFolder, "Highflow_StreamPower.lyr", brat_table_file, "Hydrology", "Highflow Stream Power", "iHyd_SP2")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Baseflow_StreamPower.lyr", brat_table_file, "Hydrology", "Baseflow Stream Power", "iHyd_SPLow")

    check_intermediate_layer(intermediates_folder, symbologyFolder, "Existing_Veg_Capacity.lyr", brat_table_file, "VegDamCapacity", "Existing Veg Dam Building Capacity", "oVC_EX")
    check_intermediate_layer(intermediates_folder, symbologyFolder, "Historic_Veg_Capacity.lyr", brat_table_file, "VegDamCapacity", "Historic Veg Dam Building Capacity", "oVC_PT")


def check_intermediate_layer(intermediates_folder, symbology_folder, symbology_layer_name, brat_table_file, folder_name,
                             layer_name, field_for_layer, layer_file_name=None):
    """

    :param intermediates_folder: The
    :param symbology_folder:
    :param symbology_layer_name:
    :param brat_table_file:
    :param folder_name:
    :param layer_name:
    :param field_for_layer:
    :param layer_file_name:
    :return:
    """
    fields = [f.name for f in arcpy.ListFields(brat_table_file)]
    if field_for_layer not in fields: # we don't want to create the layer if the field isn't in the BRAT table file
        return

    if layer_file_name == None:
        layer_file_name = layer_name.replace(" ", "")
    layer_symbology = os.path.join(symbology_folder, symbology_layer_name)

    layer_folder = findFolder(intermediates_folder, folder_name)

    if layer_folder == None:
        layer_folder = makeFolder(intermediates_folder, findAvailableNum(intermediates_folder) + "_" + folder_name)

    layer_path = os.path.join(layer_folder, layer_file_name)
    if not layer_path.endswith(".lyr"):
        layer_path += '.lyr'

    if not os.path.exists(layer_path):
        makeLayer(layer_folder, brat_table_file, layer_name, layer_symbology, fileName=layer_file_name)


def check_layer(layer_path, base_path, symbology_layer=None, isRaster=False, layer_name=None):
    """
    If the base exists, but the layer does not, makes the layer
    :param layer_path: The layer we want to check for
    :param base_path: The file that the layer is based off of
    :param symbology_layer: The symbology to apply to the new layer (if necessary)
    :param isRaster: If the new layer is a raster
    :return:
    """
    if not os.path.exists(layer_path) and os.path.exists(base_path):
        output_folder = os.path.dirname(layer_path)
        if layer_name is None:
            layer_name = os.path.basename(layer_path)
        makeLayer(output_folder, base_path, layer_name, symbology_layer, isRaster=isRaster)


def find_BRAT_table_output(intermediates_folder):
    """
    Finds the path to the BRAT Table output for use in generating layers
    :param intermediates_folder: Where the BRAT Table output should be
    :return:
    """
    brat_table_file = ""
    for dir in os.listdir(intermediates_folder):
        if dir.endswith(".shp"):
            brat_table_file = os.path.join(intermediates_folder, dir)

    return brat_table_file


def check_buffer_layers(intermediates_folder, symbology_folder):
    """
    Finds the buffer folder, and checks that it has the
    :param intermediates_folder:
    :param symbology_folder:
    :return:
    """
    buffer_folder = findFolder(intermediates_folder, "Buffers")

    buffer_100m = os.path.join(buffer_folder, "buffer_100m.shp")
    buffer_100m_layer = os.path.join(buffer_folder, "100mBuffer.lyr")
    buffer_100m_symbology = os.path.join(symbology_folder, "buffer_100m.lyr")
    check_layer(buffer_100m_layer, buffer_100m, buffer_100m_symbology, isRaster = False, layer_name = '100 m Buffer')

    buffer_30m = os.path.join(buffer_folder, "buffer_30m.shp")
    buffer_30m_layer = os.path.join(buffer_folder, "30mBuffer.lyr")
    buffer_30m_symbology = os.path.join(symbology_folder, "buffer_30m.lyr")
    check_layer(buffer_30m_layer, buffer_30m, buffer_30m_symbology, isRaster = False, layer_name = '30 m Buffer')


def checkAnalyses(analyses_folder, symbology_folder):
    """
    Checks for all the intermediate layers
    :param analyses_folder: Where our analyses are kept
    :param symbology_folder: Where we pull symbology from
    :return:
    """
    capacity_folder = findFolder(analyses_folder, "Capacity")
    historic_capacity_folder = findFolder(capacity_folder, "HistoricCapacity")
    existing_capacity_folder = findFolder(capacity_folder, "ExistingCapacity")
    management_folder = findFolder(analyses_folder, "Management")

    check_analyses_layer(analyses_folder, existing_capacity_folder, "Existing Dam Building Capacity", symbology_folder, "Existing_Capacity.lyr", "oCC_EX")
    check_analyses_layer(analyses_folder, historic_capacity_folder, "Historic Dam Building Capacity", symbology_folder, "Historic_Capacity.lyr", "oCC_PT")
    check_analyses_layer(analyses_folder, existing_capacity_folder, "Existing Dam Complex Size", symbology_folder, "Existing_Capacity_Count.lyr", "mCC_EX_Ct")
    check_analyses_layer(analyses_folder, historic_capacity_folder, "Historic Dam Complex Size", symbology_folder, "Historic_Capacity_Count.lyr", "mCC_PT_Ct")

    check_analyses_layer(analyses_folder, management_folder, "Beaver Management Zones", symbology_folder, "BeaverManagementZones.lyr", "oPBRC")
    check_analyses_layer(analyses_folder, management_folder, "Unsuitable or Limited Opportunities", symbology_folder, "Dam_Building_Not_Likely.lyr", "oPBRC")
    check_analyses_layer(analyses_folder, management_folder, "Restoration or Conservation Opportunities", symbology_folder, "Restoration_Conservation_Opportunities.lyr", "oPBRC")


def check_analyses_layer(analyses_folder, layer_base_folder, layer_name, symbology_folder, symbology_file_name, field_name, layer_file_name=None):
    """
    Checks if an analyses layer exists. If it does not, it looks for a shape file that can create the proper symbology.
    If it finds a proper shape file, it creates the layer that was missing
    :param analyses_folder: The root of the analyses folder
    :param layer_name: The name of the layer to create
    :param symbology_folder: The path to the symbology folder
    :param symbology_file_name: The name of the symbology layer we want to pull from
    :param field_name: The name of the field we'll be basing our symbology off of
    :param layer_file_name: The name of the layer file (if different from the layer_name without spaces)
    :return:
    """
    if layer_file_name is None:
        layer_file_name = layer_name.replace(" ", "") + ".lyr"

    layer_file = os.path.join(layer_base_folder, layer_file_name)
    if os.path.exists(layer_file): # if the layer already exists, we don't care, we can exit the function
        return

    shape_file = find_shape_file_with_field(analyses_folder, field_name)
    if shape_file is None:
        return

    layer_symbology = os.path.join(symbology_folder, symbology_file_name)

    makeLayer(layer_base_folder, shape_file, layer_name, symbology_layer=layer_symbology)



def find_shape_file_with_field(folder, field_name):
    for file in os.listdir(folder):
        if file.endswith(".shp"):
            file_path = os.path.join(folder, file)
            file_fields = [f.name for f in arcpy.ListFields(file_path)]
            if field_name in file_fields:
                return file_path
    return None


def checkInputs(inputsFolder, symbologyFolder):
    """
    Checks for all the intermediate layers
    :param inputsFolder: Where our inputs are kept
    :param symbologyFolder: Where we pull symbology from
    :return:
    """
    vegetationFolder = findFolder(inputsFolder, "Vegetation")
    networkFolder = findFolder(inputsFolder, "Network")
    topoFolder = findFolder(inputsFolder, "Topography")
    anthropogenicFolder = findFolder(inputsFolder, "Anthropogenic")

    exVegFolder = findFolder(vegetationFolder, "ExistingVegetation")
    histVegFolder = findFolder(vegetationFolder, "HistoricVegetation")

    valleyBottomFolder = findFolder(anthropogenicFolder, "ValleyBottom")
    roadFolder = findFolder(anthropogenicFolder, "Roads")
    railroadFolder = findFolder(anthropogenicFolder, "Railroads")
    canalsFolder = findFolder(anthropogenicFolder, "Canals")
    landUseFolder = findFolder(anthropogenicFolder, "LandUse")
    landOwnershipFolder = findFolder(anthropogenicFolder, "LandOwnership")

    exVegSuitabilitySymbology = os.path.join(symbologyFolder, "Existing_Veg_Suitability.lyr")
    exVegRiparianSymbology = os.path.join(symbologyFolder, "Existing_Veg_Riparian.lyr")
    exVegEVTTypeSymbology = os.path.join(symbologyFolder, "Existing_Veg_EVT_Type.lyr")
    exVegEVTClassSymbology = os.path.join(symbologyFolder, "Existing_Veg_EVT_Class.lyr")
    exVegClassNameSymbology = os.path.join(symbologyFolder, "Existing_Veg_ClassName.lyr")

    histVegGroupSymbology = os.path.join(symbologyFolder, "Historic_Veg_BPS_Type.lyr")
    histVegBPSNameSymbology = os.path.join(symbologyFolder, "Historic_Veg_BPS_Name.lyr")
    histVegSuitabilitySymbology = os.path.join(symbologyFolder, "Historic_Veg_Suitability.lyr")
    histVegRiparianSymbology = os.path.join(symbologyFolder, "Historic_Veg_Riparian.lyr")

    networkSymbology = os.path.join(symbologyFolder, "Network.lyr")
    landuseSymbology = os.path.join(symbologyFolder, "Land_Use_Raster.lyr")
    landOwnershipSymbology = os.path.join(symbologyFolder, "SurfaceManagementAgency.lyr")
    canalsSymbology = os.path.join(symbologyFolder, "Canals.lyr")
    roadsSymbology = os.path.join(symbologyFolder, "Roads.lyr")
    railroadsSymbology = os.path.join(symbologyFolder, "Railroads.lyr")
    valleyBottomSymbology = os.path.join(symbologyFolder, "ValleyBottom.lyr")
    valleyBottomOutlineSymbology = os.path.join(symbologyFolder, "ValleyBottom_Outline.lyr")
    flowDirectionSymbology = os.path.join(symbologyFolder, "Network_FlowDirection.lyr")

    exVegDestinations = findDestinations(exVegFolder)
    makeInputLayers(exVegDestinations, "Existing Vegetation Suitability for Beaver Dam Building", symbologyLayer=exVegSuitabilitySymbology, isRaster=True, fileName="ExVegSuitability")
    makeInputLayers(exVegDestinations, "Existing Riparian", symbologyLayer=exVegRiparianSymbology, isRaster=True)
    makeInputLayers(exVegDestinations, "Veg Type - EVT Type", symbologyLayer=exVegEVTTypeSymbology, isRaster=True)
    makeInputLayers(exVegDestinations, "Veg Type - EVT Class", symbologyLayer=exVegEVTClassSymbology, isRaster=True)
    makeInputLayers(exVegDestinations, "Veg Type - ClassName", symbologyLayer=exVegClassNameSymbology, isRaster=True)

    histVegDestinations = findDestinations(histVegFolder)
    makeInputLayers(histVegDestinations, "Historic Vegetation Suitability for Beaver Dam Building", symbologyLayer=histVegSuitabilitySymbology, isRaster=True)
    makeInputLayers(histVegDestinations, "Veg Type - BPS Type", symbologyLayer=histVegGroupSymbology, isRaster=True, checkField="GROUPVEG")
    makeInputLayers(histVegDestinations, "Veg Type - BPS Name", symbologyLayer=histVegBPSNameSymbology, isRaster=True)
    makeInputLayers(histVegDestinations, "Historic Riparian", symbologyLayer=histVegRiparianSymbology, isRaster=True, checkField="GROUPVEG")

    networkDestinations = findDestinations(networkFolder)
    makeInputLayers(networkDestinations, "Network", symbologyLayer=networkSymbology, isRaster=False)
    makeInputLayers(networkDestinations, "Flow Direction", symbologyLayer=flowDirectionSymbology, isRaster=False)

    makeTopoLayers(topoFolder)

    # add landuse raster to the project
    if landUseFolder is not None:
        landuseDestinations = findDestinations(landUseFolder)
        makeInputLayers(landuseDestinations, "Land Use Raster", symbologyLayer=landuseSymbology, isRaster=True)

    # add the conflict inputs to the project
    if valleyBottomFolder is not None:
        vallyBottomDestinations = findDestinations(valleyBottomFolder)
        makeInputLayers(vallyBottomDestinations, "Valley Bottom Fill", symbologyLayer=valleyBottomSymbology, isRaster=False)
        makeInputLayers(vallyBottomDestinations, "Valley Bottom Outline", symbologyLayer=valleyBottomOutlineSymbology, isRaster=False)

    # add road layers to the project
    if roadFolder is not None:
        roadDestinations = findDestinations(roadFolder)
        makeInputLayers(roadDestinations, "Roads", symbologyLayer=roadsSymbology, isRaster=False)

    # add railroad layers to the project
    if railroadFolder is not None:
        rrDestinations = findDestinations(railroadFolder)
        makeInputLayers(rrDestinations, "Railroads", symbologyLayer=railroadsSymbology, isRaster=False)

    # add canal layers to the project
    if canalsFolder is not None:
        canalDestinations = findDestinations(canalsFolder)
        makeInputLayers(canalDestinations, "Canals", symbologyLayer=canalsSymbology, isRaster=False)

    # add land ownership layers to the project
    if landOwnershipFolder is not None:
        ownershipDestinations = findDestinations(landOwnershipFolder)
        makeInputLayers(ownershipDestinations, "Land Ownership", symbologyLayer=landOwnershipSymbology, isRaster=False)


def makeTopoLayers(topoFolder):
    """
    Writes the layers
    :param topoFolder: We want to make layers for the stuff in this folder
    :return:
    """
    sourceCodeFolder = os.path.dirname(os.path.abspath(__file__))
    symbologyFolder = os.path.join(sourceCodeFolder, 'BRATSymbology')
    demSymbology = os.path.join(symbologyFolder, "DEM.lyr")
    slopeSymbology = os.path.join(symbologyFolder, "Slope.lyr")

    for folder in os.listdir(topoFolder):
        demFolderPath = os.path.join(topoFolder, folder)
        for fileName in os.listdir(demFolderPath):
            if fileName.endswith(".tif"):
                demFile = os.path.join(demFolderPath, fileName)
                if not os.path.exists(os.path.join(demFolderPath, "DEM.lyr")) and os.path.exists(demFile):
                    makeLayer(demFolderPath, demFile, "DEM", demSymbology, isRaster=True)

        hillshadeFolder = findFolder(demFolderPath, "Hillshade")
        hillshadeFile = os.path.join(hillshadeFolder, "Hillshade.tif")
        if not os.path.exists(os.path.join(hillshadeFolder, "Hillshade.lyr")) and os.path.exists(hillshadeFile):
            makeLayer(hillshadeFolder, hillshadeFile, "Hillshade", isRaster=True)

        slopeFolder = findFolder(demFolderPath, "Slope")
        slopeFile = os.path.join(slopeFolder, "Slope.tif")
        if not os.path.exists(os.path.join(slopeFolder, "Slope.lyr")) and os.path.exists(slopeFile):
            makeLayer(slopeFolder, slopeFile, "Slope", slopeSymbology, isRaster=True)


def findDestinations(root_folder):
    """
    Finds all the .shp and .tif files in a directory, and returns an array with the paths to them
    :param root_folder:
    :return:
    """
    destinations = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".shp") or file.endswith('.tif'):
                destinations.append(os.path.join(root, file))
    return destinations


def makeInputLayers(destinations, layerName, isRaster, symbologyLayer=None, fileName=None, checkField=None):
    """
    Makes the layers for everything in the folder
    :param destinations: A list of paths to our inputs
    :param layerName: The name of the layer
    :param isRaster: Whether or not it's a raster
    :param symbologyLayer: The base for the symbology
    :param fileName: The name for the file (if it's different from the layerName)
    :param checkField: The name of the field that the symbology is based on
    :return:
    """
    if fileName == None:
        fileName = layerName
    for destination in destinations:
        skip_loop = False
        destDirName = os.path.dirname(destination)

        if fileName is None:
            fileName = layerName.replace(" ", "")
        new_layer_save = os.path.join(destDirName, fileName.replace(' ', ''))
        if not new_layer_save.endswith(".lyr"):
            new_layer_save += ".lyr"
        if os.path.exists(new_layer_save):
            skip_loop = True
        if checkField:
            fields = [f.name for f in arcpy.ListFields(destination)]
            if checkField not in fields:
                # Skip the loop if the base doesn't support
                skip_loop = True

        if not skip_loop:
            makeLayer(destDirName, destination, layerName, symbology_layer=symbologyLayer, isRaster=isRaster, fileName=fileName)


def makeLayerPackage(output_folder, intermediatesFolder, analysesFolder, inputsFolder, symbologyFolder, layerPackageName):
    """
    Makes a layer package for the project
    :param output_folder: The folder that we want to base our layer package off of
    :param layerPackageName: The name of the layer package that we'll make
    :return:
    """
    if layerPackageName == "" or layerPackageName is None:
        layerPackageName = "LayerPackage"
    if not layerPackageName.endswith(".lpk"):
        layerPackageName += ".lpk"

    arcpy.AddMessage("Making Layer Package...")
    emptyGroupLayer = os.path.join(symbologyFolder, "EmptyGroupLayer.lyr")

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    analyses_layer = get_analyses_layer(analysesFolder, emptyGroupLayer, df, mxd)
    inputsLayer = getInputsLayer(emptyGroupLayer, inputsFolder, df, mxd)
    intermediatesLayer = getIntermediatesLayers(emptyGroupLayer, intermediatesFolder, df, mxd)
    outputLayer = groupLayers(emptyGroupLayer, "Output", [intermediatesLayer, analyses_layer], df, mxd)
    outputLayer = groupLayers(emptyGroupLayer, layerPackageName[:-4], [outputLayer, inputsLayer], df, mxd, removeLayer=False)

    layerPackage = os.path.join(output_folder, layerPackageName)
    arcpy.PackageLayer_management(outputLayer, layerPackage)


def get_analyses_layer(analyses_folder, empty_group_layer, df, mxd):
    """
    Returns the layers we want for the 'Output' section
    :param analyses_folder:
    :return:
    """
    capacity_folder = findFolder(analyses_folder, "Capacity")
    existing_capacity_folder = findFolder(capacity_folder, "ExistingCapacity")
    historic_capacity_folder = findFolder(capacity_folder, "HistoricCapacity")
    management_folder = findFolder(analyses_folder, "Management")

    existing_capacity_layers = findLayersInFolder(existing_capacity_folder)
    existing_capacity_layer = groupLayers(empty_group_layer, "Existing Capacity", existing_capacity_layers, df, mxd)
    historic_capacity_layers = findLayersInFolder(historic_capacity_folder)
    historic_capacity_layer = groupLayers(empty_group_layer, "Historic Capacity", historic_capacity_layers, df, mxd)
    management_layers = findLayersInFolder(management_folder)
    management_layer = groupLayers(empty_group_layer, "Management", management_layers, df, mxd)

    capacity_layer = groupLayers(empty_group_layer, "Capacity", [historic_capacity_layer, existing_capacity_layer], df, mxd)
    output_layer = groupLayers(empty_group_layer, "Beaver Restoration Assessment Tool - BRAT", [management_layer, capacity_layer], df, mxd)

    return output_layer



def getInputsLayer(emptyGroupLayer, inputsFolder, df, mxd):
    """
    Gets all the input layers, groups them properly, returns the layer
    :param emptyGroupLayer: The base to build the group layer with
    :param inputsFolder: Path to the inputs folder
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return: layer for inputs
    """
    vegetationFolder = findFolder(inputsFolder, "_Vegetation")
    exVegFolder = findFolder(vegetationFolder, "_ExistingVegetation")
    histVegFolder = findFolder(vegetationFolder, "_HistoricVegetation")

    networkFolder = findFolder(inputsFolder, "_Network")

    topoFolder = findFolder(inputsFolder, "_Topography")

    conflictFolder = findFolder(inputsFolder, "Anthropogenic")
    valleyFolder = findFolder(conflictFolder, "ValleyBottom")
    roadsFolder = findFolder(conflictFolder, "Roads")
    railroadsFolder = findFolder(conflictFolder, "Railroads")
    canalsFolder = findFolder(conflictFolder, "Canals")
    landUseFolder = findFolder(conflictFolder, "LandUse")

    exVegLayers = findInstanceLayers(exVegFolder)
    exVegLayer = groupLayers(emptyGroupLayer, "Existing Vegetation Dam Capacity", exVegLayers, df, mxd)
    histVegLayers = findInstanceLayers(histVegFolder)
    histVegLayer = groupLayers(emptyGroupLayer, "Historic Vegetation Dam Capacity", histVegLayers, df, mxd)
    vegLayer = groupLayers(emptyGroupLayer, "Vegetation", [histVegLayer, exVegLayer], df, mxd)

    networkLayers = findInstanceLayers(networkFolder)
    networkLayer = groupLayers(emptyGroupLayer, "Network", networkLayers, df, mxd)

    demLayers = findInstanceLayers(topoFolder)
    hillshadeLayers = find_dem_derivative(topoFolder, "Hillshade")
    slopeLayers = find_dem_derivative(topoFolder, "Slope")
    flowLayers = find_dem_derivative(topoFolder, "Flow")
    topoLayer = groupLayers(emptyGroupLayer, "Topography", hillshadeLayers + demLayers + slopeLayers + flowLayers, df, mxd)

    valleyLayers = findInstanceLayers(valleyFolder)
    valleyLayer = groupLayers(emptyGroupLayer, "Valley Bottom", valleyLayers, df, mxd)
    roadLayers = findInstanceLayers(roadsFolder)
    roadLayer = groupLayers(emptyGroupLayer, "Roads", roadLayers, df, mxd)
    railroadLayers = findInstanceLayers(railroadsFolder)
    railroadLayer = groupLayers(emptyGroupLayer, "Railroads", railroadLayers, df, mxd)
    canalLayers = findInstanceLayers(canalsFolder)
    canalLayer = groupLayers(emptyGroupLayer, "Canals", canalLayers, df, mxd)
    landUseLayers = findInstanceLayers(landUseFolder)
    landUseLayer = groupLayers(emptyGroupLayer, "Land Use", landUseLayers, df, mxd)
    conflictLayer = groupLayers(emptyGroupLayer, "Conflict Layers", [valleyLayer, roadLayer, railroadLayer, canalLayer, landUseLayer], df, mxd)

    return groupLayers(emptyGroupLayer, "Inputs", [topoLayer, vegLayer, networkLayer, conflictLayer], df, mxd)


def getIntermediatesLayers(emptyGroupLayer, intermediatesFolder, df, mxd):
    """
    Returns a group layer with all of the intermediates
    :param emptyGroupLayer: The base to build the group layer with
    :param intermediatesFolder: Path to the intermediates folder
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return: Layer for intermediates
    """
    intermediate_layers = []

    # findAndGroupLayers(intermediate_layers, intermediatesFolder, "HumanBeaverConflict", "Human Beaver Conflict", emptyGroupLayer, df, mxd)
    anthropogenic_metrics_folder = findFolder(intermediatesFolder, "AnthropogenicMetrics")
    if anthropogenic_metrics_folder:
        sorted_conflict_layers = []
        wanted_conflict_layers = []
        existing_conflict_layers = findLayersInFolder(anthropogenic_metrics_folder)

        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoCanal.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoRailroad.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoRailroadinValleyBottom.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoRoad.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoRoadCrossing.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoRoadinValleyBottom.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "DistancetoClosestInfrastructure.lyr"))
        wanted_conflict_layers.append(os.path.join(anthropogenic_metrics_folder, "LandUseIntensity.lyr"))


        for layer in wanted_conflict_layers:
            if layer in existing_conflict_layers:
                sorted_conflict_layers.append(layer)

        intermediate_layers.append(groupLayers(emptyGroupLayer, "Human Beaver Conflict", sorted_conflict_layers, df, mxd))

    findAndGroupLayers(intermediate_layers, intermediatesFolder, "VegDamCapacity", "Overall Vegetation Dam Capacity", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "Buffers", "Buffers", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "Hydrology", "Hydrology", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "AnabranchHandler", "Anabranch Handler", emptyGroupLayer, df, mxd)
    findAndGroupLayers(intermediate_layers, intermediatesFolder, "TopographicMetrics", "Topographic Index", emptyGroupLayer, df, mxd)

    # veg_folder_name = "VegDamCapacity"
    # veg_group_layer_name = "Overall Vegetation Dam Capacity"
    # veg_folder_path = findFolder(intermediatesFolder, veg_folder_name)
    # if veg_folder_path:
    #     veg_layers = findLayersInFolder(veg_folder_path)
    #     if len(veg_layers) == 2:
    #         desc = arcpy.Describe(veg_layers[0])
    #         if "Existing" in desc.nameString:
    #             veg_layers = [veg_layers[1], veg_layers[0]]
    #
    #     intermediate_layers.append(groupLayers(emptyGroupLayer, veg_group_layer_name, veg_layers, df, mxd))

    return groupLayers(emptyGroupLayer, "Intermediates", intermediate_layers, df, mxd)


def findAndGroupLayers(layers_list, folderBase, folderName, groupLayerName, emptyGroupLayer, df, mxd):
    """
    Looks for the folder that matches what we're looking for, then groups them together. Adds that grouped layer to the
    list of grouped layers that it was given
    :param layers_list: The list of layers that we will add our grouped layer to
    :param folderBase: Path to the folder that contains the folder we want
    :param folderName: The name of the folder to look in
    :param groupLayerName: What we want to name the group layer
    :param emptyGroupLayer: The base to build the group layer with
    :param df: The dataframe we're working with
    :param mxd: The map document we're working with
    :return:
    """
    folderPath = findFolder(folderBase, folderName)
    if folderPath:
        layers = findLayersInFolder(folderPath)

        layers_list.append(groupLayers(emptyGroupLayer, groupLayerName, layers, df, mxd))


def findInstanceLayers(root_folder):
    """
    Finds every layer when buried beneath an additional layer of folders (ie, in DEM_1, DEM_2, DEM_3, etc)
    :param root_folder: The path to the folder root
    :return: A list of layers
    """
    layers = []
    for instance_folder in os.listdir(root_folder):
        instance_folder_path = os.path.join(root_folder, instance_folder)
        layers += findLayersInFolder(instance_folder_path)
    return layers


def find_dem_derivative(root_folder, dir_name):
    """
    Designed to look specifically for flow, slope, and hillshade layers
    :param root_folder: Where we look
    :param dir_name: The directory we're looking for
    :return:
    """
    layers = []
    for instance_folder in os.listdir(root_folder):
        instance_folder_path = os.path.join(os.path.join(root_folder, instance_folder), dir_name)
        layers += findLayersInFolder(instance_folder_path)
    return layers


def findLayersInFolder(folder_root):
    """
    Returns a list of all layers in a folder
    :param folder_root: Where we want to look
    :return:
    """
    layers = []
    for instance_file in os.listdir(folder_root):
        if instance_file.endswith(".lyr"):
            layers.append(os.path.join(folder_root, instance_file))
    return layers



def groupLayers(groupLayer, groupName, layers, df, mxd, removeLayer=True):
    """
    Groups a bunch of layers together
    :param groupLayer:
    :param groupName:
    :param layers:
    :param df:
    :param mxd:
    :param removeLayer: Tells us if we should remove the layer from the map display
    :return: The layer that we put our layers in
    """
    groupLayer = arcpy.mapping.Layer(groupLayer)
    groupLayer.name = groupName
    groupLayer.description = "Made Up Description"
    arcpy.mapping.AddLayer(df, groupLayer, "BOTTOM")
    groupLayer = arcpy.mapping.ListLayers(mxd, groupName, df)[0]

    for layer in layers:
        if not isinstance(layer, arcpy.mapping.Layer):
            layer_instance = arcpy.mapping.Layer(layer)
        else:
            layer_instance = layer
        arcpy.mapping.AddLayerToGroup(df, groupLayer, layer_instance)

    if removeLayer:
        arcpy.mapping.RemoveLayer(df, groupLayer)

    return groupLayer

