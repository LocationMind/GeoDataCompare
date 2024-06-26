
# Quality criterias result between OSM and OMF datasets

The test were run on 26/06/2024 16:25, using the 2024-06-13-beta.1 release of OvertureMap data and the OSM data until 2024/06/07.

## General results

| **Criterion**                                | **Area**           | **OSM Value**   | **OMF Value**   |
|----------------------------------------------|--------------------|-----------------|-----------------|
| **1. Number of nodes**                       | *Hamamatsu*        | 44483           | 39614           |
| **1. Number of nodes**                       | *Higashihiroshima* | 14057           | 13138           |
| **1. Number of nodes**                       | *Kumamoto*         | 19010           | 18213           |
| **1. Number of nodes**                       | *Morioka*          | 17644           | 16737           |
| **1. Number of nodes**                       | *Tateyama*         | 8486            | 7886            |
| **1. Number of nodes**                       | *Tokyo*            | 110184          | 101426          |
| **2. Number of edges**                       | *Hamamatsu*        | 32765           | 27890           |
| **2. Number of edges**                       | *Higashihiroshima* | 10414           | 9502            |
| **2. Number of edges**                       | *Kumamoto*         | 13614           | 12824           |
| **2. Number of edges**                       | *Morioka*          | 12599           | 11710           |
| **2. Number of edges**                       | *Tateyama*         | 6808            | 6207            |
| **2. Number of edges**                       | *Tokyo*            | 74902           | 66382           |
| **3. Total length (km)**                     | *Hamamatsu*        | 1770.0          | 1756.0          |
| **3. Total length (km)**                     | *Higashihiroshima* | 942.0           | 912.0           |
| **3. Total length (km)**                     | *Kumamoto*         | 1298.0          | 1286.0          |
| **3. Total length (km)**                     | *Morioka*          | 1150.0          | 1129.0          |
| **3. Total length (km)**                     | *Tateyama*         | 627.0           | 605.0           |
| **3. Total length (km)**                     | *Tokyo*            | 3204.0          | 3161.0          |
| **4. Number of connected components**        | *Hamamatsu*        | 53              | 52              |
| **4. Number of connected components**        | *Higashihiroshima* | 28              | 23              |
| **4. Number of connected components**        | *Kumamoto*         | 108             | 116             |
| **4. Number of connected components**        | *Morioka*          | 31              | 34              |
| **4. Number of connected components**        | *Tateyama*         | 25              | 18              |
| **4. Number of connected components**        | *Tokyo*            | 253             | 256             |
| **5. Number of strong connected components** | *Hamamatsu*        | 101             | 105             |
| **5. Number of strong connected components** | *Higashihiroshima* | 67              | 38              |
| **5. Number of strong connected components** | *Kumamoto*         | 130             | 158             |
| **5. Number of strong connected components** | *Morioka*          | 100             | 60              |
| **5. Number of strong connected components** | *Tateyama*         | 32              | 20              |
| **5. Number of strong connected components** | *Tokyo*            | 593             | 594             |
| **6. Number of isolated nodes**              | *Hamamatsu*        | 12              | 0               |
| **6. Number of isolated nodes**              | *Higashihiroshima* | 8               | 0               |
| **6. Number of isolated nodes**              | *Kumamoto*         | 10              | 0               |
| **6. Number of isolated nodes**              | *Morioka*          | 8               | 0               |
| **6. Number of isolated nodes**              | *Tateyama*         | 3               | 0               |
| **6. Number of isolated nodes**              | *Tokyo*            | 16              | 0               |
| **7. Number of strong connected components** | *Hamamatsu*        | 100.00 %        | 95.90 %         |
| **7. Number of strong connected components** | *Higashihiroshima* | 99.98 %         | 91.16 %         |
| **7. Number of strong connected components** | *Kumamoto*         | 99.97 %         | 94.82 %         |
| **7. Number of strong connected components** | *Morioka*          | 99.95 %         | 93.13 %         |
| **7. Number of strong connected components** | *Tateyama*         | 100.00 %        | 91.58 %         |
| **7. Number of strong connected components** | *Tokyo*            | 99.50 %         | 94.93 %         |
| **8. Number of corresponding nodes**         | *Hamamatsu*        | 44480           | 40008           |
| **8. Number of corresponding nodes**         | *Higashihiroshima* | 14027           | 13300           |
| **8. Number of corresponding nodes**         | *Kumamoto*         | 19004           | 18545           |
| **8. Number of corresponding nodes**         | *Morioka*          | 17602           | 17025           |
| **8. Number of corresponding nodes**         | *Tateyama*         | 8484            | 8014            |
| **8. Number of corresponding nodes**         | *Tokyo*            | 109840          | 102264          |
| **9. Percentage of corresponding nodes**     | *Hamamatsu*        | 100.0 %         | 99.96 %         |
| **9. Percentage of corresponding nodes**     | *Higashihiroshima* | 99.89 %         | 99.95 %         |
| **9. Percentage of corresponding nodes**     | *Kumamoto*         | 99.99 %         | 99.91 %         |
| **9. Percentage of corresponding nodes**     | *Morioka*          | 99.9 %          | 99.95 %         |
| **9. Percentage of corresponding nodes**     | *Tateyama*         | 100.0 %         | 99.96 %         |
| **9. Percentage of corresponding nodes**     | *Tokyo*            | 99.75 %         | 99.97 %         |

