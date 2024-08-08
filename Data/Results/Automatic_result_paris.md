# Quality criterias result between OSM and OMF datasets

The test were run on 24/07/2024 14:28, using the 2024-06-13-beta.1 release of OvertureMap data and the OSM data until 2024/06/07.

## General results

| **Criterion**                                | **Area**   |   **OSM Value** |   **OMF Value** |   **Difference (abs)** |
|----------------------------------------------|------------|-----------------|-----------------|------------------------|
| **1. Number of nodes**                       | *Paris*    |       124312    |        97329    |               26983    |
| **2. Number of edges**                       | *Paris*    |       170612    |       142409    |               28203    |
| **3. Total length (km)**                     | *Paris*    |         3694    |         3614    |                  80    |
| **4. Number of connected components**        | *Paris*    |         1311    |         1185    |                 126    |
| **5. Number of strong connected components** | *Paris*    |         1860    |         1911    |                  51    |
| **6. Number of isolated nodes**              | *Paris*    |           18    |            0    |                  18    |
| **7. Overlap indicator (%)**                 | *Paris*    |           97.97 |           95.96 |                   2.01 |
| **8. Number of corresponding nodes**         | *Paris*    |        95623    |        95623    |                   0    |
| **9. Percentage of corresponding nodes (%)** | *Paris*    |           76.92 |           98.25 |                  21.33 |

## Specific results

### Total kilometer of roads by class

#### *Paris*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     23.75 |                        808 |                     23.31 |                        655 |
| crosswalk     |                      0    |                          0 |                     22.5  |                       4831 |
| cycleway      |                    171.31 |                       5273 |                    170.32 |                       4906 |
| driveway      |                     17.2  |                        698 |                     16.46 |                        564 |
| footway       |                    571.55 |                      56086 |                   1014.17 |                      56361 |
| living_street |                     44.79 |                       1542 |                     44.54 |                       1477 |
| motorway      |                      0.03 |                          2 |                      0    |                          0 |
| parking_aisle |                     30.29 |                       1114 |                     27.77 |                        955 |
| path          |                      9.75 |                        315 |                      9.57 |                        307 |
| pedestrian    |                    100.02 |                       3415 |                    100.29 |                       3158 |
| primary       |                    138.09 |                       4009 |                    133.54 |                       3674 |
| residential   |                    545.5  |                      17318 |                    543.61 |                      16903 |
| secondary     |                    107.56 |                       3552 |                    111.46 |                       3518 |
| sidewalk      |                   1559.95 |                      60571 |                   1038.15 |                      31755 |
| steps         |                     39.24 |                       4905 |                     24.39 |                       3413 |
| tertiary      |                    101.97 |                       3505 |                    102.19 |                       3364 |
| track         |                      0.72 |                          7 |                      0.72 |                          5 |
| trunk         |                      9.34 |                         69 |                      6.87 |                         33 |
| unclassified  |                     28.42 |                       1023 |                     27.69 |                        967 |
| unknown       |                    193.83 |                       6400 |                    195.63 |                       5563 |
