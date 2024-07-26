# Buildings

## Overture Maps

- Install a CLI tool or overturemaps-py repo to download Overture Maps data.

```sh
bash OMF/setup.sh
```

- Run the following code and it will download building in target areas from Overture Maps and import them into PostgreSQL

```sh
# get latest
## address
bash OMF/ETL/omf_download.sh address latest
bash OMF/ETL/omf_import.sh address latest
## building
bash OMF/ETL/omf_download.sh building latest
bash OMF/ETL/omf_import.sh building latest
## place
bash OMF/ETL/omf_download.sh place latest
bash OMF/ETL/omf_import.sh place latest

# get target version
## address
bash OMF/ETL/omf_download.sh address 2024-07-22.0
bash OMF/ETL/omf_import.sh address 2024-07-22.0
...
```

- Check all versions available

```sh
$ aws s3 ls s3://overturemaps-us-west-2/release/ --region us-west-2 --no-sign-request
  PRE 2023-04-02-alpha/
  PRE 2023-07-26-alpha.0/
  PRE 2023-10-19-alpha.0/
  PRE 2023-11-14-alpha.0/
  PRE 2023-12-14-alpha.0/
  PRE 2024-01-17-alpha.0/
  PRE 2024-02-15-alpha.0/
  PRE 2024-03-12-alpha.0/
  PRE 2024-04-16-beta.0/
  PRE 2024-05-16-beta.0/
  PRE 2024-06-13-beta.0/
  PRE 2024-06-13-beta.1/
  PRE 2024-07-22.0/
```

- Check all themes available

```sh
$ aws s3 ls s3://overturemaps-us-west-2/release/2024-07-22.0/ --region us-west-2 --no-sign-request
  PRE theme=addresses/
  PRE theme=base/
  PRE theme=buildings/
  PRE theme=divisions/
  PRE theme=places/
  PRE theme=transportation/
```

## OpenStreetMap

This script just import tsv files into PostgreSQL.
You need to extract data before running this script.

```sh
bash building/import_osm_tsv.sh
```
