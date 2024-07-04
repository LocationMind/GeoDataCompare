# Test of different framework or tools for data visualisation

This document aims to do a review of the different frameowk or tools that could be used to visualise data, mainly for web visualisation.
The draft made for the final web application is provided [here](./OSM_Overture_vizualization_draft.20240628.pdf), or more easily here:

![Draft web application](./Images/Test-frameworks/draft_web_application.png)

- [Test of different framework or tools for data visualisation](#test-of-different-framework-or-tools-for-data-visualisation)
- [QGIS](#qgis)
- [Web visualisation](#web-visualisation)
  - [Apache-superset](#apache-superset)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Using apache-superset](#using-apache-superset)
    - [Review](#review)


# QGIS

With QGIs, it is quite easy to put two map viewer and to visualise data from two datasources using themes.
We can create as many themes as we want, and also it is possible to detach the second view from the application, which can be useful when working with two screens for example.
The image following shows the results we could have on Tokyo area when comparing the overlap indicator.
The map on theright is for OSM, and the other one is for OMF.

![Example of two views comparing overlap indicator on Tokyo](./Images/Test-frameworks/qgis_comparison_overlap_indicator.png)

It is possible to reduce or raise the scale factor, to synchronize the second map to the extent of the first one, or to show main canvas extent on the second map.

Using QGIs is quite easy for the visualisation, even though it is a bit annoying to create themes and stuff.
It is not possible to really interact with the second map, as all tools such as select, identify features etc. are only available for the main map.

For the visualisation, QGIs could be used.
However, it is not possible to add easily statistical information on QGIS main application.
Some work exists online for QGIS dashboards but they are not really as expected.
It should be possible to construct a QGIS plugin to create dashboard, but I do not know if it is worth it as it would take some time to create it,, and maybe using another technology for web visualisation would be more worthy.

# Web visualisation

## Apache-superset

[Apache-superset](https://superset.apache.org/) is, according to the website an "open-source modern data exploration and visualization platform".
The github project can be find [here](https://github.com/apache/superset).
Apache-superset is a powerful tool to create dashboard and is a no-code tool, meaning that aside from the installation and configuration, it is possible to create dashboard etc. without being a software developer.
It provides a full web architecture allowing multiple users with different roles, connection to multiple databases and more.
It is supported by the [Apache Software Fundation](https://www.apache.org/) and is under the [Apache 2.0 License](https://apache.org/licenses/LICENSE-2.0)

### Installation

To install apache-superset without using docker, the best is to use a python virtual environnment.
The link of the documentation to install with pip : https://superset.apache.org/docs/installation/pypi
For an unknown reason, I did not succeed to install apache-superset version 4.0.2 with python 3.12.4, so I had to install python 3.11 in order to install apache-superset.
Also, there were dependencies conflict between apache-superset and overturemaps python tool with the version of pyarrow so I made two requirements files, one for each version of python.
The [requirement_311.in](../requirements_311.in) file nclude apache-superset but not overturemaps and some other tools are not required with their last version as they are downloaded by apache-superset.
On the opposite side, the [requirement_312.in](../requirements_312.in) file does not include apache-superset but includes overturemaps python tool.

Please refer to the [python virtual environnment](./command.md#create-virtual-environnment) section to know how to create a python virtual environnment and how to install the necessary packages.

### Configuration

Once apache-superset installed, please run the following command to start apache-superset server: 

```
superset db upgrade

set FLASK_APP=superset
```

Then create a file `superset_config.py` and add a line in this file, as follow:

```python
SECRET_KEY = 'MYKEY'

# Non mandatory lines
SQL_MAX_ROW = 1000000
ROW_LIMIT = 1000000
```

The secret key is really week and should not be used as it is now with a production development, but it is enough for testing the application.

Save the file, copy the absolute path of this file and run this command:

```
set SUPERSET_CONFIG_PATH=your\absolute\path\to\superset_config.py
```

```
superset fab create-admin
```

Information will be required for you, but except for the password, you are not forced to change the value.
However, if you change the value of the admin name, it is possible that you might not see the different basic examples, according to some issues that I found online.

```
superset load_examples

superset init
```

Finally, start the server:

```
superset run -p 8088 --with-threads --reload --debugger
```

You can then access in your browser with `localhost:8088`.

### Using apache-superset

When you first connect, you will be asked to connect with the information provided before.

![Login page of apache superset](./Images/Test-frameworks/login_page_apache-superset.png)

You will arrive on the welcome page.
On this page, you can find the last dashboards, charts or saved queries that you made or used.
The part that interests us is to connect to PostgreSQL / PostGIS to try to add layer to a dashboard.
To do this, go on the settings anc click on Database connections.

![Welcome page of apache superset](./Images/Test-frameworks/main_page_apache-superset.png)

Then, you will be able to add a database and you will have to select PostgreSQL.
You will have to write the information of the database connection or you can enter directly the string to connect to the database : `postgresql://postgres:postgres@127.0.0.1:5432/pgrouting`, if all the information are the same than me (see [Database section](../Readme.md#database) of the readme for more information).

Then, go to `SQL/SQL Lab` to be able to create a SQL request and load the result to a dataset.
For a reason I do not know, apache-superset does not seem to be able to read directly into PostGIS table for the geom column.
Therefore, it is necessary to use GeoJSON format to add a geometry column.
Also, apache-superset seems to change the `"` into `'` when reading JSON, which is a problem because the GeoJSON because unvalid after this.
To prevent this, we have to use the `REPLACE` function to replace simple quote in double quotes.
You can write the following SQL query and click on RUN to run the query:

```sql
SELECT REPLACE(jsonb_build_object(
  'type',       'Feature',
  'id',         e.id,
  'geometry',   public.ST_AsGeoJSON(geom)::jsonb,
  'properties',   to_jsonb(e.* ))::text, '''', '\"') AS geojson
FROM omf.edge_with_cost_tokyo AS e;
```

![alt text](image.png)

![SQL Lab page with a preview of the results](./Images/Test-frameworks/sql_lab_apache-superset.png)

Once the query is finished, you can click on SAVE in the right side of the window and add the result to a new dataset.
Choose a name and click on SAVE & EXPLORE.

You will arrive on the charts page, where the chart source will have been automatically selected.
By default, the chart type is not the good one, so you will have to change it by clicking on `View all charts`, and then select `deck.gl Geojson`.
You will have to select the geojson column and a row limit.
I chose 50 000 rows, which is the maximum that you can choose by default.
It is probably possible to raise this limit by modifying the `superset_config.py` file.
Click on UPDATE CHART to see the result.
I do not know how to add a base map to the results, so for the moment I can only see the results as shown in the next image.

![Result with the deck.gl geojson chart](./Images/Test-frameworks/result_charts_apache-superset.png)

I did not try to create a dashboard but seeing the different examples, it seems to be possible and quite powerfull.

### Review

Apache-superset seems to be a really powerfull tool for dashboard and data analysis.
however, I am not sure that it is a good idea to use it with geospatial information, as it seems complicated to load easily the data and then to visualise it.
Depending on the other frameworks, this tool might be chosen.

The more convenient thing about apache-superset is that it is quite easy to use, and it seems to have a whole architecture already develop, including differents roles for different users.