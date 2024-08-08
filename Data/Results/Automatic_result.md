# Quality criterias result between OSM and OMF datasets

The test were run on 08/08/2024 10:53, using the 2024-06-13-beta.1 release of OvertureMap data and the OSM data until 2024/06/07.

## General results

| **Criterion**                                | **Area**           |   **OSM Value** |   **OMF Value** |   **Difference (abs)** |
|----------------------------------------------|--------------------|-----------------|-----------------|------------------------|
| **1. Number of nodes**                       | *Hamamatsu*        |        32765    |        27890    |                4875    |
| **1. Number of nodes**                       | *Higashihiroshima* |        10414    |         9502    |                 912    |
| **1. Number of nodes**                       | *Kumamoto*         |        13614    |        12824    |                 790    |
| **1. Number of nodes**                       | *Morioka*          |        12599    |        11710    |                 889    |
| **1. Number of nodes**                       | *Paris*            |       124318    |        97329    |               26989    |
| **1. Number of nodes**                       | *Tateyama*         |         6808    |         6207    |                 601    |
| **1. Number of nodes**                       | *Tokyo*            |        74902    |        66382    |                8520    |
| **2. Number of edges**                       | *Hamamatsu*        |        44483    |        39614    |                4869    |
| **2. Number of edges**                       | *Higashihiroshima* |        14057    |        13138    |                 919    |
| **2. Number of edges**                       | *Kumamoto*         |        19010    |        18213    |                 797    |
| **2. Number of edges**                       | *Morioka*          |        17644    |        16737    |                 907    |
| **2. Number of edges**                       | *Paris*            |       170611    |       142409    |               28202    |
| **2. Number of edges**                       | *Tateyama*         |         8486    |         7886    |                 600    |
| **2. Number of edges**                       | *Tokyo*            |       110184    |       101426    |                8758    |
| **3. Total length (km)**                     | *Hamamatsu*        |         1770    |         1756    |                  14    |
| **3. Total length (km)**                     | *Higashihiroshima* |          942    |          912    |                  30    |
| **3. Total length (km)**                     | *Kumamoto*         |         1298    |         1286    |                  12    |
| **3. Total length (km)**                     | *Morioka*          |         1150    |         1129    |                  21    |
| **3. Total length (km)**                     | *Paris*            |         3694    |         3614    |                  80    |
| **3. Total length (km)**                     | *Tateyama*         |          627    |          605    |                  22    |
| **3. Total length (km)**                     | *Tokyo*            |         3204    |         3161    |                  43    |
| **4. Number of connected components**        | *Hamamatsu*        |           53    |           52    |                   1    |
| **4. Number of connected components**        | *Higashihiroshima* |           28    |           24    |                   4    |
| **4. Number of connected components**        | *Kumamoto*         |          108    |          117    |                   9    |
| **4. Number of connected components**        | *Morioka*          |           31    |           34    |                   3    |
| **4. Number of connected components**        | *Paris*            |         1311    |         1185    |                 126    |
| **4. Number of connected components**        | *Tateyama*         |           25    |           18    |                   7    |
| **4. Number of connected components**        | *Tokyo*            |          253    |          257    |                   4    |
| **5. Number of strong connected components** | *Hamamatsu*        |          101    |           99    |                   2    |
| **5. Number of strong connected components** | *Higashihiroshima* |           67    |           39    |                  28    |
| **5. Number of strong connected components** | *Kumamoto*         |          130    |          160    |                  30    |
| **5. Number of strong connected components** | *Morioka*          |          100    |           61    |                  39    |
| **5. Number of strong connected components** | *Paris*            |         1861    |         1911    |                  50    |
| **5. Number of strong connected components** | *Tateyama*         |           32    |           20    |                  12    |
| **5. Number of strong connected components** | *Tokyo*            |          593    |          637    |                  44    |
| **6. Number of isolated nodes**              | *Hamamatsu*        |           12    |            0    |                  12    |
| **6. Number of isolated nodes**              | *Higashihiroshima* |            8    |            0    |                   8    |
| **6. Number of isolated nodes**              | *Kumamoto*         |           10    |            0    |                  10    |
| **6. Number of isolated nodes**              | *Morioka*          |            8    |            0    |                   8    |
| **6. Number of isolated nodes**              | *Paris*            |           18    |            0    |                  18    |
| **6. Number of isolated nodes**              | *Tateyama*         |            3    |            0    |                   3    |
| **6. Number of isolated nodes**              | *Tokyo*            |           16    |            0    |                  16    |
| **7. Overlap indicator (%)**                 | *Hamamatsu*        |          100    |           95.84 |                   4.16 |
| **7. Overlap indicator (%)**                 | *Higashihiroshima* |           99.98 |           91.01 |                   8.97 |
| **7. Overlap indicator (%)**                 | *Kumamoto*         |           99.97 |           94.66 |                   5.31 |
| **7. Overlap indicator (%)**                 | *Morioka*          |           99.95 |           93.11 |                   6.84 |
| **7. Overlap indicator (%)**                 | *Paris*            |           97.94 |           95.95 |                   1.99 |
| **7. Overlap indicator (%)**                 | *Tateyama*         |          100    |           91.58 |                   8.42 |
| **7. Overlap indicator (%)**                 | *Tokyo*            |           99.5  |           94.87 |                   4.63 |
| **8. Number of corresponding nodes**         | *Hamamatsu*        |        27687    |        27687    |                   0    |
| **8. Number of corresponding nodes**         | *Higashihiroshima* |         9390    |         9390    |                   0    |
| **8. Number of corresponding nodes**         | *Kumamoto*         |        12557    |        12557    |                   0    |
| **8. Number of corresponding nodes**         | *Morioka*          |        11618    |        11618    |                   0    |
| **8. Number of corresponding nodes**         | *Paris*            |        95591    |        95591    |                   0    |
| **8. Number of corresponding nodes**         | *Tateyama*         |         6157    |         6157    |                   0    |
| **8. Number of corresponding nodes**         | *Tokyo*            |        65609    |        65609    |                   0    |
| **9. Percentage of corresponding nodes (%)** | *Hamamatsu*        |           84.5  |           99.27 |                  14.77 |
| **9. Percentage of corresponding nodes (%)** | *Higashihiroshima* |           90.17 |           98.82 |                   8.65 |
| **9. Percentage of corresponding nodes (%)** | *Kumamoto*         |           92.24 |           97.92 |                   5.68 |
| **9. Percentage of corresponding nodes (%)** | *Morioka*          |           92.21 |           99.21 |                   7    |
| **9. Percentage of corresponding nodes (%)** | *Paris*            |           76.89 |           98.21 |                  21.32 |
| **9. Percentage of corresponding nodes (%)** | *Tateyama*         |           90.44 |           99.19 |                   8.75 |
| **9. Percentage of corresponding nodes (%)** | *Tokyo*            |           87.59 |           98.84 |                  11.25 |

