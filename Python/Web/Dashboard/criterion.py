import os
import sys
import geopandas as gpd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import theme as t
import lonboard
from abc import ABC, abstractmethod
import sqlalchemy
from htmltools import Tag
import faicons as fa

class Criterion(ABC):
    """Represents a criterion.

    Attributes:
        theme:theme.Theme
        osmLayer:str
        omfLayer:str
        osmOtherLayers:list
        omfOtherLayers:list
        columnCriterion:str
        layerType:lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer
        otherLayersType: list[lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer]
        displayName:str
    """
    
    area:str
    areaKm2:float
    crs:int
    theme:t.Theme
    
    icon:Tag
    
    osmGdf:gpd.GeoDataFrame
    omfGdf:gpd.GeoDataFrame
    
    osmLayer:lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer
    omfLayer:lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer
    layerType:lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer
    
    osmOtherGdf:gpd.GeoDataFrame
    omfOtherGdf:gpd.GeoDataFrame
    
    osmOtherLayers:list[lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer]
    omfOtherLayers:list[lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer]
    otherLayersType: list[lonboard.ScatterplotLayer | lonboard.PathLayer | lonboard.PolygonLayer]
    
    columnCriterion:str
    displayNameCriterion:str
    displayNameMap:str
    
    @property
    @abstractmethod
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        pass
    
    
    @property
    @abstractmethod
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        pass
    
    
    @property
    @abstractmethod
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm layer.
        """
        pass
    
    
    @property
    @abstractmethod
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for omf layer.
        """
        pass
    
    
    def _getLayer(self,
                  tableName:str,
                  engine:sqlalchemy.engine.base.Engine) -> gpd.GeoDataFrame:
        """Get OSM layer for the table.
        The tableName is made from the area.

        Args:
            tableName (str): Name of the PostGIS table.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame corresponding to the layer.
        """
        return gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {tableName}", engine)
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Parameter
        self.area = area
        self.areaKm2 = areaKm2
        self.crs = crs
        
        # OSM and OMF gdfs
        self.osmGdf = self._getLayer(self._osmLayerTemplate.format(area.lower()), engine)
        self.omfGdf = self._getLayer(self._omfLayerTemplate.format(area.lower()), engine)
        
        # Create LonBoard layer
        self.osmLayer = self.layerType.from_geopandas(self.osmGdf)
        self.omfLayer = self.layerType.from_geopandas(self.omfGdf)
        
        # Optional other gdfs and Lonboard layer creation
        self.osmOtherGdf = [self._getLayer(layerTemplate.format(area.lower()), engine) for layerTemplate in self._osmOtherLayerTemplate]
        self.omfOtherGdf = [self._getLayer(layerTemplate.format(area.lower()), engine) for layerTemplate in self._omfOtherLayerTemplate]
        
        self.osmOtherLayers = [self.otherLayersType[index].from_geopandas(gdf) for index, gdf in enumerate(self.osmOtherGdf)]
        self.omfOtherLayers = [self.otherLayersType[index].from_geopandas(gdf) for index, gdf in enumerate(self.omfOtherGdf)]
        
        # Calculate criterion values
        self.osmValue = self.calculateInformation(self.osmGdf)
        self.omfValue = self.calculateInformation(self.omfGdf)
    
    
    @abstractmethod
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        pass


class DefaultCriterion(Criterion):
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return ""
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return ""
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm layer.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
        
    
    def __init__(self) -> None:
        """Constructor for the default criterion.
        """
        # Theme
        self.theme = t.DefaultTheme
        
        self.area = ""
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = ""
        self.displayNameCriterion = "Criteria display"
        self.displayNameMap = ""
        
        self.icon = fa.icon_svg("star")
        
        # Do not calculate information for the Default Criterion
        self.osmValue = ""
        self.omfValue = ""
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        pass


