import sys
import os
import duckdb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.Utils import utils


# Connections to the database
connection = utils.getConnection()
engine = utils.getEngine()
utils.initialiseDuckDB()


# Create test table
query = """
DROP TABLE IF EXISTS test CASCADE;

CREATE TEMP TABLE test (id, name) AS
VALUES (0::integer, 'foo'), (1::integer, 'bar') ;"""
utils.executeQueryWithTransaction(connection, query)

# Bbox
bbox = "139.74609375,35.67514744,139.83398438,35.74651226"
expectedWKT = "POLYGON ((139.74609375 35.74651226, 139.83398438 35.74651226, 139.83398438 35.67514744, 139.74609375 35.67514744, 139.74609375 35.74651226))"
expectedTuple = (35.74651226, 35.67514744, 139.83398438, 139.74609375)


def test_getConnection():
    assert connection is not None


def test_getEngine():
    assert engine is not None


def test_executeSelectQuery():
    query = "SELECT * FROM test;"
    cursor = utils.executeSelectQuery(connection, query)
    row = cursor.fetchone()
    assert row == (0, "foo")


def test_posgtresVersion():
    query = "SELECT version();"
    cursor = utils.executeSelectQuery(connection, query)
    row = cursor.fetchone()
    assert "PostgreSQL 16.2" in row[0]


def test_postgisVersion():
    query = "SELECT postgis_version();"
    cursor = utils.executeSelectQuery(connection, query)
    row = cursor.fetchone()
    assert row[0] == "3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1"


def test_prgroutingVersion():
    query = "SELECT pgr_version();"
    cursor = utils.executeSelectQuery(connection, query)
    row = cursor.fetchone()
    assert row[0] == "3.6.1"


def test_initDuckDB():
    spatial = duckdb.sql(
        "SELECT extension_name, installed, description FROM duckdb_extensions() WHERE extension_name = 'spatial';"
    )
    rowSpatial = spatial.fetchone()
    postgres = duckdb.sql(
        "SELECT extension_name, installed, description FROM duckdb_extensions() WHERE extension_name = 'postgres_scanner';"
    )
    rowPostgres = postgres.fetchone()
    assert rowSpatial[1]
    assert rowPostgres[1]


def test_bboxCSVToBboxWKT():
    assert utils.bboxCSVToBboxWKT(bbox) == expectedWKT


def test_bboxCSVToTuple():
    assert utils.bboxCSVToTuple(bbox) == expectedTuple


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", __file__])
