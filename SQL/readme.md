# Buildings

## Overture Maps

Install a CLI tool to download Overture Maps data.

```
pip install overturemaps
```

Run the following code and it will download buildings in target areas from Overture Maps and import them into PostgreSQL.

```
bash buildings/download_import_ovt.sql
```

## OpenStreetMap

This script just import tsv files into PostgreSQL.
You need to extract data before running this script.

```
bash building/import_osm_tsv.shcd .
```
