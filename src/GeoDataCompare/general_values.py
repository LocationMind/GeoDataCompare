import pandas as pd
import sqlalchemy
from abc import ABC
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import datasets as d


class AbstractGeneralValues(ABC):
    """Abstract class for general values"""

    datasetA: d.Dataset
    datasetB: d.Dataset

    nbNodesDatasetA: str
    nbNodesDatasetB: str
    nbEdgesDatasetA: str
    nbEdgesDatasetB: str
    nbBuildingsDatasetA: str
    nbBuildingsDatasetB: str
    nbPlacesDatasetA: str
    nbPlacesDatasetB: str

    def __init__(self, datasetA: d.Dataset, datasetB: d.Dataset) -> None:
        """Constructor that calulates all general values for the abstract class

        Args:
            area (str): Name of the area.
            datasetA (dataset.Dataset): First dataset.
            datasetB (dataset.Dataset): Second dataset.
        """
        self.datasetA = datasetA
        self.datasetB = datasetB


class DefaultGeneralValues(AbstractGeneralValues):

    def __init__(self, datasetA: d.Dataset, datasetB: d.Dataset) -> None:
        """Constructor for default values

        Args:
            area (str): Name of the area.
            datasetA (dataset.Dataset): First dataset.
            datasetB (dataset.Dataset): Second dataset.
        """
        super().__init__(datasetA, datasetB)

        # Set only default values
        self.nbNodesDatasetA = ""
        self.nbNodesDatasetB = ""
        self.nbEdgesDatasetA = ""
        self.nbEdgesDatasetB = ""
        self.nbBuildingsDatasetA = ""
        self.nbBuildingsDatasetB = ""
        self.nbPlacesDatasetA = ""
        self.nbPlacesDatasetB = ""


class GeneralValues(DefaultGeneralValues):

    def getNbRowTable(
        self, engine: sqlalchemy.engine.base.Engine, tableName: str
    ) -> str:
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
        number = result.iloc[0, 0]

        return str(number)

    def __init__(
        self,
        area: str,
        engine: sqlalchemy.engine.base.Engine,
        datasetA: d.Dataset,
        datasetB: d.Dataset,
    ) -> None:
        """Constructor that calulates all general values

        Args:
            area (str): Name of the area.
            engine (sqlalchemy.engine.base.Engine):
            Engine used for (geo)pandas sql queries.
        """
        super().__init__(datasetA, datasetB)
        # Get all values
        self.nbEdgesDatasetA = self.getNbRowTable(
            engine, self.datasetA.edgeTable.format(area.lower())
        )
        self.nbEdgesDatasetB = self.getNbRowTable(
            engine, self.datasetB.edgeTable.format(area.lower())
        )
        self.nbNodesDatasetA = self.getNbRowTable(
            engine, self.datasetA.nodeTable.format(area.lower())
        )
        self.nbNodesDatasetB = self.getNbRowTable(
            engine, self.datasetB.nodeTable.format(area.lower())
        )
        self.nbBuildingsDatasetA = self.getNbRowTable(
            engine, self.datasetA.buildingTable.format(area.lower())
        )
        self.nbBuildingsDatasetB = self.getNbRowTable(
            engine, self.datasetB.buildingTable.format(area.lower())
        )
        self.nbPlacesDatasetA = self.getNbRowTable(
            engine, self.datasetA.placeTable.format(area.lower())
        )
        self.nbPlacesDatasetB = self.getNbRowTable(
            engine, self.datasetB.placeTable.format(area.lower())
        )
