# User doc: Quality criteria and dashboard

This file provides information on how to use the Dashboard from scratch.
It includes: formatting and preparing the database, adding a new area, downloading and integrating data in the database, launching and using the Dashboard.

- [User doc: Quality criteria and dashboard](#user-doc-quality-criteria-and-dashboard)
- [Necessary components](#necessary-components)
  - [Database](#database)
    - [Schemas](#schemas)
    - [Download PostgreSQL and PostGIS](#download-postgresql-and-postgis)
    - [Create the database and schemas](#create-the-database-and-schemas)
  - [Python](#python)
    - [Virtual environment](#virtual-environment)
- [Quality assessment](#quality-assessment)
  - [Adding areas](#adding-areas)
  - [Custom database connection](#custom-database-connection)
  - [Download and process data](#download-and-process-data)
  - [Quality assessment criteria](#quality-assessment-criteria)
- [Dashboard](#dashboard)
  - [Custom environment variable (and app if needed)](#custom-environment-variable-and-app-if-needed)
  - [Run the application](#run-the-application)
  - [Use the application](#use-the-application)

# Necessary components

It was explained in other markdown, but to run the application, you will need mainly two components:

- A PostgreSQL database with PostGIS extension;

- Python

## Database

For the database, the information of the version are written on the [Readme.md](../Readme.md#database) file at the root of the repository, in the Database section.
This information is reminded here:

| **Tool** | Version |
| --- | --- |
| **PostgreSQL** | 16.2 |
| **PostGIS** | 3.4 |
| **PgRouting** | 3.6.0 |
| **PgAdmin** | 8.4 |
| **DuckDB** | 0.10.2 |

The database used in this repository is:

- `name`: `pgrouting`
- `host`: `127.0.0.1`
- `port`: `5432`
- `user`: `postgres`
- `password`: `postgres`

### Schemas

4 schemas are used in this database:

- `public`: Defaults schema, where PostGIS and PgRouting are installed.
It also means that to use these function, the `public.` prefix has to be used to avoid conflict and problems.
Also, the bounding box table is located in the public schema, to be used by the other one easily.

- `osm`: As the name indicates it, this schema contains all tables for OpenStreetMap data.

- `omf`: Same than the `osm` schema, but for OvertureMap Fundation data.

- `results`: The name also speaks for itself, this schema contains the different results of quality assessment.

Using only one database with multiple schemas is better than using multiple ones as it is way easier to use tables from different schemas than table from different database (at least it is the case with PostgreSQL).

### Download PostgreSQL and PostGIS

The repository to download PostgreSQL is here: https://www.postgresql.org/download/.
Please install the good version of PostgreSQL.
During the installation, you will be able to install PostGIS too, so please do it.

### Create the database and schemas

If you are using PgAdmin, you can easily add a new database.
Make sure to call it `pgrouting` to avoid having to change the database name in other files.
Otherwise, you can create a database in a command line, using psql:

Connect to the default database with the postgres user: `psql -U postgres`.

Enter your password.

Then, run this command to create the database: `CREATE DATABASE pgrouting;`, and run `\c pgrouting` to connect to the database.

Now you can run these queries to create the schemas and extensions needed:

```sql
CREATE SCHEMA osm;
CREATE SCHEMA omf;
CREATE SCHEMA results;
CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;
```

## Python

Python 3.12.3 has been used for the dashboard and data integration.
You can download Python here: https://www.python.org/downloads/ (you can change the os on this page too).
Install it and add it to the path if you are using Windows.

### Virtual environment

To prevent conflict with other applications, it is recommended to use a virtual environment to install only necessary dependencies in Python.
It is recommended to use an IDE as VSCode and do everything in VSCode terminal.
This way, you will be able to select your virtual environment for your python files.
If you want to add several virtual environments, you might want to create a folder where you will put the different virtual environments that you will create in the future.

Most of these commands are also written in the [command.md](command.md) file.

To do so, please run these commands, after downloading python:

**Create virtual environment**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Activate / deactivate**

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
pip install pip-tools && pip-compile Requirements\requirements.txt && pip install -r Requirements\requirements.txt
```

Of course, you have to adapt the path and names if you have changed anything.

Note: it is quite long to download everything, between 10 and 20 minutes probably, but it should be working.


# Quality assessment

## Adding areas

If you do not modify the python scripts, then the areas used are the one registered in the [bboxs.json](../Data/Bbox/bboxs.json) file.
Here is a sample of this file:

```json
{
    "bboxs" : [
        {
            "bbox":"139.74609375,35.67514744,139.83398438,35.74651226",
            "area":"Tokyo"
        },
        {
            "bbox":"137.63671875,34.66935855,137.72460938,34.7416125",
            "area":"Hamamatsu"
        },
        {
            "bbox":"139.83398438,34.95799531,139.921875,35.02999637",
            "area":"Tateyama"
        },
        {
            "bbox":"141.07765453,39.6823863,141.16554516,39.75375112",
            "area":"Morioka"
        },
        {
            "bbox":"130.68726409,32.72948989,130.77515472,32.80174385",
            "area":"Kumamoto"
        },
        {
            "bbox":"132.69418348,34.38622724,132.7820741,34.45848119",
            "area":"Higashihiroshima"
        },
        {
            "bbox":"2.289261,48.828241,2.395691,48.899046",
            "area":"Paris"
        }
    ]
}
```

If you want to modify these areas to download data on other places, you can modify this file.
The important part is to only add element in the `bboxs` array.
Each element have two mandatory attributes:

- `bbox`: Bounding box of the area, in a csv format. The data will be extracted from this area. You can use this [bounding box tool](https://boundingbox.klokantech.com/) to create easily a bounding box and you can directly copy and paste the result into a CSV format. For the moment, extended areas are not really available, so it is recommended to download bounding box of approximately 8 x 8 km. You cannot measure directly on the bounding box tool, but you can use [this website](https://www.freemaptools.com/measure-distance.htm) to measure approximatively your bounding box. Please make sure to have no space between numbers and comma.

- `name`: Name of the area. It should start by a capital letter, and the rest of it must be lower letters. No space or any special accent must be used. It is not convenient, but for the moment it is not possible to do otherwise. Also, the name should be unique, otherwise there will be problems in the process.

Every area in this file will be downloaded and used in the other scripts, so please remove those you do not want to download. If the area has already been downloaded, then there will not be any problem.

## Custom database connection

In the python files, the database connection can take two forms:

- `connection = utils.getConnection(database)`: Connection used for psycopg2 package;

- `engine = utils.getEngine(database)`: Engine used for geopandas (query to the database);

These functions are written in the [utils.py](../Python/utils.py) script.
They take the same arguments, and you can custom your connections with other parameter than the database name:

- `host`: Ip address for the database connection. The default is `127.0.0.1`
- `user`: Username for the database connection. The default is `postgres`.
- `password`: Password for the database connection. The default is `postgres`.
- `port`: Port for the connection. The default is `5432`.

Change these elements by adding them in the different files (such as `connection  = utils.getConnection(database, user = "myuser", password = "mypassword)` for instance)

## Download and process data

You can download the data corresponding to the areas you have chosen by using the [main.py](../Python/main.py) script.
You can change some attributes value in this file, such as:

- `database`: Name of the database to connect to. Defaults to `pgrouting`.

- `createBoundingBoxTable`: If True, will create the bounding box table, even if it has already been created. Defaults to `True`.

- `skipCheck`: If True, will recreate all layers for each area in the bounding box json file. Otherwise, will create layers only if they have not been created yet. Defaults to `False`.

- `ox.settings.overpass_settings`: This is a setting used to limit OSM data until a certain date. The default date is `2024-06-07T23:59:59Z`. You can change this date if you want, but it is better to change it with a data that is approximatively the same than the one corresponding to the overturemaps.py tool (the default date corresponds to the 2024-06-13-beta.1 release).

Normally, you should not need to change anyting else (such as template names for the layer, name of the schema or path of the bbox file etc.).
If you need to change them, feel free to do it, but these changes must be coherent between the different files.

You should then only have to run the script in a command line or using an IDE to download and store data in the database. It can take some time to download everything, but some things are printed in the console to let you know how much time it is taking.

## Quality assessment criteria

Once you have downloaded the data, you can run the necessary scripts to assess the quality of the different layer.
For the moment, the criteria are all on graph data. The python script is [graph_analysis.py](../Python/graph_analysis.py).

Here too, you can change some attributes value, such as:

- `fileName`: Name of the markdown file that will be produced. Defaults to `Automatic_result.md`.

- `pathSave`: Path to save the markdown file. If the folder does not exists, will return an error. Defaults to `./Data/Results/<fileName>`, where `<fileName>` is the variable mentioned previously.

- `database`: Name of the database to connect to. Defaults to `pgrouting`

- `bounding_box_table`: Name of the bounding box table in the database. Defaults to `bounding_box`.

Here too, you can change some other variable, but it is not recommended, especially because after you will have to change them in the dashboard too.

As the previous script, you should then only have to run the script in a command line or using an IDE to calculate those criteria. It can take some time to calculate everything, but the results are printed to the console.

# Dashboard

## Custom environment variable (and app if needed)

Before running the [app.py](../Python/Web/Dashboard/app.py) script and being able to manipulate the Dashboard, you can custom the environment variable to connect to the database.
You can change these variable in the [.env](../Python/Web/Dashboard/.env).

Also, if you have make some changes in the name of the layer, then you might want to change some the `template_layers_name` variable.
A dict with layer names for each dataset. Those names are the same than in the quality assessment process.

## Run the application

To run the application, as the requirements are already downloaded, you can just run this command:

```
shiny run .\Python\Web\Dashboard\app.py
```

Then, go on your browser and go to http://127.0.0.1:8000

## Use the application

To use it, you can check the `Help` panel of the application or see the [Shiny x Lonboard: Creating the dashboard](./tests-visualisation.md#shiny-x-lonboard-creating-the-dashboard) section of the [tests-visualisation.md](./tests-visualisation.md) file.