class RoadNetwork(Criterion):
    
    displayNameMap = "Road network"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "osm.edge_with_cost_{}"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "omf.edge_with_cost_{}"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return ["osm.node_{}"]
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return ["omf.node_{}"]
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph
        
        # Layer type
        self.layerType = lonboard.PathLayer
        self.otherLayersType = [lonboard.ScatterplotLayer]
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "overlap"
        self.displayNameCriterion = "Total length (km)"
        
        self.icon = fa.icon_svg("ruler")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Get total length for the layer.
        Sum up the distance from the dataframe of length per class.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame of length per class.
        
        Returns:
            str: Overlap indicator value.
        """
        # Copy the DataFrame to prevent problems
        gdfCopy = gdf.copy()
        # If it is empty, create an empty DataFrame
        if gdfCopy.empty:
            value = ""
        else:
            # Set geometry column and project to another crs
            gdfCopy = gdfCopy.set_geometry("geom")
            gdfProj = gdfCopy.to_crs(self.crs)
            
            # Calculate length based on the projected geometry in km
            gdfCopy['length'] = gdfProj['geom'].length / 1000
            
            # Calculate the sum of the length column
            value = round(gdfCopy["length"].sum())
        return str(value)
    

class ConnectedComponents(Criterion):
    
    displayNameMap = "Connected components"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "results.connected_components_{}_osm"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "results.connected_components_{}_omf"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return ["osm.edge_with_cost_{}"]
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return ["omf.edge_with_cost_{}"]
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph
        
        # Layer type
        self.layerType = lonboard.ScatterplotLayer
        self.otherLayersType = [lonboard.PathLayer]
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "component"
        self.displayNameCriterion = "Number of connected components"
        
        self.icon = fa.icon_svg("arrows-left-right")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Missing value if the GeoDataFrame is empty
        if gdf.empty:
            value = ""

        else:
            # Aggregate on the column and count the number of aggregation
            gdfSumup = gdf[[self.columnCriterion]].groupby(self.columnCriterion, dropna = False)[self.columnCriterion].agg(['count'])
            
            # Reset index and take the number
            gdfSumup.reset_index(inplace=True)
            value = gdfSumup.shape[0]
        
        return str(value)


class StrongComponents(Criterion):
    
    displayNameMap = "Strongly connected components"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "results.strong_components_{}_osm"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "results.strong_components_{}_omf"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return ["osm.edge_with_cost_{}"]
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return ["omf.edge_with_cost_{}"]
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph
        
        # Layer type
        self.layerType = lonboard.ScatterplotLayer
        self.otherLayersType = [lonboard.PathLayer]
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "component"
        self.displayNameCriterion = "Number of strongly connected components"
        
        self.icon = fa.icon_svg("arrow-right")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Missing value if the GeoDataFrame is empty
        if gdf.empty:
            value = ""

        else:
            # Aggregate on the column and count the number of aggregation
            gdfSumup = gdf[[self.columnCriterion]].groupby(self.columnCriterion, dropna = False)[self.columnCriterion].agg(['count'])
            
            # Reset index and take the number
            gdfSumup.reset_index(inplace=True)
            value = gdfSumup.shape[0]
        
        return str(value)


class IsolatedNodes(Criterion):
    
    displayNameMap = "Number of isolated nodes"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "results.isolated_nodes_{}_osm"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "results.isolated_nodes_{}_omf"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph
        
        # Layer type
        self.layerType = lonboard.ScatterplotLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "intersects"
        self.displayNameCriterion = "Isolated nodes"
        
        self.icon = fa.icon_svg("circle-dot")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Missing value if the GeoDataFrame is empty
        if gdf.empty:
            value = ""

        else:
            # Aggregate on the column and count the number of aggregation
            gdfSumup = gdf[[self.columnCriterion]].groupby(self.columnCriterion, dropna = False)[self.columnCriterion].agg(['count'])
            
            # Reset index
            gdfSumup.reset_index(inplace=True)
            value = 0
            
            for _, row in gdfSumup.iterrows():
                # Take the number of nodes that do not intersects
                if row[self.columnCriterion] == False:
                    value = row['count']
        
        return str(value)


class OverlapIndicator(Criterion):
    
    displayNameMap = "Overlap indicator"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "results.overlap_indicator_{}_osm"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "results.overlap_indicator_{}_omf"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph
        
        # Layer type
        self.layerType = lonboard.PathLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "overlap"
        self.displayNameCriterion = "Overlap indicator (%)"
        
        self.icon = fa.icon_svg("grip-lines")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self,
                             gdf:gpd.GeoDataFrame) -> str:
        """Get indicator value for the overlap indicator criterion.
        Calculate the total length of overlapping roads and return
        the proportion of length overlapping over the total length.

        Args:
            gdf (gpd.GeoDataFrame): Layer GeoDataFrame.

        Returns:
            str: Value of the indicator.
        """
        # Copy the GeoDataFrame to prevent error
        gdfCopy = gdf.copy()

        # Missing value if the GeoDataFrame is empty
        if gdfCopy.empty:
            value = ""
            
        else:
            # Set geometry column
            gdfCopy = gdfCopy.set_geometry("geom")
            
            # Get crs for the area and project to this crs
            gdfProj = gdfCopy.to_crs(self.crs)
            
            # Calculate length based on the projected geometry in km
            gdfCopy['length'] = gdfProj['geom'].length / 1000
            
            # Agregate per class and calculate sum for each class
            gdfSumup = gdfCopy[[self.columnCriterion, 'length']].groupby(self.columnCriterion, dropna = False)['length'].agg(['sum'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Get overlapping length and total length
            overlapLength = 0
            totalLength = 0
            
            for _, row in gdfSumup.iterrows():
                if row[self.columnCriterion] == True:
                    overlapLength = row['sum']
                totalLength += row['sum']
            
            # Calculate the proporion in %
            value = round((overlapLength / totalLength) * 100, 2)
            value = f"{value} %"
        
        return str(value)


class CorrespondingNodes(Criterion):
    
    displayNameMap = "Corresponding nodes"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "results.corresponding_nodes_{}_osm"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "results.corresponding_nodes_{}_omf"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph
        
        # Layer type
        self.layerType = lonboard.ScatterplotLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "intersects"
        self.displayNameCriterion = "Corresponding nodes (Total number - %)"
        
        self.icon = fa.icon_svg("clone")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Copie the GeoDataFrame to prevent error
        if gdf.empty:
            value = ""

        else:
            # Aggregate on the column and count the number of rows
            gdfSumup = gdf[[self.columnCriterion]].groupby(self.columnCriterion, dropna = False)[self.columnCriterion].agg(['count'])
            
            # Reset index
            gdfSumup.reset_index(inplace=True)
            
            # Get number of corresponding nodes and number of total nodes
            totalNodes = 0
            correspondingNodes = 0
            for _, row in gdfSumup.iterrows():
                if row[self.columnCriterion] == True:
                    correspondingNodes = row['count']
                totalNodes += row['count']
            
            # Calculate proportion and create string value
            percentage = round((correspondingNodes / totalNodes) * 100, 2)
            value = f"{correspondingNodes} - {percentage} %"
        
        return str(value)


class BuildingCoverage(Criterion):
    
    displayNameMap = "Buildings (coverage)"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "osm.building_{}"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "omf.building_{}"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Building
        
        # Layer type
        self.layerType = lonboard.PolygonLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.displayNameCriterion = "Buildings coverage (%)"
        
        self.icon = fa.icon_svg("building")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Copy the GeoDataFrame to prevent error
        gdfCopy = gdf.copy()
        
        # Missing value if the GeoDataFrame is empty
        if gdfCopy.empty:
            value = ""
        
        else:
            # Set geometry column
            gdfCopy = gdfCopy.set_geometry("geom")
            
            # Project to the crs
            gdfProj = gdfCopy.to_crs(self.crs)
            
            # Calculate area based on the projected geometry in km
            gdfCopy['area'] = gdfProj["geom"].area
            
            # Calculate the sum of the buildings area in km2
            buildingsArea = gdfCopy["area"].sum() / 1000000
            
            # Calculate the coverage
            value = f"{round((buildingsArea / self.areaKm2), 2)} %"
        
        return str(value)


class BuildingDensity(Criterion):
    
    displayNameMap = "Buildings (density)"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "osm.building_{}"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "omf.building_{}"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Building
        
        # Layer type
        self.layerType = lonboard.PolygonLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.displayNameCriterion = "Density of buildings (nb / km2)"
        
        self.icon = fa.icon_svg("city")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Missing value if the GeoDataFrame is empty
        if gdf.empty:
            value = ""
        
        else:
            # Get number of element
            number = gdf.shape[0]
            
            # Calculate the density
            value = f"{round((number / self.areaKm2), 2)} / km2"
        
        return str(value)


class PlaceDensity(Criterion):
    
    displayNameMap = "Places / Points of interest (density)"
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return "osm.place_{}"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "omf.place_{}"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list[str]:
        """
        list: Template name for osm other layers.
        """
        return []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        list: Template names for omf other layers.
        """
        return []
    
    
    def __init__(self,
                 area:str,
                 areaKm2:float,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            areaKm2 (float): Area in km2 of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Place
        
        # Layer type
        self.layerType = lonboard.ScatterplotLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.displayNameCriterion = "Density of POI (nb / km2)"
        
        self.icon = fa.icon_svg("location-dot")
        
        # Get GeoDataFrames
        super().__init__(area, areaKm2, crs, engine)
    
    
    def calculateInformation(self, gdf:gpd.GeoDataFrame) -> str:
        """Calulate the criterion information for the given GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame for OSM or OMF value.
        
        Returns:
            str: Criterion value.
        """
        # Missing value if the GeoDataFrame is empty
        if gdf.empty:
            value = ""
        
        else:
            # Get number of element
            number = gdf.shape[0]
            
            # Calculate the density
            value = f"{round((number / self.areaKm2), 2)} / km2"
        
        return str(value)