## Specific results

### Total kilometer of roads by type (before mapping)

#### *Hamamatsu*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0    |                          0 |                     13.92 |                        320 |
| crosswalk     |                      0    |                          0 |                      8.41 |                       1254 |
| driveway      |                      0    |                          0 |                     19.36 |                        579 |
| footway       |                    283.01 |                      10352 |                    236.27 |                       5340 |
| motorway      |                      6.64 |                         23 |                      7.61 |                         18 |
| motorway_link |                      2.17 |                         16 |                      0    |                          0 |
| parking_aisle |                      0    |                          0 |                    107.63 |                       4769 |
| path          |                     37.02 |                        991 |                     36.12 |                        838 |
| pedestrian    |                      2.43 |                         41 |                      2.42 |                         36 |
| primary       |                     39    |                        874 |                     38.71 |                        840 |
| primary_link  |                      0.02 |                          2 |                      0    |                          0 |
| residential   |                    586.16 |                      12876 |                    584.39 |                      12638 |
| secondary     |                     23.59 |                        663 |                     23.55 |                        642 |
| service       |                    202.71 |                       7909 |                      0    |                          0 |
| sidewalk      |                      0    |                          0 |                     36.23 |                        745 |
| steps         |                      4.19 |                        396 |                      4.21 |                        390 |
| tertiary      |                    179.85 |                       4203 |                    178.6  |                       4045 |
| tertiary_link |                      0.02 |                          4 |                      0    |                          0 |
| track         |                     66.45 |                        734 |                     65.82 |                        659 |
| trunk         |                     24.47 |                        510 |                     26.32 |                        525 |
| trunk_link    |                      2.1  |                         23 |                      0    |                          0 |
| unclassified  |                    310.04 |                       4866 |                    308.62 |                       4533 |
| unknown       |                      0    |                          0 |                     56.96 |                       1443 |

#### *Higashihiroshima*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0    |                          0 |                      0.49 |                          8 |
| crosswalk     |                      0    |                          0 |                      1.93 |                        245 |
| cycleway      |                      2.93 |                         30 |                      2.93 |                         28 |
| driveway      |                      0    |                          0 |                      4.96 |                        175 |
| footway       |                     95.8  |                       2036 |                     48.95 |                       1042 |
| motorway      |                     13.98 |                         27 |                      3.77 |                         10 |
| motorway_link |                      2.53 |                         12 |                      0    |                          0 |
| parking_aisle |                      0    |                          0 |                     23.05 |                        754 |
| path          |                     50.36 |                        589 |                     46.84 |                        543 |
| pedestrian    |                      0.49 |                         11 |                      0.49 |                         11 |
| primary       |                     13.56 |                        135 |                     13    |                        122 |
| residential   |                    331.65 |                       4785 |                    328.02 |                       4599 |
| secondary     |                     23.23 |                        289 |                     22.92 |                        274 |
| service       |                     92.14 |                       2215 |                      0    |                          0 |
| sidewalk      |                      0    |                          0 |                     43.96 |                        523 |
| steps         |                      1.82 |                        140 |                      1.73 |                        126 |
| tertiary      |                     68.91 |                        949 |                     68.25 |                        880 |
| tertiary_link |                      0.07 |                          4 |                      0    |                          0 |
| track         |                     22.16 |                        180 |                     21.2  |                        161 |
| trunk         |                     31.97 |                        297 |                     39.01 |                        315 |
| trunk_link    |                      8.8  |                         62 |                      0    |                          0 |
| unclassified  |                    180.77 |                       2296 |                    176.36 |                       2105 |
| unknown       |                      0    |                          0 |                     63.16 |                       1217 |

