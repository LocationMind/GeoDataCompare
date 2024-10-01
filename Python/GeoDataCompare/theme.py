from abc import ABC, abstractmethod
import pandas as pd
import geopandas as gpd
import sqlalchemy

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import datasets as d

class Theme(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """
    datasetA: d.Dataset
    datasetB: d.Dataset
    
    datasetAClasses:gpd.GeoDataFrame
    datasetBClasses:gpd.GeoDataFrame
    
    crs:int
    
    dfHeader:str
    columnGroupBy:str
    
    @property
    @abstractmethod
    def _datasetALayerTemplate(self) -> str:
        """
        str: Template name for dataset A layer.
        """
        pass
    
    @property
    @abstractmethod
    def _datasetBLayerTemplate(self) -> str:
        """
        str: Template name for dataset B layer.
        """
        pass
    
    @abstractmethod
    def calculateDataFrame(self,
                           tableName:str,
                           engine:sqlalchemy.Engine):
        pass
    
    def __init__(self,
                 area:str,
                 crs:int,
                 engine:sqlalchemy.Engine,
                 datasetA:d.Dataset,
                 datasetB:d.Dataset,) -> None:
        """Constructor for a Theme

        Args:
            area (str): Name of the area.
            crs (int): UTM Projection for the area. 
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
            datasetA (dataset.Dataset): First dataset.
            datasetB (dataset.Dataset): Second dataset.
        """
        # Theme
        self.crs = crs
        
        self.datasetA = datasetA
        self.datasetB = datasetB
        
        self.datasetAClasses = self.calculateDataFrame(self._datasetALayerTemplate.format(area.lower()), engine)
        self.datasetBClasses = self.calculateDataFrame(self._datasetBLayerTemplate.format(area.lower()), engine)
        


class DefaultTheme(Theme):
    
    def __init__(self) -> None:
        self.dfHeader = ""
        
        self.datasetAClasses = gpd.GeoDataFrame()
        self.datasetBClasses = gpd.GeoDataFrame()
    
    @property
    def _datasetALayerTemplate(self) -> str:
        """
        str: Template name for dataset A layer.
        """
        return ""
    
    @property
    def _datasetBLayerTemplate(self) -> str:
        """
        str: Template name for dataset B layer.
        """
        return ""
    
    def calculateDataFrame(self):
        return pd.DataFrame()
    

class Graph(Theme):
    
    def __init__(self,
                 area: str,
                 crs: int,
                 engine: sqlalchemy.Engine,
                 datasetA:d.Dataset,
                 datasetB:d.Dataset,) -> None:
        
        self.dfHeader = f"Number of edges and total length (in km) per class in {area}"
        
        self.columnGroupBy = "class"
        self.columnDisplay = "Class"
        
        super().__init__(area, crs, engine, datasetA = datasetA, datasetB = datasetB)
    
    @property
    def _datasetALayerTemplate(self) -> str:
        """
        str: Template name for dataset A layer.
        """
        return self.datasetA.edgeTable
    
    @property
    def _datasetBLayerTemplate(self) -> str:
        """
        str: Template name for dataset B layer.
        """
        return self.datasetB.edgeTable
    
    def calculateDataFrame(self,
                           tableName:str,
                           engine:sqlalchemy.engine.base.Engine) -> pd.DataFrame:
        """Return the dataframe to display for the graph theme.
        It corresponds to the length and number of edges per classes

        Args:
            tableName (str): Name of the table.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.

        Returns:
            pd.DataFrame: Dataframe with values for each classes
        """
        # Get dataframe
        gdf = gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {tableName}", engine)
        # If it is empty, create an empty DataFrame
        if gdf.empty:
            gdfSumup = pd.DataFrame()
        else:
            # Set geometry column and project to another crs
            gdf = gdf.set_geometry("geom")
            gdfProj = gdf.to_crs(self.crs)
            
            # Calculate length based on the projected geometry in km
            gdf['length'] = gdfProj['geom'].length / 1000
            
            # Agregate per class and calculate the sum and count for each class
            gdfSumup = gdf[[self.columnGroupBy, 'length']].groupby(self.columnGroupBy, dropna = False)['length'].agg(['sum', 'count'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Rename columns
            gdfSumup = gdfSumup.rename(columns = {
                self.columnGroupBy:self.columnDisplay,
                "sum": "Total length (km)",
                "count":"Number of edges",
            })
        
        return gdfSumup


class Building(Theme):
    
    def __init__(self,
                 area: str,
                 crs: int,
                 engine: sqlalchemy.Engine,
                 datasetA:d.Dataset,
                 datasetB:d.Dataset,) -> None:
        
        self.dfHeader = f"Number of buildings and total area (in km2) per class in {area}"
        
        self.columnGroupBy = "class"
        self.columnDisplay = "Class"
        
        super().__init__(area, crs, engine, datasetA = datasetA, datasetB = datasetB)
    
    @property
    def _datasetALayerTemplate(self) -> str:
        """
        str: Template name for dataset A layer.
        """
        return self.datasetA.buildingTable
    
    @property
    def _datasetBLayerTemplate(self) -> str:
        """
        str: Template name for dataset B layer.
        """
        return self.datasetB.buildingTable
    
    def calculateDataFrame(self,
                           tableName:str,
                           engine:sqlalchemy.engine.base.Engine) -> pd.DataFrame:
        """Return a DataFrame with length and number of edges per classes.

        Args:
            gdf (gpd.GeoDataFrame): edge GeoDataFrame

        Returns:
            pd.DataFrame: Dataframe with values for each classes
        """
        # Get dataframe
        gdf = gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {tableName}", engine)
        # If it is empty, create an empty DataFrame
        if gdf.empty:
            gdfSumup = pd.DataFrame()
        else:
            # Set geometry column and project to another crs
            gdf = gdf.set_geometry("geom")
            gdfProj = gdf.to_crs(self.crs)
            
            # Calculate area based on the projected geometry in km
            gdf['area'] = gdfProj['geom'].area / 1000000
            
            # Agregate per class and calculate the sum and count for each class
            gdfSumup = gdf[[self.columnGroupBy, 'area']].groupby(self.columnGroupBy, dropna = False)['area'].agg(['sum', 'count'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Rename columns
            gdfSumup = gdfSumup.rename(columns = {
                self.columnGroupBy:self.columnDisplay,
                "sum": "Total area (km2)",
                "count":"Number of buildings",
            })
        
        return gdfSumup


class Place(Theme):
    
    def __init__(self,
                 area: str,
                 crs: int,
                 engine: sqlalchemy.Engine,
                 datasetA:d.Dataset,
                 datasetB:d.Dataset,) -> None:
        
        self.dfHeader = f"Number of places per category in {area}"
        
        self.columnGroupBy = "category"
        self.columnDisplay = "Category"
        
        super().__init__(area, crs, engine, datasetA = datasetA, datasetB = datasetB)
    
    @property
    def _datasetALayerTemplate(self) -> str:
        """
        str: Template name for dataset A layer.
        """
        return self.datasetA.placeTable
    
    @property
    def _datasetBLayerTemplate(self) -> str:
        """
        str: Template name for dataset B layer.
        """
        return self.datasetB.placeTable
    
    def calculateDataFrame(self,
                           tableName:str,
                           engine:sqlalchemy.engine.base.Engine) -> pd.DataFrame:
        """Return a DataFrame with length and number of edges per classes.

        Args:
            edgeGDF (gpd.GeoDataFrame): edge GeoDataFrame

        Returns:
            pd.DataFrame: Dataframe with values for each classes
        """
        # Get dataframe
        gdf = gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {tableName}", engine)
        # If it is empty, create an empty DataFrame
        if gdf.empty:
            gdfSumup = pd.DataFrame()
        
        else:
            # Set geometry column and project to another crs
            gdf = gdf.set_geometry("geom")
            
            # Agregate per categories and calculate the sum and count for each category
            gdfSumup = gdf[[self.columnGroupBy]].groupby(self.columnGroupBy, dropna = False)[self.columnGroupBy].agg(['size'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Replace NaN value by 'Null'
            gdfSumup = gdfSumup.fillna('Null')
            
            # Rename columns
            gdfSumup = gdfSumup.rename(columns = {
                self.columnGroupBy:self.columnDisplay,
                "size":"Number of places",
            })
        
        return gdfSumup