## Specific results

### Total kilometer of roads by class

#### *Hamamatsu*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     14.44 |                        340 |                     13.92 |                        320 |
| crosswalk     |                      0    |                          0 |                      8.41 |                       1254 |
| driveway      |                     19.48 |                        606 |                     19.36 |                        579 |
| footway       |                    283.01 |                      10352 |                    236.27 |                       5340 |
| motorway      |                      8.81 |                         39 |                      7.61 |                         18 |
| parking_aisle |                    109.03 |                       5474 |                    107.63 |                       4769 |
| path          |                     37.02 |                        991 |                     36.12 |                        838 |
| pedestrian    |                      2.43 |                         41 |                      2.42 |                         36 |
| primary       |                     39.02 |                        876 |                     38.71 |                        840 |
| residential   |                    586.16 |                      12876 |                    584.39 |                      12638 |
| secondary     |                     23.59 |                        663 |                     23.55 |                        642 |
| sidewalk      |                      0    |                          0 |                     36.23 |                        745 |
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
| crosswalk     |                      0    |                          0 |                      1.93 |                        245 |
| cycleway      |                      2.93 |                         30 |                      2.93 |                         28 |
| driveway      |                      4.96 |                        174 |                      4.96 |                        175 |
| footway       |                     95.8  |                       2036 |                     48.95 |                       1042 |
| motorway      |                     16.51 |                         39 |                      3.77 |                         10 |
| parking_aisle |                     25.93 |                        843 |                     23.05 |                        754 |
| path          |                     50.36 |                        589 |                     46.84 |                        543 |
| pedestrian    |                      0.49 |                         11 |                      0.49 |                         11 |
| primary       |                     13.56 |                        135 |                     13    |                        122 |
| residential   |                    331.65 |                       4785 |                    328.02 |                       4599 |
| secondary     |                     23.23 |                        289 |                     22.92 |                        274 |
| sidewalk      |                      0    |                          0 |                     43.96 |                        523 |
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
| crosswalk     |                      0    |                          0 |                      2.41 |                        214 |
| cycleway      |                      4.27 |                         32 |                      4.27 |                         32 |
| driveway      |                      2.55 |                         53 |                      2.54 |                         53 |
| footway       |                     83.86 |                       1656 |                     55.24 |                        897 |
| motorway      |                      0.1  |                          2 |                      0    |                          0 |
| parking_aisle |                      7.34 |                        199 |                      7.22 |                        200 |
| path          |                     44.41 |                        347 |                     43.83 |                        306 |
| pedestrian    |                      2.25 |                         70 |                      2.23 |                         58 |
| primary       |                     29.79 |                        347 |                     28.75 |                        331 |
| residential   |                    280.2  |                       4204 |                    277.02 |                       4108 |
| secondary     |                     43.13 |                        517 |                     42.98 |                        482 |
| sidewalk      |                      0    |                          0 |                     25.53 |                        307 |
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
| crosswalk     |                      0    |                          0 |                      5.56 |                        740 |
| cycleway      |                      8.16 |                         26 |                      7.38 |                         17 |
| driveway      |                      0.35 |                         10 |                      0.35 |                          8 |
| footway       |                    131.21 |                       3108 |                     59.28 |                       1076 |
| motorway      |                     22.66 |                        126 |                     15.56 |                         45 |
| parking_aisle |                      6.44 |                        171 |                      6.29 |                        162 |
| path          |                     33.78 |                        453 |                     33.17 |                        434 |
| pedestrian    |                      9.43 |                        157 |                      9.38 |                        142 |
| primary       |                     25.45 |                        275 |                     25.16 |                        255 |
| residential   |                    335.67 |                       4598 |                    333.05 |                       4501 |
| secondary     |                     14.2  |                        209 |                     14.14 |                        197 |
| sidewalk      |                      0    |                          0 |                     63.83 |                        981 |
| steps         |                      2.98 |                        155 |                      2.98 |                        152 |
| tertiary      |                    136.64 |                       1847 |                    135.3  |                       1755 |
| track         |                     25.59 |                        169 |                     24.56 |                        157 |
| trunk         |                     38.77 |                        385 |                     35.8  |                        302 |
| unclassified  |                    296.48 |                       4599 |                    294.31 |                       4463 |
| unknown       |                     41.55 |                        903 |                     42.24 |                        905 |