#### *Kumamoto*:

| class          |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|----------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley          |                      0    |                          0 |                     21.14 |                        395 |
| bus_stop       |                      0.03 |                          2 |                      0    |                          0 |
| busway         |                      0.36 |                          9 |                      0    |                          0 |
| crosswalk      |                      0    |                          0 |                      2.41 |                        214 |
| cycleway       |                      4.27 |                         32 |                      4.27 |                         32 |
| driveway       |                      0    |                          0 |                      2.54 |                         53 |
| footway        |                     83.86 |                       1656 |                     55.24 |                        897 |
| motorway       |                      0.05 |                          1 |                      0    |                          0 |
| motorway_link  |                      0.06 |                          1 |                      0    |                          0 |
| parking_aisle  |                      0    |                          0 |                      7.22 |                        200 |
| path           |                     44.41 |                        347 |                     43.83 |                        306 |
| pedestrian     |                      2.25 |                         70 |                      2.23 |                         58 |
| primary        |                     29.75 |                        345 |                     28.75 |                        331 |
| primary_link   |                      0.04 |                          2 |                      0    |                          0 |
| residential    |                    280.2  |                       4204 |                    277.02 |                       4108 |
| secondary      |                     43.02 |                        514 |                     42.98 |                        482 |
| secondary_link |                      0.11 |                          3 |                      0    |                          0 |
| service        |                     88.23 |                       1626 |                      0    |                          0 |
| sidewalk       |                      0    |                          0 |                     25.53 |                        307 |
| steps          |                      0.95 |                         93 |                      0.95 |                         93 |
| tertiary       |                    109.26 |                       1490 |                    110.63 |                       1511 |
| tertiary_link  |                      1.72 |                         38 |                      0    |                          0 |
| track          |                     60.22 |                        314 |                     59.83 |                        310 |
| trunk          |                     50.07 |                        474 |                     50.89 |                        436 |
| trunk_link     |                      0.96 |                         11 |                      0    |                          0 |
| unclassified   |                    497.81 |                       7778 |                    492.83 |                       7529 |
| unknown        |                      0    |                          0 |                     57.05 |                        951 |

#### *Morioka*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0    |                          0 |                     19.84 |                        445 |
| crosswalk     |                      0    |                          0 |                      5.56 |                        740 |
| cycleway      |                      8.16 |                         26 |                      7.38 |                         17 |
| driveway      |                      0    |                          0 |                      0.35 |                          8 |
| footway       |                    131.21 |                       3108 |                     59.28 |                       1076 |
| motorway      |                     15.88 |                         66 |                     15.56 |                         45 |
| motorway_link |                      6.78 |                         60 |                      0    |                          0 |
| parking_aisle |                      0    |                          0 |                      6.29 |                        162 |
| path          |                     33.78 |                        453 |                     33.17 |                        434 |
| pedestrian    |                      9.43 |                        157 |                      9.38 |                        142 |
| primary       |                     25.41 |                        272 |                     25.16 |                        255 |
| primary_link  |                      0.04 |                          3 |                      0    |                          0 |
| residential   |                    335.67 |                       4598 |                    333.05 |                       4501 |
| secondary     |                     14.2  |                        209 |                     14.14 |                        197 |
| service       |                     68.43 |                       1537 |                      0    |                          0 |
| sidewalk      |                      0    |                          0 |                     63.83 |                        981 |
| steps         |                      2.98 |                        155 |                      2.98 |                        152 |
| tertiary      |                    136.2  |                       1835 |                    135.3  |                       1755 |
| tertiary_link |                      0.44 |                         12 |                      0    |                          0 |
| track         |                     25.59 |                        169 |                     24.56 |                        157 |
| trunk         |                     38.42 |                        381 |                     35.8  |                        302 |
| trunk_link    |                      0.35 |                          4 |                      0    |                          0 |
| unclassified  |                    296.48 |                       4599 |                    294.31 |                       4463 |
| unknown       |                      0    |                          0 |                     42.24 |                        905 |

