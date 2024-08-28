from abc import ABC, abstractmethod
import pandas as pd
import geopandas as gpd
import sqlalchemy

class Theme(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """
    
    osmClasses:gpd.GeoDataFrame
    omfClasses:gpd.GeoDataFrame
    
    crs:int
    
    dfHeader:str
    
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
    
    @abstractmethod
    def calculateDataFrame(self,
                           tableName:str,
                           engine:sqlalchemy.Engine):
        pass
    
    def __init__(self,
                 area:str,
                 crs:int,
                 engine:sqlalchemy.Engine) -> None:
        """Constructor for the overlap indicator

        Args:
            area (str): Name of the area.
            engine (sqlalchemy.engine.base.Engine): Engine for database connexion.
        """
        # Theme
        self.crs = crs
        
        self.osmClasses = self.calculateDataFrame(self._osmLayerTemplate.format(area.lower()), engine)
        self.omfClasses = self.calculateDataFrame(self._omfLayerTemplate.format(area.lower()), engine)
        


class DefaultTheme(Theme):
    
    def __init__(self) -> None:
        self.dfHeader = ""
        
        self.osmClasses = gpd.GeoDataFrame()
        self.omfClasses = gpd.GeoDataFrame()
    
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
    
    def calculateDataFrame(self):
        print("Default DataFrame")
    

class Graph(Theme):
    
    def __init__(self, area: str, crs: int, engine: sqlalchemy.Engine) -> None:
        self.dfHeader = f"Number of edges and total length (in km) per class in {area}"
        super().__init__(area, crs, engine)
    
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
    
    def calculateDataFrame(self,
                           tableName:str,
                           engine:sqlalchemy.engine.base.Engine) -> pd.DataFrame:
        """Return the dataframe to display for the graph theme.
        It corresponds to the length and number of edges per classes

        Args:
            gdf (gpd.GeoDataFrame): edges GeoDataFrame.
            crs (int): crs to use for the calculation.
            columnType (str, optional): Type of the column to aggregate on.
            Only used in calculateDataFramePlaces function.
            Default value is None.

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
            gdfSumup = gdf[['class', 'length']].groupby('class', dropna = False)['length'].agg(['sum', 'count'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Rename columns
            gdfSumup = gdfSumup.rename(columns = {
                "class":"Class",
                "sum": "Total length (km)",
                "count":"Number of edges",
            })
        
        return gdfSumup


class Building(Theme):
    
    def __init__(self, area: str, crs: int, engine: sqlalchemy.Engine) -> None:
        self.dfHeader = f"Number of buildings and total area (in km2) per class in {area}"
        self.dfHeader = f"Number of places per category in {area}"
        super().__init__(area, crs, engine)
    
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
            gdfSumup = gdf[['class', 'area']].groupby('class', dropna = False)['area'].agg(['sum', 'count'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Rename columns
            gdfSumup = gdfSumup.rename(columns = {
                "class":"Class",
                "sum": "Total area (km2)",
                "count":"Number of buildings",
            })
        
        return gdfSumup


class Place(Theme):
    
    def __init__(self, area: str, crs: int, engine: sqlalchemy.Engine) -> None:
        self.dfHeader = f"Number of places per category in {area}"
        super().__init__(area, crs, engine)
    
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
            
            # Check first value not null of categories
            value = gdf[gdf['categories'].notnull()]["categories"].iloc[0]
            
            # If it is a dictionnary, it is OMF dataset. We take the main category
            if type(value) == dict:
                gdf['category'] = gdf['categories'].apply(lambda categories: categories['main'] if (categories is not None) else None)
            # Otherwise, we rename the column to 'category'
            else:
                gdf = gdf.rename(columns = {'categories':'category'})
            
            # Agregate per categories and calculate the sum and count for each category
            gdfSumup = gdf[['category']].groupby('category', dropna = False)['category'].agg(['size'])
            
            # Reset index to export class
            gdfSumup.reset_index(inplace=True)
            
            # Replace NaN value by 'Null'
            gdfSumup = gdfSumup.fillna('Null')
            
            # Rename columns
            gdfSumup = gdfSumup.rename(columns = {
                "category":"Category",
                "size":"Number of places",
            })
        
        return gdfSumup