#### *Paris*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     23.75 |                        808 |                     23.31 |                        655 |
| crosswalk     |                      0    |                          0 |                     22.5  |                       4831 |
| cycleway      |                    171.17 |                       5273 |                    170.32 |                       4906 |
| driveway      |                     17.2  |                        698 |                     16.46 |                        564 |
| footway       |                   2131.45 |                     116649 |                   1014.17 |                      56361 |
| living_street |                     44.79 |                       1542 |                     44.54 |                       1477 |
| motorway      |                      0.03 |                          2 |                      0    |                          0 |
| parking_aisle |                     30.28 |                       1111 |                     27.77 |                        955 |
| path          |                      9.78 |                        317 |                      9.57 |                        307 |
| pedestrian    |                    100.94 |                       3427 |                    100.29 |                       3158 |
| primary       |                    138.09 |                       4010 |                    133.54 |                       3674 |
| residential   |                    545.48 |                      17315 |                    543.61 |                      16903 |
| secondary     |                    107.56 |                       3554 |                    111.46 |                       3518 |
| sidewalk      |                      0    |                          0 |                   1038.15 |                      31755 |
| steps         |                     39.24 |                       4905 |                     24.39 |                       3413 |
| tertiary      |                    101.97 |                       3506 |                    102.19 |                       3364 |
| track         |                      0.72 |                          7 |                      0.72 |                          5 |
| trunk         |                      9.34 |                         69 |                      6.87 |                         33 |
| unclassified  |                     28.42 |                       1023 |                     27.69 |                        967 |
| unknown       |                    193.76 |                       6395 |                    195.63 |                       5563 |

#### *Tateyama*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     33.64 |                        527 |                     33.34 |                        501 |
| crosswalk     |                      0    |                          0 |                      2.66 |                        528 |
| driveway      |                      3.7  |                         75 |                      3.59 |                         70 |
| footway       |                     13    |                        790 |                      7.54 |                        146 |
| parking_aisle |                      6.86 |                        145 |                      6.19 |                        136 |
| path          |                     64.58 |                        344 |                     53.54 |                        287 |
| pedestrian    |                      0.05 |                          2 |                      0.05 |                          2 |
| primary       |                      6.09 |                         67 |                      5.95 |                         57 |
| residential   |                    264.43 |                       3883 |                    261.7  |                       3672 |
| secondary     |                     24.72 |                        473 |                     24.59 |                        441 |
| sidewalk      |                      0    |                          0 |                      2.57 |                         41 |
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
| footway       |                   1101.96 |                      47925 |                    690.92 |                      25827 |
| living_street |                      0.16 |                          7 |                      0.16 |                          7 |
| motorway      |                     87.18 |                        386 |                     72.24 |                        196 |
| parking_aisle |                     16.44 |                        619 |                     15.05 |                        564 |
| path          |                     34.52 |                       1049 |                     34.29 |                       1028 |
| pedestrian    |                     27.87 |                        827 |                     27.75 |                        785 |
| primary       |                    105.79 |                       2709 |                    104.25 |                       2547 |
| residential   |                    693.14 |                      20895 |                    692.35 |                      20807 |
| secondary     |                    132.65 |                       3584 |                    131.69 |                       3405 |
| sidewalk      |                      0    |                          0 |                    348.61 |                       8820 |
| steps         |                     20.71 |                       2056 |                     19.43 |                       1855 |
| tertiary      |                    235.02 |                       7650 |                    233.91 |                       7479 |
| trunk         |                     59.45 |                       1511 |                     58.9  |                       1440 |
| unclassified  |                    393.12 |                      12564 |                    392.14 |                      12452 |
| unknown       |                    126.76 |                       3712 |                    129.11 |                       3589 |