#### *Tateyama*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0    |                          0 |                     33.34 |                        501 |
| crosswalk     |                      0    |                          0 |                      2.66 |                        528 |
| driveway      |                      0    |                          0 |                      3.59 |                         70 |
| footway       |                     13    |                        790 |                      7.54 |                        146 |
| parking_aisle |                      0    |                          0 |                      6.19 |                        136 |
| path          |                     64.58 |                        344 |                     53.54 |                        287 |
| pedestrian    |                      0.05 |                          2 |                      0.05 |                          2 |
| primary       |                      6.09 |                         67 |                      5.95 |                         57 |
| residential   |                    264.43 |                       3883 |                    261.7  |                       3672 |
| secondary     |                     24.72 |                        473 |                     24.59 |                        441 |
| service       |                     59.43 |                       1043 |                      0    |                          0 |
| sidewalk      |                      0    |                          0 |                      2.57 |                         41 |
| steps         |                      0.46 |                         23 |                      0.46 |                         22 |
| tertiary      |                     36.7  |                        504 |                     35.07 |                        485 |
| track         |                    104.91 |                        775 |                    102.47 |                        680 |
| trunk         |                     23.3  |                        288 |                     22.82 |                        259 |
| unclassified  |                     28.56 |                        294 |                     25.98 |                        273 |
| unknown       |                      0    |                          0 |                     16.02 |                        286 |

#### *Tokyo*:

| class          |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|----------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley          |                      0    |                          0 |                    143.42 |                       3976 |
| bridleway      |                      0.02 |                          1 |                      0.02 |                          1 |
| busway         |                      0.17 |                         10 |                      0    |                          0 |
| corridor       |                      0.13 |                         15 |                      0    |                          0 |
| crosswalk      |                      0    |                          0 |                     43.44 |                       6014 |
| cycleway       |                     11.24 |                        191 |                     10.56 |                        181 |
| driveway       |                      0    |                          0 |                     12.29 |                        453 |
| elevator       |                      0.05 |                          8 |                      0    |                          0 |
| footway        |                   1101.96 |                      47925 |                    690.92 |                      25827 |
| living_street  |                      0.16 |                          7 |                      0.16 |                          7 |
| motorway       |                     63.21 |                        176 |                     72.24 |                        196 |
| motorway_link  |                     23.97 |                        210 |                      0    |                          0 |
| parking_aisle  |                      0    |                          0 |                     15.05 |                        564 |
| path           |                     34.52 |                       1049 |                     34.29 |                       1028 |
| pedestrian     |                     27.87 |                        827 |                     27.75 |                        785 |
| primary        |                    103.23 |                       2647 |                    104.25 |                       2547 |
| primary_link   |                      2.56 |                         62 |                      0    |                          0 |
| residential    |                    693.14 |                      20895 |                    692.35 |                      20807 |
| road           |                      0.13 |                          3 |                      0    |                          0 |
| secondary      |                    130.65 |                       3524 |                    131.69 |                       3405 |
| secondary_link |                      2    |                         60 |                      0    |                          0 |
| service        |                    300.4  |                       8793 |                      0    |                          0 |
| sidewalk       |                      0    |                          0 |                    348.61 |                       8820 |
| steps          |                     20.71 |                       2056 |                     19.43 |                       1855 |
| tertiary       |                    232.88 |                       7583 |                    233.91 |                       7479 |
| tertiary_link  |                      2.14 |                         67 |                      0    |                          0 |
| trunk          |                     57.57 |                       1461 |                     58.9  |                       1440 |
| trunk_link     |                      1.89 |                         50 |                      0    |                          0 |
| unclassified   |                    393.12 |                      12564 |                    392.14 |                      12452 |
| unknown        |                      0    |                          0 |                    129.11 |                       3589 |

### Total kilometer of roads by type (after mapping)

#### *Hamamatsu*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     14.44 |                        340 |                     13.92 |                        320 |
| bridleway     |                      0    |                          0 |                      0    |                          0 |
| crosswalk     |                      0    |                          0 |                      8.41 |                       1254 |
| cycleway      |                      0    |                          0 |                      0    |                          0 |
| driveway      |                     19.48 |                        606 |                     19.36 |                        579 |
| footway       |                     74.45 |                       5736 |                    236.27 |                       5340 |
| living_street |                      0    |                          0 |                      0    |                          0 |
| motorway      |                      8.81 |                         39 |                      7.61 |                         18 |
| parking_aisle |                    109.03 |                       5474 |                    107.63 |                       4769 |
| path          |                     37.02 |                        991 |                     36.12 |                        838 |
| pedestrian    |                      2.43 |                         41 |                      2.42 |                         36 |
| primary       |                     39.02 |                        876 |                     38.71 |                        840 |
| residential   |                    586.16 |                      12876 |                    584.39 |                      12638 |
| secondary     |                     23.59 |                        663 |                     23.55 |                        642 |
| sidewalk      |                    208.57 |                       4616 |                     36.23 |                        745 |
| steps         |                      4.19 |                        396 |                      4.21 |                        390 |
| tertiary      |                    179.86 |                       4207 |                    178.6  |                       4045 |
| track         |                     66.45 |                        734 |                     65.82 |                        659 |
| trunk         |                     26.57 |                        533 |                     26.32 |                        525 |
| unclassified  |                    310.04 |                       4866 |                    308.62 |                       4533 |
| unknown       |                     59.77 |                       1489 |                     56.96 |                       1443 |

