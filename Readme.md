# GeoDataCompare: Visualisation system to compare OpenStreetMap and Overture Maps Foundation data

|   |   |
|:---:|:---:|
| Main  | [![Test](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml/badge.svg?branch=main)](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml?query=branch%3Amain)  |
| Dev  | [![Test](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml/badge.svg?branch=dev)](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml?query=branch%3Adev)  |
| Last commit | [![Test](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml/badge.svg)](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml) |

- [GeoDataCompare: Visualisation system to compare OpenStreetMap and Overture Maps Foundation data](#geodatacompare-visualisation-system-to-compare-openstreetmap-and-overture-maps-foundation-data)
- [Documentation](#documentation)
- [Getting started](#getting-started)
  - [Install](#install)
    - [Necessary components](#necessary-components)
    - [Requirements](#requirements)
    - [Database](#database)
    - [Environment file](#environment-file)
  - [Using the scripts](#using-the-scripts)
    - [Download data](#download-data)
    - [Quality assessment](#quality-assessment)
    - [Running the application](#running-the-application)
- [Licenses](#licenses)
- [Credits](#credits)

[Overture Maps Foundation](https://overturemaps.org/) (OMF) released its first official release in July 2024, and as its schemas are structured and its data come from different sources, it is interesting to know what one can do with this data.
To answer this question, a comparison between it and [OpenStreetMap](https://www.openstreetmap.org/) (OSM), probably the most famous Open Source dataset for geoinformation data, has been made.

This project provides Python scripts to download and integrate data into a PostgreSQL database under a common model and assess its quality according to specific criteria, as well as a visualisation system based on Shiny for Python and LonBoard, two Python packages, to compare data with a dashboard.

This project was initially created for an internship at the [ENSG-Géomatique](https://ensg.eu/fr) school and is maintained by [LocationMind Inc.](https://locationmind.com/).

The information on the command line is provided for Windows users only.
It might be necessary to make small changes in the command line if you are a Mac or Linux user, for instance.

# Documentation

If you want more information about the data, quality criteria, or how to use the dashboard, you can refer to the [user documentation](./Documentation/user-doc.md).

If you want to modify a process or the dashboard (especially to add more criteria or other themes), please refer to the [developer documentation](./Documentation/dev-doc.md).

# Getting started

## Install

Whether it is for installing the dependencies, running the scripts, or the application, it is always assumed that the command line is at the root of the GitHub project.
This is important, as some scripts might not work if they are not run from the root of the project.

Also, depending on the OS you are using, you might need to change `\` to `/` or vice versa.
It should not be necessary to do so in the Python scripts, only in the command line.

### Necessary components

To run the application, it is necessary to have at least these two components:

- A PostgreSQL database with PostGIS and PgRouting extensions;
- Python

with these specific versions used for development and testing:

| **Tool** | Version |
| --- | --- |
| **PostgreSQL** | 16.2 |
| **PostGIS** | 3.4 |
| **PgRouting** | 3.6.0 |
| **Python** | 3.12.3 |


### Requirements

It is strongly recommended to use a Python virtual environment to download the necessary dependencies only within the virtual environment.
Here is how you can do this:

**Create virtual environment**
```cmd
python -m venv .venv
```

**Activate / Deactivate**

```cmd
.venv\Scripts\activate

.venv\Scripts\deactivate.bat
```

**Upgrade pip version**
```cmd
python.exe -m pip install --upgrade pip
```

**Install dependencies**

```cmd
pip install pip-tools && pip-compile Requirements\requirements.in && pip install -r Requirements\requirements.txt
```

### Database

Create a PostGIS database named `pgrouting`.

Then, to install the extensions and create the schemas according to the database model, run the [init.sql](./Data/init.sql) script in your database.
This is not a necessary step, as it should be run by the scripts as well, but it prevents errors to do it manually.

More information about the database can be found in the [Database section](./Documentation/user-doc.md#database) of the user documentation.

### Environment file

You can customise the [.env](./.env) file to configure your connection to the PostGIS database.
Initially, the parameter values are:

- `POSTGRES_DATABASE` (Name of the database): pgrouting
- `POSTGRES_HOST` (IP address of the host): 127.0.0.1
- `POSTGRES_USER` (Username): postgres
- `POSTGRES_PASSWORD` (Password): postgres
- `POSTGRES_PORT` (Port to connect to): 5432

This file is used in all scripts, whether for quality assessment or the dashboard.

## Using the scripts

### Download data

Use the [data_integration.py](src/Assessment/data_integration.py) file to download and integrate OSM and OMF data:

```cmd
python src\Assessment\data_integration.py
```

It uses the file containing the bounding box: [bboxs.json](./Data/bboxs.json).
Refer to the [user documentation](./Documentation/user-doc.md#adding-areas) for more information on how to add new areas.
You will also find information on how to configure the [data_integration.py](src/Assessment/data_integration.py/) file to force the data download or prevent the bounding box table from being recreated.

### Quality assessment

This script needs to be run after the data integration process, but before running the dashboard.
It is contained in the [quality_assessment.py](./src/Assessment/quality_assessment.py).
To run this script:

```cmd
python src\Assessment\quality_assessment.py
```

This script will create layers in the database for the visible ones and also a summary result.
The summary result is located in the [`Results`](./Results/) folder of the repository.

Once again, you can refer to the [user documentation](./Documentation/user-doc.md#quality-assessment-criteria) for more information about this script and how to configure it.


### Running the application

Run this command to launch the application:

```
shiny run .\Python\GeoDataCompare\app.py
```

You can then go to this link: http://127.0.0.1:8000

You can find more information about how to use the application in the `Help` section directly on the app.

# Licenses

OpenStreetMap data is under the [Open Data Commons Open Database License](https://opendatacommons.org/licenses/odbl/), while Overture Maps Foundation might have different licences (see [here](https://docs.overturemaps.org/attribution/)), but for the buildings and transportation themes, as OSM data is used, it is under the same licence.
Place data from OvertureMap is under the [Community Data License Agreement – Permissive – Version 2.0](https://cdla.dev/permissive-2-0/).

The visualisation platform and this project, in general, are under the [MIT License](./LICENSE.md).

# Credits

Without other explicit credits, all map data are from [OpenStreetMap](https://www.openstreetmap.org/copyright).
The data displayed on these maps are either from [OpenStreetMap](https://www.openstreetmap.org/copyright) or from [Overture Maps Foundation](https://docs.overturemaps.org/attribution/), depending on the picture.
Usually, the type of data (OSM, OMF, or both) is described in the context of the picture.