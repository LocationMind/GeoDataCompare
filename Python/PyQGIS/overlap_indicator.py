"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       edit,
                       QgsFeatureSink,
                       QgsField,
                       QgsUnitTypes,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsProcessingException,
                       QgsProcessingParameterCrs,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import processing


class OverlapIndicator(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    INPUT = 'INPUT'
    INTERSECT = 'INTERSECT'
    BUFFERDIST = 'BUFFERDIST'
    TARGETEPSG = 'TARGETEPSG'
    OUTPUT = 'OUTPUT'
    PROPORTION = 'PROPORTION'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return OverlapIndicator()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'overlapindicator'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Overlap Indicator')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Quality criteria')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'qualitycriteria'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the 
        parameters and outputs associated with it..
        """
        return self.tr("""This algorithm calculate the proportion of road from dataset A that overlapped roads from dataset B.
        Copy of the layers are created to reproject them to EPSG:6691 by default (Japanese projection). This value can be changed in the parameter of the algorithm.
        The output layer is a copy of the input layer with a boolean attribute named 'overlap' that is true if the entity overlap the road, and false otherwise.
        It also return the proportion of road as a result (PROPORTION output).
        """)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Input layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input road layer'),
                [QgsProcessing.SourceType.VectorLine]
            )
        )
        
        # Intersect layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INTERSECT,
                self.tr('Intersect road layer'),
                [QgsProcessing.SourceType.VectorLine]
            )
        )
        
        # Buffer distance
        paramBufferDist = QgsProcessingParameterDistance(
            self.BUFFERDIST,
            self.tr('Buffer distance'),
            defaultValue = 1,
            minValue = 0
        )
        
        paramBufferDist.setDefaultUnit(QgsUnitTypes.DistanceMeters)
        self.addParameter(paramBufferDist)
        
        self.addParameter(
            QgsProcessingParameterCrs(
                self.TARGETEPSG,
                self.tr('Target EPSG for the process'),
                defaultValue = 'EPSG:6691'
            )
        )

        # Output layer
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """        
        ## Algorithm initialisation
        # Get the input parameter
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        intersect = self.parameterAsSource(
            parameters,
            self.INTERSECT,
            context
        )
        
        bufferDist = self.parameterAsDouble(
            parameters,
            self.BUFFERDIST,
            context
        )
        
        targetEPSG = self.parameterAsCrs(
            parameters,
            self.TARGETEPSG,
            context
        )
        
        # Exception if parameters are not found
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
            
        if intersect is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INTERSECTS))
        
        if bufferDist is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TARGETEPSG))
            
        if targetEPSG is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.BUFFERDIST))
        
        # Add a field to the source fields before creating the sink
        outputFields = source.fields()
        outputFields.append(QgsField('overlap', QVariant.Bool))
        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            outputFields,
            source.wkbType(),
            source.sourceCrs()
        )
        
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Send some information to the user
        feedback.pushInfo(f'CRS source is {source.sourceCrs().authid()}')
        
        feedback.pushInfo(f'CRS target is {targetEPSG.authid()}')
        
        ## Algorithm process 
        
        # Get the layer from the parameter
        sourceLayer = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        
        intersectLayer = self.parameterAsVectorLayer(
            parameters,
            self.INTERSECT,
            context
        )
        
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        ## Beginning of the algorithm
        # Reproject the layers
        sourceReprojected = processing.run("native:reprojectlayer", {
            'INPUT':sourceLayer,
            'TARGET_CRS':targetEPSG,
            'OUTPUT':'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        # Create overlap field for sourceReprojected layer
        sourceReprojected = processing.run("native:fieldcalculator", {
            'INPUT':sourceReprojected,
            'FIELD_NAME':'overlap',
            'FIELD_TYPE':6,
            'FIELD_LENGTH':0,
            'FIELD_PRECISION':0,
            'FORMULA':'True',
            'OUTPUT':'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        intersectReprojected = processing.run("native:reprojectlayer", {
            'INPUT':intersectLayer,
            'TARGET_CRS':targetEPSG,
            'OUTPUT':'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
            
        # Create spatial indexes
        feedback.pushInfo("Create spatial index for the projected layers")
        
        sourceReprojected.dataProvider().createSpatialIndex()
        feedback.pushInfo("Spatial index created for the projected source layer")
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        intersectReprojected.dataProvider().createSpatialIndex()
        feedback.pushInfo("Spatial index created for the projected intersect layer")
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        # Create the buffer
        feedback.pushInfo("Start buffer creation")
        
        bufferedLayer = processing.run("native:buffer", {
            'INPUT': intersectReprojected,
            'DISTANCE': bufferDist,
            'SEGMENTS': 5,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'DISSOLVE': True,
            'OUTPUT': 'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        bufferedLayer.dataProvider().createSpatialIndex()
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        feedback.pushInfo("Start selecting by location")
        
        # Select roads that overlaps the buffer (ie are within the buffer)
        sourceReprojected = processing.run("native:selectbylocation", {
            'INPUT':sourceReprojected,
            'PREDICATE':[6],
            'INTERSECT':bufferedLayer,
            'METHOD':0
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        # Because the two datasets are similar, we invert the selection to treat less features
        sourceReprojected.invertSelection()
        
        with edit(sourceReprojected):
            # Number of feature for the algorithm
            total = 100.0 / sourceReprojected.selectedFeatureCount() if sourceReprojected.selectedFeatureCount() else 0
            
            # Get overlap index
            idx = sourceReprojected.fields().indexFromName('overlap')
            
            for current, id in enumerate(sourceReprojected.selectedFeatureIds()):
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    feedback.pushWarning("Feedback cancelled")
                    return {}
                
                # Change the attribute value to false
                sourceReprojected.changeAttributeValue(id, idx, False)
                
                # Update the progress bar
                feedback.setProgress(int(current * total))
        
        
        feedback.pushInfo(f"Total features : {sourceReprojected.featureCount()}")
        feedback.pushInfo(f"Selected features : {sourceReprojected.selectedFeatureCount()}")
        
        sourceInitialCrs = processing.run("native:reprojectlayer", {
            'INPUT':sourceReprojected,
            'TARGET_CRS':source.sourceCrs(),
            'OUTPUT':'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        features = sourceInitialCrs.getFeatures()
        
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                feedback.pushWarning("Feedback cancelled")
                return {}
            
            # Add the feature to the sink
            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))
        
        ## Calculate proportion of roads covers
        
        # Geometry total length
        overlapLength = 0
        totalLength = 0
        
        # Add length attribute to the layer
        sourceReprojected = processing.run("native:fieldcalculator", {
            'INPUT':sourceReprojected,
            'FIELD_NAME':'length_bis',
            'FIELD_TYPE':0,
            'FIELD_LENGTH':0,
            'FIELD_PRECISION':0,
            'FORMULA':'length($geometry)',
            'OUTPUT':'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        # Calculate statistics on length depending on overlap attribute
        stats = processing.run("qgis:statisticsbycategories", {
            'INPUT':sourceReprojected,
            'VALUES_FIELD_NAME':'length_bis',
            'CATEGORIES_FIELD_NAME':['overlap'],
            'OUTPUT':'TEMPORARY_OUTPUT'
            }, context=context, feedback=feedback)['OUTPUT']
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        # Get attributes index
        idxOverlap = stats.fields().indexFromName('overlap')
        idxSum = stats.fields().indexFromName('sum')
        
        # Get sum values
        for feature in stats.getFeatures():
            feedback.pushInfo("overlap")
            feedback.pushInfo(str(feature[idxOverlap]))
            feedback.pushInfo("sum")
            feedback.pushInfo(str(feature[idxSum]))
            # Take the value of the length sum for overlapped roads
            if feature[idxOverlap] == True:
                overlapLength = feature[idxSum]
            
            # Calculate the total length
            totalLength += feature[idxSum]
        
        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            feedback.pushWarning("Feedback cancelled")
            return {}
        
        # Push length information to the user
        feedback.pushInfo(f"Length overlap : {overlapLength}")
        feedback.pushInfo(f"Total length : {totalLength}")
        
        # Calculate proporition of road overlapped
        proportion = overlapLength / totalLength
        feedback.pushInfo(f"Proportion : {proportion}")
        
        # Return the output id and the proportion as a result
        return {self.OUTPUT: dest_id, self.PROPORTION: proportion}