#### *Higashihiroshima*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0.49 |                          8 |                      0.49 |                          8 |
| bridleway     |                      0    |                          0 |                      0    |                          0 |
| crosswalk     |                      0    |                          0 |                      1.93 |                        245 |
| cycleway      |                      2.93 |                         30 |                      2.93 |                         28 |
| driveway      |                      4.96 |                        174 |                      4.96 |                        175 |
| footway       |                     30.41 |                       1154 |                     48.95 |                       1042 |
| living_street |                      0    |                          0 |                      0    |                          0 |
| motorway      |                     16.51 |                         39 |                      3.77 |                         10 |
| parking_aisle |                     25.93 |                        843 |                     23.05 |                        754 |
| path          |                     50.36 |                        589 |                     46.84 |                        543 |
| pedestrian    |                      0.49 |                         11 |                      0.49 |                         11 |
| primary       |                     13.56 |                        135 |                     13    |                        122 |
| residential   |                    331.65 |                       4785 |                    328.02 |                       4599 |
| secondary     |                     23.23 |                        289 |                     22.92 |                        274 |
| sidewalk      |                     65.38 |                        882 |                     43.96 |                        523 |
| steps         |                      1.82 |                        140 |                      1.73 |                        126 |
| tertiary      |                     68.98 |                        953 |                     68.25 |                        880 |
| track         |                     22.16 |                        180 |                     21.2  |                        161 |
| trunk         |                     40.77 |                        359 |                     39.01 |                        315 |
| unclassified  |                    180.77 |                       2296 |                    176.36 |                       2105 |
| unknown       |                     60.76 |                       1190 |                     63.16 |                       1217 |

#### *Kumamoto*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     21.18 |                        403 |                     21.14 |                        395 |
| bridleway     |                      0    |                          0 |                      0    |                          0 |
| crosswalk     |                      0    |                          0 |                      2.41 |                        214 |
| cycleway      |                      4.27 |                         32 |                      4.27 |                         32 |
| driveway      |                      2.55 |                         53 |                      2.54 |                         53 |
| footway       |                     32.43 |                        968 |                     55.24 |                        897 |
| living_street |                      0    |                          0 |                      0    |                          0 |
| motorway      |                      0.1  |                          2 |                      0    |                          0 |
| parking_aisle |                      7.34 |                        199 |                      7.22 |                        200 |
| path          |                     44.41 |                        347 |                     43.83 |                        306 |
| pedestrian    |                      2.25 |                         70 |                      2.23 |                         58 |
| primary       |                     29.79 |                        347 |                     28.75 |                        331 |
| residential   |                    280.2  |                       4204 |                    277.02 |                       4108 |
| secondary     |                     43.13 |                        517 |                     42.98 |                        482 |
| sidewalk      |                     51.42 |                        688 |                     25.53 |                        307 |
| steps         |                      0.95 |                         93 |                      0.95 |                         93 |
| tertiary      |                    110.98 |                       1528 |                    110.63 |                       1511 |
| track         |                     60.22 |                        314 |                     59.83 |                        310 |
| trunk         |                     51.04 |                        485 |                     50.89 |                        436 |
| unclassified  |                    497.81 |                       7778 |                    492.83 |                       7529 |
| unknown       |                     57.55 |                        982 |                     57.05 |                        951 |

