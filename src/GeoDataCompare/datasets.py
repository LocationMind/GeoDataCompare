from abc import ABC


class Dataset(ABC):
    """Abstract class for datasets.

    Attributes:
        name (str): Name of the dataset.
        acronym (str): Acronym of the dataset.
        schema (str): Name of the schema in the database.
        iconSrc (str): Link of the dataset logo.
        websiteLink (str): Link of the dataset website.
        title (str): Title of the icon if it exits.

        edgeTable (str): Name of the edge table for this dataset in the database
        nodeTable (str): Name of the node table for this dataset in the database
        buildingTable (str): Name of the building table for this dataset in the database
        placeTable (str): Name of the edge place for this dataset in the database
    """

    name: str
    acronym: str
    schema: str
    iconSrc: str
    websiteLink: str
    title: str

    edgeTable: str
    nodeTable: str
    buildingTable: str
    placeTable: str


class OpenStreetMap(Dataset):
    """OpenStreetMap dataset"""

    def __init__(self) -> None:
        self.name = "OpenStreetMap"
        self.acronym = "OSM"
        self.schema = "osm"
        self.iconSrc = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Openstreetmap_logo.svg/32px-Openstreetmap_logo.svg.png?20220919103849"
        self.href = "https://openstreetmaps.org"
        self.title = "Ken Vermette based on https://commons.wikimedia.org/wiki/File:OpenStreetMap-Logo-2006.svg, CC BY-SA 2.0 &lt;https://creativecommons.org/licenses/by-sa/2.0&gt;, via Wikimedia Commons"

        self.edgeTable = "osm.edge_with_cost_{}"
        self.nodeTable = "osm.node_{}"
        self.buildingTable = "osm.building_{}"
        self.placeTable = "osm.place_{}"


class OvertureMapsFoundation(Dataset):
    """Overture Maps Foundation dataset"""

    def __init__(self) -> None:
        self.name = "Overture Maps Foundation"
        self.acronym = "OMF"
        self.schema = "omf"
        self.iconSrc = "https://docs.overturemaps.org/img/omf_logo_transparent.png"
        self.href = "https://overturemaps.org/"
        self.title = ""

        self.edgeTable = "omf.edge_with_cost_{}"
        self.nodeTable = "omf.node_{}"
        self.buildingTable = "omf.building_{}"
        self.placeTable = "omf.place_{}"
