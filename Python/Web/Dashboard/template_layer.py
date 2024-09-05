import pandas as pd
import sqlalchemy

class DefaultGeneralValues(object):
    
    def __init__(self) -> None:
        """Constructor that calulates all general values

        Args:
            area (str): Name of the area.
            engine (sqlalchemy.engine.base.Engine):
            Engine used for (geo)pandas sql queries.
        """
        # Set only default values
        self.nbNodesOSM = ""
        self.nbNodesOMF = ""
        self.nbEdgesOSM = ""
        self.nbEdgesOMF = ""
        self.nbBuildingsOSM = ""
        self.nbBuildingsOMF = ""
        self.nbPlacesOSM = ""
        self.nbPlacesOMF = ""


class GeneralValues(DefaultGeneralValues):
    """Provides function to get general values for an area
    """
    # Template layer names
    _osmEdgeTable = "osm.edge_with_cost_{}"
    _omfEdgeTable = "omf.edge_with_cost_{}"
    _osmNodeTable = "osm.node_{}"
    _omfNodeTable = "omf.node_{}"
    _osmBuildingTable = "osm.building_{}"
    _omfBuildingTable = "omf.building_{}"
    _osmPlaceTable = "osm.place_{}"
    _omfPlaceTable = "omf.place_{}"
    
    def getNbRowTable(self,
                      engine:sqlalchemy.engine.base.Engine,
                      tableName:str) -> str:
        """Get the number of elements in a table directly store in PostgreSQL.

        Args:
            engine (sqlalchemy.engine.base.Engine):
            Engine used for (geo)pandas sql queries.
            tableName (str, optional): Name of the table
            (with the schema already on it).

        Returns:
            str: Number of entity in the table.
        """
        # Get all the entity from bounding box table
        sqlQueryTable = f"""SELECT count(*) as nb FROM {tableName};"""
        
        result = pd.read_sql(sqlQueryTable, engine)
        
        # Take the first element of the result
        number = result.iloc[0,0]
        
        return str(number)
    
    def __init__(self,
                 area:str,
                 engine:sqlalchemy.engine.base.Engine) -> None:
        """Constructor that calulates all general values

        Args:
            area (str): Name of the area.
            engine (sqlalchemy.engine.base.Engine):
            Engine used for (geo)pandas sql queries.
        """
        # Get all values
        self.nbNodesOSM = self.getNbRowTable(engine, self._osmEdgeTable.format(area.lower()))
        self.nbNodesOMF = self.getNbRowTable(engine, self._omfEdgeTable.format(area.lower()))
        self.nbEdgesOSM = self.getNbRowTable(engine, self._osmNodeTable.format(area.lower()))
        self.nbEdgesOMF = self.getNbRowTable(engine, self._omfNodeTable.format(area.lower()))
        self.nbBuildingsOSM = self.getNbRowTable(engine, self._osmBuildingTable.format(area.lower()))
        self.nbBuildingsOMF = self.getNbRowTable(engine, self._omfBuildingTable.format(area.lower()))
        self.nbPlacesOSM = self.getNbRowTable(engine, self._osmPlaceTable.format(area.lower()))
        self.nbPlacesOMF = self.getNbRowTable(engine, self._omfPlaceTable.format(area.lower()))