#### *Morioka*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     20.08 |                        453 |                     19.84 |                        445 |
| bridleway     |                      0    |                          0 |                      0    |                          0 |
| crosswalk     |                      0    |                          0 |                      5.56 |                        740 |
| cycleway      |                      8.16 |                         26 |                      7.38 |                         17 |
| driveway      |                      0.35 |                         10 |                      0.35 |                          8 |
| footway       |                     40.68 |                       1597 |                     59.28 |                       1076 |
| living_street |                      0    |                          0 |                      0    |                          0 |
| motorway      |                     22.66 |                        126 |                     15.56 |                         45 |
| parking_aisle |                      6.44 |                        171 |                      6.29 |                        162 |
| path          |                     33.78 |                        453 |                     33.17 |                        434 |
| pedestrian    |                      9.43 |                        157 |                      9.38 |                        142 |
| primary       |                     25.45 |                        275 |                     25.16 |                        255 |
| residential   |                    335.67 |                       4598 |                    333.05 |                       4501 |
| secondary     |                     14.2  |                        209 |                     14.14 |                        197 |
| sidewalk      |                     90.54 |                       1511 |                     63.83 |                        981 |
| steps         |                      2.98 |                        155 |                      2.98 |                        152 |
| tertiary      |                    136.64 |                       1847 |                    135.3  |                       1755 |
| track         |                     25.59 |                        169 |                     24.56 |                        157 |
| trunk         |                     38.77 |                        385 |                     35.8  |                        302 |
| unclassified  |                    296.48 |                       4599 |                    294.31 |                       4463 |
| unknown       |                     41.55 |                        903 |                     42.24 |                        905 |

#### *Tateyama*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     33.64 |                        527 |                     33.34 |                        501 |
| bridleway     |                      0    |                          0 |                      0    |                          0 |
| crosswalk     |                      0    |                          0 |                      2.66 |                        528 |
| cycleway      |                      0    |                          0 |                      0    |                          0 |
| driveway      |                      3.7  |                         75 |                      3.59 |                         70 |
| footway       |                      5.95 |                        668 |                      7.54 |                        146 |
| living_street |                      0    |                          0 |                      0    |                          0 |
| motorway      |                      0    |                          0 |                      0    |                          0 |
| parking_aisle |                      6.86 |                        145 |                      6.19 |                        136 |
| path          |                     64.58 |                        344 |                     53.54 |                        287 |
| pedestrian    |                      0.05 |                          2 |                      0.05 |                          2 |
| primary       |                      6.09 |                         67 |                      5.95 |                         57 |
| residential   |                    264.43 |                       3883 |                    261.7  |                       3672 |
| secondary     |                     24.72 |                        473 |                     24.59 |                        441 |
| sidewalk      |                      7.05 |                        122 |                      2.57 |                         41 |
| steps         |                      0.46 |                         23 |                      0.46 |                         22 |
| tertiary      |                     36.7  |                        504 |                     35.07 |                        485 |
| track         |                    104.91 |                        775 |                    102.47 |                        680 |
| trunk         |                     23.3  |                        288 |                     22.82 |                        259 |
| unclassified  |                     28.56 |                        294 |                     25.98 |                        273 |
| unknown       |                     15.23 |                        296 |                     16.02 |                        286 |

#### *Tokyo*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                    144.97 |                       4028 |                    143.42 |                       3976 |
| bridleway     |                      0.02 |                          1 |                      0.02 |                          1 |
| crosswalk     |                      0    |                          0 |                     43.44 |                       6014 |
| cycleway      |                     11.24 |                        191 |                     10.56 |                        181 |
| driveway      |                     12.71 |                        470 |                     12.29 |                        453 |
| footway       |                    417.56 |                      27031 |                    690.92 |                      25827 |
| living_street |                      0.16 |                          7 |                      0.16 |                          7 |
| motorway      |                     87.18 |                        386 |                     72.24 |                        196 |
| parking_aisle |                     16.44 |                        619 |                     15.05 |                        564 |
| path          |                     34.13 |                       1040 |                     34.29 |                       1028 |
| pedestrian    |                     27.87 |                        827 |                     27.75 |                        785 |
| primary       |                    105.79 |                       2709 |                    104.25 |                       2547 |
| residential   |                    693.14 |                      20895 |                    692.35 |                      20807 |
| secondary     |                    132.65 |                       3584 |                    131.69 |                       3405 |
| sidewalk      |                    684.79 |                      20903 |                    348.61 |                       8820 |
| steps         |                     20.71 |                       2056 |                     19.43 |                       1855 |
| tertiary      |                    235.02 |                       7650 |                    233.91 |                       7479 |
| track         |                      0    |                          0 |                      0    |                          0 |
| trunk         |                     59.45 |                       1511 |                     58.9  |                       1440 |
| unclassified  |                    393.12 |                      12564 |                    392.14 |                      12452 |
| unknown       |                    126.76 |                       3712 |                    129.11 |                       3589 |
