# Buildings

## Overture Maps

Install a CLI tool or overturemaps-py repo to download Overture Maps data.

```sh
bash OMF/setup.sh
```

Run the following code and it will download building in target areas from Overture Maps and import them into PostgreSQL

```sh
## address
bash OMF/ETL/omf_download.sh address latest
bash OMF/ETL/omf_import.sh address
## building
bash OMF/ETL/omf_download.sh building 
bash OMF/ETL/omf_import.sh building
## place
bash OMF/ETL/omf_download.sh place
bash OMF/ETL/omf_import.sh place
```

Check all version available 

## OpenStreetMap

This script just import tsv files into PostgreSQL.
You need to extract data before running this script.

```sh
bash building/import_osm_tsv.sh
```