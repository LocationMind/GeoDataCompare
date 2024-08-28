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
        str: Template name for osm layer.
        """
        pass
    
    
    @property
    @abstractmethod
    def _omfOtherLayerTemplate(self) -> list[str]:
        """
        str: Template name for omf layer.
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
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for a criterion

        Args:
            area (str): Name of the area.
            crs (int): UTM projection id.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.area = area
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
        self.calculateInformation()
    
    @abstractmethod
    def calculateInformation(self):
        pass

class OverlapIndicator(Criterion):
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return  "results.overlap_indicator_{}_osm"
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return "results.overlap_indicator_{}_omf"
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list:
        """
        str: Template name for osm layer.
        """
        return  []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list:
        """
        str: Template name for omf layer.
        """
        return []
    
    def __init__(self,
                 area:str,
                 crs:int,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor for the overlap indicator

        Args:
            area (str): Name of the area.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.Graph(area, crs, engine)
        
        # Layer type
        self.layerType = lonboard.PathLayer
        self.otherLayersType = []
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = "overlap"
        self.displayNameCriterion = "Overlap indicator (%)"
        self.displayNameMap = "Overlap indicator"
        
        self.icon = fa.icon_svg("grip-lines")
        
        # Get GeoDataFrames
        super().__init__(area, crs, engine)
        
        
        
    
    
    def calculateInformation(self) -> None:
        """Get indicator value for the overlap indicator criterion.
        Calculate the total length of overlapping roads and return
        the proportion of length overlapping over the total length.
        
        Returns:
            tuple[str, str]: First value is for OSM, second one is for OMF.
        """
        # Copy the GeoDataFrame to prevent error
        self.osmValue = self._calculateOverlapIndicator(self.osmGdf)
        self.omfValue = self._calculateOverlapIndicator(self.omfGdf)
    
    
    def _calculateOverlapIndicator(self,
                                   gdf:gpd.GeoDataFrame) -> str:
        """Get indicator value for the overlap indicator criterion.
        Calculate the total length of overlapping roads and return
        the proportion of length overlapping over the total length.

        Args:
            areaCRS (dict[str, int]): UTM projection for each areas, in a dict form.

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
    

class DefaultCriterion(Criterion):
    
    @property
    def _osmLayerTemplate(self) -> str:
        """
        str: Template name for osm layer.
        """
        return  ""
    
    
    @property
    def _omfLayerTemplate(self) -> str:
        """
        str: Template name for omf layer.
        """
        return ""
    
    
    @property
    def _osmOtherLayerTemplate(self) -> list:
        """
        str: Template name for osm layer.
        """
        return  []
    
    
    @property
    def _omfOtherLayerTemplate(self) -> list:
        """
        str: Template name for omf layer.
        """
        return []
        
    
    def __init__(self) -> None:
        """Constructor for the overlap indicator

        Args:
            area (str): Name of the area.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.theme = t.DefaultTheme()
        
        self.area = ""
        
        # Name of the column for the criterion and for displaying it
        self.columnCriterion = ""
        self.displayNameCriterion = "Criteria display"
        self.displayNameMap = ""
        
        self.icon = fa.icon_svg("star")
    
    
    def calculateInformation(self,
                             areasCRS:dict[str, int]) -> tuple[str, str]:
        """Get indicator value for the overlap indicator criterion.
        Calculate the total length of overlapping roads and return
        the proportion of length overlapping over the total length.

        Args:
            areaCRS (dict[str, int]): UTM projection for each areas, in a dict form.

        Returns:
            tuple[str, str]: First value is for OSM, second one is for OMF.
        """
        # Copy the GeoDataFrame to prevent error
        self.osmValue = ""
        self.omfValue = ""