# Test of different framework or tools for data visualisation

This document aims to do a review of the different frameowk or tools that could be used to visualise data, mainly for web visualisation.
The draft made for the final web application is provided [here](./OSM_Overture_vizualization_draft.20240628.pdf), or more easily here:

![Draft web application](./Images/Test-frameworks/draft_web_application.png)

- [Test of different framework or tools for data visualisation](#test-of-different-framework-or-tools-for-data-visualisation)
- [QGIS](#qgis)
- [Web visualisation](#web-visualisation)
  - [Virtual environments and requirements files](#virtual-environments-and-requirements-files)
  - [Apache-superset](#apache-superset)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Using apache-superset](#using-apache-superset)
    - [Review](#review)
  - [Streamlit](#streamlit)
    - [Installation](#installation-1)
    - [Using Streamlit](#using-streamlit)
    - [Review](#review-1)
  - [Plotly Dash](#plotly-dash)
    - [Installation](#installation-2)
    - [Using Dash](#using-dash)
    - [Review](#review-2)
- [GeoServer](#geoserver)
  - [Why using GeoServer?](#why-using-geoserver)
  - [Installing GeoServer with Docker](#installing-geoserver-with-docker)
  - [Configuring GeoServer](#configuring-geoserver)
    - [Adding layers with the app](#adding-layers-with-the-app)
    - [Adding layers with REST API](#adding-layers-with-rest-api)
    - [Review](#review-3)


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

## Virtual environments and requirements files

For all python packages, please refer to the [python virtual environnment](./command.md#create-virtual-environnment) section to know how to create a python virtual environnment and how to install the necessary packages using a requirements.in file.
Each package has its own requirements file, usually with a name like `requirements_<package>.in`.
All requirements files are in the [Requirements](../Requirements) folder.
It is better to use a different virtual environment for each package.

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
You can use the [`requirements_apache-superset.in`](../Requirements/requirements_apache-superset.in) to install it.

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

## Streamlit

[Streamlit](https://streamlit.io/) is, according to the website, a python package "that transform python scripts into interactive web apps in minutes, instead of week".
With Streamlit, it is possible to create dashboards and also web visualisation for geospatial information.
The github project can be find [here](https://github.com/streamlit/streamlit).
An example of what it is possible to do for geospatial information can be found on this [github page](https://github.com/opengeos/streamlit-geospatial) or directly in [this website](https://huggingface.co/spaces/giswqs/Streamlit).
This specific project is under the [MIT license](https://github.com/opengeos/streamlit-geospatial?tab=MIT-1-ov-file). 
Streamlit is under the [Apache 2.0 License](https://apache.org/licenses/LICENSE-2.0)

### Installation

You can find the Streamlit documentation [here](https://docs.streamlit.io/).

Streamlit is really easy to install, just with `pip install streamlit`, it is enough.

You can then run `streamlit hello` to have a demo app open in your browser.

### Using Streamlit

To use streamlit with a custom python file, create a pyton file and then run in a command line 

```
streamlit run your_script.py
```

You can click on the `Alway rerun` button in the right top of your web app to synchronise your python file and the app.
This way, every time you will make some change in your python file and save it, the app will rerun your script.
It allows to develop easily the application.

The documentation is really well done so the best is probably to use follow the recommendation of this documentation to understand how it works.

### Review

Streamlit is really easy to use, and the documentation is well done too.
It is possible to use maps and charts, and possibly to create dashboard too. 
However, using layer from postgis directly is complicated, as streamlit struggle to display the layer if there are too many entities.
When using a geodataframe, it is not possible to use `st.map(gdf)`, as this function needs to have a lat and lon column specified in the geodataframe.
As it is, I think that this tool is really powerful but maybe not adapted to be used with postgis directly.

It would be interesting to try to use a GeoServer for instance to query the map features in OGC Standards (WMS or WFS, depending on what we want to do), as it would probably be less demanding for the client.
But a GeoServer is a bit tricky to use and to set, so this question really needs to be think about carefully.

## Plotly Dash

[Plotly Dash](https://dash.plotly.com/) or simply Dash is, according to the website, "the original low-code framework for rapidly building data apps in Python".
With Dash, it is possible to create data apps to visualise and analyse data from different sources, but also to render maps.
The github project can be find [here](https://github.com/plotly/dash).
Dash is under the [MIT License](https://github.com/plotly/dash/blob/dev/LICENSE)

### Installation

You can find the documentation to install Dash [here](https://dash.plotly.com/installation).

Streamlit is really easy to install, just with `pip install dash`, it is enough.
For more possibilities, especially to use geospatial data, you can install geopandas via `pip install geopandas`.

### Using Dash

To use dash, you can create a python file and then run in a command line: 

```
python your_script.py
```

You do not have to repeat this process when you make change in your file.
Whenever you save your file, the script will rerun. 

### Review

With Pyplot Dash, it is possible to create quite easily different web applications, and even though it requires to have more knowledge about web language to know the different balises for instance, it probably gives more possibilities for the user to custom their apps.
Also, different kind of maps can be produced, most of them using MapBox and once again it is necessary to have the latitudes and longitudes in different columns, so it is not really possible to use PostGIS directly.
MapBox is free when using layers as OpenStreetMap for instance, so it is quite handy.
Also, it is possible to use WMS layers with MapBox, which can be useful and convenient if a geoserver is used for instance.
However, I did not succeed to import geojson layers get by a WMS Vector Tiles flows.
It is probably possible to succeed but I did not manage to use the bbox as it was supposed to be used, nor display the geojson in the map after.

PyPlot charts (not only maps) can be displayed with Streamlit too, using `st.plotly_chart(fig)`.

Here again, it would be interesting to try to use a GeoServer for instance to query the map features in OGC Standards (WMS or WFS, depending on what we want to do), as it would probably be less demanding for the client.

# GeoServer

[GeoServer](https://geoserver.org) is, according to the website, "an open source server for sharing geospatial data".
It is mainly used for spatial information, as it implements a lot of OGC Standards.
Among them, the Web Services (WMS, WFS, WMTS...) are particularly interesting.

These steps and some usages are inspired from a class project that I did this year.
The GitHub associated with this project can be find [here](https://github.com/VGiudicelli1/TSI_stage/tree/dev).

## Why using GeoServer?

After testing Apache-Superset, Streamlit and Plotly Dash, it is quite obvious that whatever the package used, the amount of data is too important to try to use it directly from PostGIS.
By connecting the database in local to GeoServer, it is then possible to request PostGIS data with OGC Standards Web Services, particularly WMS or WFS.
It is way ligther for the client, as only images are sent.
Of course, it is complicated then to apply different styles, or at least not as easy as with vector layers directly.
But because it is WMS or WFS flows, most of the libraries can used flows sent by GeoServer.

## Installing GeoServer with Docker

GeoServer is very powerful, but installing and maintening it can be a bit complicated.
However, using Docker installing GeoServer is not that complicated.
Indeed, there are offical release of GeoServer images up-to-date, and it can be easily installed on local devices only for the moment.
The one that we use is `docker.osgeo.org/geoserver:2.25.2`.
You can find the website [here]()

To install it, it is really easy because the [docker-compose.yml](..\GeoServer\docker-compose.yml) file has already been created.
For Windows user, please make sure to install and start [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) in order to use docker.

Once Docker Desktop is installed and started, run this command line to create the image and containers:

```cmd
docker-compose -f .\GeoServer\docker-compose.yml up -d
```

Of course, if your file is in another location, please change it in the command too.

Once the image has been pulled and the container has been created, you can access geoserver at [`http://localhost:8080/geoserver/`](http://localhost:8080/geoserver/).
You should be on a page that looks like this:

![Index page of GeoServer](./Images/Test-frameworks/index_geoserver.png)

## Configuring GeoServer

Even though there are environment variables in the docker-compose file for the username and password, it seems that it does not work.
Therefore, to connect please use `admin`,`geoserver` respectively for `username` and `password`.
You should arrive on this page:

![Index page after connect](./Images/Test-frameworks/after_connect_geoserver.png)

To add layers, there are two possibilities:

- [Adding them with the app](#adding-layers-with-the-app)

- [Using REST API to add them](#adding-layers-with-rest-api)

### Adding layers with the app

First, add a **Workspace**.
To do so, click on `Workspaces` in the `Data` section.
Then, click on `Add new workspace` and enter a name and an uri.
You can click on `Default Workspace` if you want (it is not mandatory ut it is good to have one default workspace).
The URI does not have to be a real URI pointing to a real object.
I chose `http://locationmind.com/test` for my URI, with `test` being the name of my workspace.

Then, we need to add a store, i.e. our database connection.
Click on `Stores` in the `Data` section.
Then, click on `Add new Store` and on `PostGIS` to add a PostGIS database.
Choose your workspace, the data source name and the description.
For the `Data Source Name`, it is better to avoid using spaces, dashes or any "special" character and rather using underscores.
This does not apply for the description.

The most important parameter is the host.
As a docker container is used, it is not possible to put `localhost` or `127.0.0.1` for the host.
Instead, please put `host.docker.internal` in order to connect to your database in local.
The other parameters are the one from your database, and the schema can be important too if you have several schemas with different layers inside.

![Connection parameters for the PostGIS connection](./Images/Test-frameworks/connection_parameter_db_geoserver.png)


Then, click on save, and you shoud arrive to a page for adding a new layer, like this:

![Adding a new layer](./Images/Test-frameworks/add_new_layer_geoserver.png)

You can also access to this page by clicking on `Layers` in the `Data` section, and then on `Add a new layer`.
You simply have to choose a store with the select box, and you will find the same page.

Choose the layer that you want to add and click on publish.
On the new page, you can add metadata or change features properties for instance.
To avoid confusion with layers from different sources (i.e. to make the difference betwwen OSM and OMF layers), you can rename the name and title of the layer by adding at the end or at the beginning of the name the datasource where it comes from (`edge_with_cost_tokyo_osm` instead of `edge_with_cost_tokyo` for instance).
On the `Bounding Boxes` section, please click on `Compute from native bounds` to add the bounding box of the layer.

![Bounding box section when adding a layer](./Images/Test-frameworks/bounding_box_section_geoserver.png)

Then, simply click on save to add the layer.

You can see what it looks like by clicking on `Layer Preview` in the `Data` section.
Click on the format that you want to visualise the layer.

The layer is then accessible via WMS for instance using a HTML request like this:

`http://localhost:8080/geoserver/test/wms?service=WMS&version=1.1.0&request=GetMap&layers=<workspace>:<layer_name>&bbox=<bbox>&width=256&height=256&srs=EPSG:4326&styles=&format=<desired_format>`

With:

- `<workspace>`: Name of your workspace (`test` in this example);
- `<layer_name>`: Name of the layer, as you have chosen it, so not necessarely the name of the layer in the database (`edge_with_cost_tokyo_osm` in this example);
- `<bbox>`: Bbox in `W,S,E,N` format (`139.74609375,35.67514419555664,139.833984375,35.74651336669922` for instance, to see over the tokyo area);
- `<desired_format>`: Depending on the format you want (`application/openlayers` to see with openlayer, or `image/png` to have a png image for instance).

Please check the [geoserver website](https://docs.geoserver.org/stable/en/user/services/wms/reference.html) to have more information about WMS requests.

### Adding layers with REST API

All of these steps are also available using HTML request with the REST API of GeoServer.
More information about the GeoServer REST API can be find [here](https://docs.geoserver.org/latest/en/user/rest/index.html).

The [`init.sh`](../GeoServer/init.sh) file contains all the request necessary to add two layers from OMF.
The database connection paramaters are located in the [`connect_omf.xml`](../GeoServer/connect_omf.xml) file, so please change parameters if there are not the same.
If you change the store name, you will have to change it in the queries too.
It is the same for the username and password in the `-u admin:geoserver` option.

**Add a workspace**

```bash
curl -v -u admin:geoserver -POST -d "<workspace><name>test</name></workspace>" -H "Content-type: text/xml"  http://localhost:8080/geoserver/rest/workspaces
```

**Add a store**

```bash
curl -v -u admin:geoserver -POST -T .\connect_omf.xml -H "Content-type: text/xml" http://localhost:8080/geoserver/rest/workspaces/test/datastores
```

**Add a layer**

```bash
curl -v -u admin:geoserver -XPOST -H "Content-type: text/xml" -d "<featureType><name>edge_with_cost_tokyo_omf</name><nativeName>edge_with_cost_tokyo</nativeName><title>edge_with_cost_tokyo_omf</title></featureType>" http://localhost:8080/geoserver/rest/workspaces/test/datastores/pgrouting_omf/featuretypes
```

The nativeName tag must correspond to the table name in the database.
You can change the rest as you want.

**Change roles for all users**

```bash
curl -v -u admin:geoserver -POST -H  "accept: application/json" -H  "content-type: application/xml" -d "<rules><rule resource=\"PgRouting_OMF.edge_with_cost_tokyo .r\">*</rule></rules>" http://localhost:8080/geoserver/rest/security/acl/layers

```

This last command is not mandatory, but it was present in the original file so I let it here.

### Review

GeoServer is really powerful and with the REST API, it is possible to add multiple layers quite easily.
It requires space and if it comes to be used by multiple users, then it will require also more power.
However, with the different way to query the features (WMS to render and WFS to display information).
There are more ways to configure GeoServer, especially for the WMS / WMTS flows, with specific values and parameters for each layer.
Also, it is possible to change the style of WMS layers, and with the vectortiles extension, it should be possible to query vector tiles to display them.
GeoServer, or another open-source solution with the same features, is probably the best way to make the desire web application.