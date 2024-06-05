# Internship program reformulation

This internship purpose is to compare and assess data quality on 3 different open sources data.
It will only focuses on road and building data.
The 3 main sources data are [OpenStreetMap](https://www.openstreetmap.org/), [Overture Map](https://overturemaps.org/) and [Daylight](https://daylightmap.org/).
It is possible to split the internship in 3 major parts, in the following order :

1. Create a commun data model and select different criterias to assess data quality, without data references.

2. Create and implement processes to upload and update data, and assess data quality. Quantitatives results are expected to assess as best as possible the quality.

3. Creating a visualisation system to compare different data sources and their quality - for specific criterias. It has not been decided yet if it will be on a web service or on QGIS.

Each part can then be split into tasks and subtasks :

1. **Modelisation and criterias selection**

    1. *Data modelisation*

        1. Check the existing schemas given by the different sources for roads and buildings.

        2. Compare those schemas and create an unique model for roads and buildings. This model must be created according to the existing schemas, so the mapping between source data and the model is possible.

        3. Choose which DBMS will be used in the rest of the internship - PostgreSQL with PostGIS extension / DuckDB / MariaDB etc.
    
    2. *Data comparison*

        1. Get data for a specific region and visualise it on QGIS
        
        2. Compare data between them, and check what is missing / added in each dataset.

    3. *Quality criterias*

        1. Search papers about assessing quality of open data.

        2. If criterias that seems important for us are not mentionned or explained in the paper, it will be necessary to create them with their assessing method. 

        3. When multiple criterias will have been targeted, prioritise which ones to keep, according to the company's needs and to the data.

2. **Processes implementation**

    1. *Uploading data*

        1. Create an algorithm to get data automatically for a specific region. The implentation will be of course different according to the data source.

        2. Create an algorithm to import data in the database, according to the model previously chosen.

    2. *Updating data*

        1. If data is to be updated monthly, then it is important to check how this process will be made.
        One can easily think that truncate all datas and just replace them by fresh data would be the solution, but it is only true if the data is not oftenly used nor modified.
        Indeed, for instance, if road data are modified to be intergrated with data from other sources, then there is a risk that the id of a road changes if the road has been updated in the month.
        For this reason, it is important to consider the update as a major task for this internship.
        Of course, it will depend on the use of the data, so it may not be necessary to have an update process.
    
    3. *Assessing data quality*

        1. Before assessing data quality, different regions for our test will have to be taken.
        It is important to have at least a rural and an urban region, in order to have an accurate representation of the landscape.
        Also, it would be useful to have data where it is possible to know if its quality is good or not, to validate the processes.
        If it is not possible to obtain them directly, it will be probably necessary to create this manually.

        2. Creating data assessment processes for each creteria selected in part 1.3.
        Thanks to the model selected and the database, it will not be necessary to create an algorithm for each data source.

        3. Compare and comment those results.
    
3. **Visualisation system**

    1. Choose between an online system or directly using QGIS.

    2. In any cases, accessing data will be a challenge, as most of them will be stored locally, so it is not accessible to everyone.
    Then, how doing so?
    For instance, it would be possible to use a geoserver, that would allow to process a lot of data and accessing it from different locations.
    But setting up a geoserver for several people is not an easy task (especially handling permissions for different groups), so it may not be a viable solution.

    3. If it is a QGIS plugin or code, then sharing it will be easy.
    However, if it is a Web Service for data visualisation, then the access should be granted to authorised persons only.

    4. The visualisation system should be able to compare original data and assessed data. If possible, the system should implement a choice for which criteria it should display.

Most of the code will be produced using Python, as it is a powerful language to process geographical data.