# Quality criterias result between OSM and OMF datasets

The test were run on 21/08/2024 23:51, using the 2024-06-13-beta.1 release of OvertureMap data and the OSM data until 2024/06/07.

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
| **2. Number of edges**                       | *Hamamatsu*        |        44483    |        40029    |                4454    |
| **2. Number of edges**                       | *Higashihiroshima* |        14057    |        13312    |                 745    |
| **2. Number of edges**                       | *Kumamoto*         |        19010    |        18564    |                 446    |
| **2. Number of edges**                       | *Morioka*          |        17644    |        17044    |                 600    |
| **2. Number of edges**                       | *Paris*            |       170611    |       143365    |               27246    |
| **2. Number of edges**                       | *Tateyama*         |         8486    |         8018    |                 468    |
| **2. Number of edges**                       | *Tokyo*            |       110184    |       102316    |                7868    |
| **3. Total length (km)**                     | *Hamamatsu*        |         1770    |         1783    |                  13    |
| **3. Total length (km)**                     | *Higashihiroshima* |          942    |          947    |                   5    |
| **3. Total length (km)**                     | *Kumamoto*         |         1298    |         1312    |                  14    |
| **3. Total length (km)**                     | *Morioka*          |         1150    |         1161    |                  11    |
| **3. Total length (km)**                     | *Paris*            |         3694    |         3660    |                  34    |
| **3. Total length (km)**                     | *Tateyama*         |          627    |          629    |                   2    |
| **3. Total length (km)**                     | *Tokyo*            |         3204    |         3214    |                  10    |
| **4. Number of connected components**        | *Hamamatsu*        |           53    |           67    |                  14    |
| **4. Number of connected components**        | *Higashihiroshima* |           28    |           36    |                   8    |
| **4. Number of connected components**        | *Kumamoto*         |          108    |          122    |                  14    |
| **4. Number of connected components**        | *Morioka*          |           31    |           43    |                  12    |
| **4. Number of connected components**        | *Paris*            |         1311    |         1209    |                 102    |
| **4. Number of connected components**        | *Tateyama*         |           25    |           28    |                   3    |
| **4. Number of connected components**        | *Tokyo*            |          253    |          287    |                  34    |
| **5. Number of strong connected components** | *Hamamatsu*        |          101    |          118    |                  17    |
| **5. Number of strong connected components** | *Higashihiroshima* |           67    |           54    |                  13    |
| **5. Number of strong connected components** | *Kumamoto*         |          130    |          169    |                  39    |
| **5. Number of strong connected components** | *Morioka*          |          100    |           81    |                  19    |
| **5. Number of strong connected components** | *Paris*            |         1861    |         1838    |                  23    |
| **5. Number of strong connected components** | *Tateyama*         |           32    |           31    |                   1    |
| **5. Number of strong connected components** | *Tokyo*            |          593    |          696    |                 103    |
| **6. Number of isolated nodes**              | *Hamamatsu*        |           12    |            0    |                  12    |
| **6. Number of isolated nodes**              | *Higashihiroshima* |            8    |            0    |                   8    |
| **6. Number of isolated nodes**              | *Kumamoto*         |           10    |            0    |                  10    |
| **6. Number of isolated nodes**              | *Morioka*          |            8    |            0    |                   8    |
| **6. Number of isolated nodes**              | *Paris*            |           18    |            0    |                  18    |
| **6. Number of isolated nodes**              | *Tateyama*         |            3    |            0    |                   3    |
| **6. Number of isolated nodes**              | *Tokyo*            |           16    |            0    |                  16    |
| **7. Overlap indicator (%)**                 | *Hamamatsu*        |          100    |           98.46 |                   1.54 |
| **7. Overlap indicator (%)**                 | *Higashihiroshima* |           99.98 |           96.39 |                   3.59 |
| **7. Overlap indicator (%)**                 | *Kumamoto*         |           99.97 |           98.03 |                   1.94 |
| **7. Overlap indicator (%)**                 | *Morioka*          |           99.95 |           97.17 |                   2.78 |
| **7. Overlap indicator (%)**                 | *Paris*            |           97.94 |           98.31 |                   0.37 |
| **7. Overlap indicator (%)**                 | *Tateyama*         |          100    |           96.31 |                   3.69 |
| **7. Overlap indicator (%)**                 | *Tokyo*            |           99.5  |           98.32 |                   1.18 |
| **8. Number of corresponding nodes**         | *Hamamatsu*        |        27687    |        27687    |                   0    |
| **8. Number of corresponding nodes**         | *Higashihiroshima* |         9390    |         9390    |                   0    |
| **8. Number of corresponding nodes**         | *Kumamoto*         |        12557    |        12557    |                   0    |
| **8. Number of corresponding nodes**         | *Morioka*          |        11618    |        11618    |                   0    |
| **8. Number of corresponding nodes**         | *Paris*            |        95592    |        95592    |                   0    |
| **8. Number of corresponding nodes**         | *Tateyama*         |         6158    |         6158    |                   0    |
| **8. Number of corresponding nodes**         | *Tokyo*            |        65609    |        65609    |                   0    |
| **9. Percentage of corresponding nodes (%)** | *Hamamatsu*        |           84.5  |           97.8  |                  13.3  |
| **9. Percentage of corresponding nodes (%)** | *Higashihiroshima* |           90.17 |           96.99 |                   6.82 |
| **9. Percentage of corresponding nodes (%)** | *Kumamoto*         |           92.24 |           95.29 |                   3.05 |
| **9. Percentage of corresponding nodes (%)** | *Morioka*          |           92.21 |           96.65 |                   4.44 |
| **9. Percentage of corresponding nodes (%)** | *Paris*            |           76.89 |           97.25 |                  20.36 |
| **9. Percentage of corresponding nodes (%)** | *Tateyama*         |           90.45 |           97.1  |                   6.65 |
| **9. Percentage of corresponding nodes (%)** | *Tokyo*            |           87.59 |           97.52 |                   9.93 |

## Specific results

### Total kilometer of roads by class

#### *Hamamatsu*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     14.44 |                        340 |                     14.05 |                        326 |
| crosswalk     |                      0    |                          0 |                      8.41 |                       1256 |
| driveway      |                     19.48 |                        606 |                     19.55 |                        588 |
| footway       |                    283.01 |                      10352 |                    239.67 |                       5381 |
| motorway      |                      8.81 |                         39 |                      8.84 |                         20 |
| parking_aisle |                    109.03 |                       5474 |                    108.05 |                       4792 |
| path          |                     37.02 |                        991 |                     37.21 |                        861 |
| pedestrian    |                      2.43 |                         41 |                      2.54 |                         37 |
| primary       |                     39.02 |                        876 |                     39.19 |                        849 |
| residential   |                    586.16 |                      12876 |                    589.46 |                      12756 |
| secondary     |                     23.59 |                        663 |                     23.69 |                        647 |
| sidewalk      |                      0    |                          0 |                     37.01 |                        755 |
| steps         |                      4.19 |                        396 |                      4.21 |                        390 |
| tertiary      |                    179.86 |                       4207 |                    180.88 |                       4087 |
| track         |                     66.45 |                        734 |                     67.05 |                        673 |
| trunk         |                     26.57 |                        533 |                     27.01 |                        532 |
| unclassified  |                    310.04 |                       4866 |                    313.19 |                       4619 |
| unknown       |                     59.77 |                       1489 |                     62.69 |                       1460 |

#### *Higashihiroshima*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0.49 |                          8 |                      0.49 |                          8 |
| crosswalk     |                      0    |                          0 |                      1.93 |                        245 |
| cycleway      |                      2.93 |                         30 |                      2.93 |                         28 |
| driveway      |                      4.96 |                        174 |                      4.96 |                        176 |
| footway       |                     95.8  |                       2036 |                     49.7  |                       1046 |
| motorway      |                     16.51 |                         39 |                     17.13 |                         16 |
| parking_aisle |                     25.93 |                        843 |                     23.05 |                        754 |
| path          |                     50.36 |                        589 |                     50.67 |                        561 |
| pedestrian    |                      0.49 |                         11 |                      0.49 |                         11 |
| primary       |                     13.56 |                        135 |                     13.65 |                        127 |
| residential   |                    331.65 |                       4785 |                    332.97 |                       4649 |
| secondary     |                     23.23 |                        289 |                     23.37 |                        278 |
| sidewalk      |                      0    |                          0 |                     44.22 |                        526 |
| steps         |                      1.82 |                        140 |                      1.73 |                        126 |
| tertiary      |                     68.98 |                        953 |                     69.66 |                        898 |
| track         |                     22.16 |                        180 |                     22.35 |                        173 |
| trunk         |                     40.77 |                        359 |                     41.06 |                        323 |
| unclassified  |                    180.77 |                       2296 |                    182.11 |                       2143 |
| unknown       |                     60.76 |                       1190 |                     63.76 |                       1224 |

#### *Kumamoto*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     21.18 |                        403 |                     21.45 |                        406 |
| crosswalk     |                      0    |                          0 |                      2.42 |                        215 |
| cycleway      |                      4.27 |                         32 |                      4.27 |                         32 |
| driveway      |                      2.55 |                         53 |                      2.58 |                         54 |
| footway       |                     83.86 |                       1656 |                     55.93 |                        903 |
| motorway      |                      0.1  |                          2 |                      0.41 |                          5 |
| parking_aisle |                      7.34 |                        199 |                      7.22 |                        200 |
| path          |                     44.41 |                        347 |                     44.6  |                        315 |
| pedestrian    |                      2.25 |                         70 |                      2.26 |                         59 |
| primary       |                     29.79 |                        347 |                     30.41 |                        344 |
| residential   |                    280.2  |                       4204 |                    282.92 |                       4195 |
| secondary     |                     43.13 |                        517 |                     43.29 |                        489 |
| sidewalk      |                      0    |                          0 |                     25.83 |                        311 |
| steps         |                      0.95 |                         93 |                      1.01 |                         94 |
| tertiary      |                    110.98 |                       1528 |                    112.59 |                       1538 |
| track         |                     60.22 |                        314 |                     61.64 |                        328 |
| trunk         |                     51.04 |                        485 |                     51.55 |                        449 |
| unclassified  |                    497.81 |                       7778 |                    503.19 |                       7669 |
| unknown       |                     57.55 |                        982 |                     57.55 |                        958 |

#### *Morioka*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     20.08 |                        453 |                     20.12 |                        451 |
| crosswalk     |                      0    |                          0 |                      5.56 |                        740 |
| cycleway      |                      8.16 |                         26 |                      8.21 |                         19 |
| driveway      |                      0.35 |                         10 |                      0.35 |                          8 |
| footway       |                    131.21 |                       3108 |                     60.71 |                       1088 |
| motorway      |                     22.66 |                        126 |                     22.88 |                         49 |
| parking_aisle |                      6.44 |                        171 |                      6.29 |                        162 |
| path          |                     33.78 |                        453 |                     34.09 |                        446 |
| pedestrian    |                      9.43 |                        157 |                      9.63 |                        147 |
| primary       |                     25.45 |                        275 |                     25.67 |                        261 |
| residential   |                    335.67 |                       4598 |                    338.76 |                       4605 |
| secondary     |                     14.2  |                        209 |                     14.2  |                        198 |
| sidewalk      |                      0    |                          0 |                     65.88 |                        997 |
| steps         |                      2.98 |                        155 |                      3.02 |                        153 |
| tertiary      |                    136.64 |                       1847 |                    137.74 |                       1791 |
| track         |                     25.59 |                        169 |                     25.98 |                        168 |
| trunk         |                     38.77 |                        385 |                     39.57 |                        320 |
| unclassified  |                    296.48 |                       4599 |                    298.38 |                       4522 |
| unknown       |                     41.55 |                        903 |                     43.25 |                        919 |

#### *Paris*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     23.75 |                        808 |                     23.46 |                        657 |
| crosswalk     |                      0    |                          0 |                     22.75 |                       4840 |
| cycleway      |                    171.17 |                       5273 |                    173.21 |                       4950 |
| driveway      |                     17.2  |                        698 |                     16.57 |                        568 |
| footway       |                   2131.45 |                     116649 |                   1023.23 |                      56609 |
| living_street |                     44.79 |                       1542 |                     45.17 |                       1493 |
| motorway      |                      0.03 |                          2 |                      0.04 |                          3 |
| parking_aisle |                     30.28 |                       1111 |                     27.91 |                        960 |
| path          |                      9.78 |                        317 |                      9.93 |                        310 |
| pedestrian    |                    100.94 |                       3427 |                    100.83 |                       3170 |
| primary       |                    138.09 |                       4010 |                    137.1  |                       3721 |
| residential   |                    545.48 |                      17315 |                    549.73 |                      17064 |
| secondary     |                    107.56 |                       3554 |                    113.62 |                       3552 |
| sidewalk      |                      0    |                          0 |                   1049.25 |                      31975 |
| steps         |                     39.24 |                       4905 |                     24.4  |                       3414 |
| tertiary      |                    101.97 |                       3506 |                    103.61 |                       3395 |
| track         |                      0.72 |                          7 |                      0.72 |                          5 |
| trunk         |                      9.34 |                         69 |                     10.34 |                         47 |
| unclassified  |                     28.42 |                       1023 |                     27.79 |                        972 |
| unknown       |                    193.76 |                       6395 |                    199.99 |                       5660 |

#### *Tateyama*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     33.64 |                        527 |                     33.53 |                        510 |
| crosswalk     |                      0    |                          0 |                      2.66 |                        528 |
| driveway      |                      3.7  |                         75 |                      3.59 |                         70 |
| footway       |                     13    |                        790 |                      7.78 |                        148 |
| parking_aisle |                      6.86 |                        145 |                      6.23 |                        137 |
| path          |                     64.58 |                        344 |                     64.85 |                        312 |
| pedestrian    |                      0.05 |                          2 |                      0.05 |                          2 |
| primary       |                      6.09 |                         67 |                      6.14 |                         59 |
| residential   |                    264.43 |                       3883 |                    265.1  |                       3718 |
| secondary     |                     24.72 |                        473 |                     24.78 |                        447 |
| sidewalk      |                      0    |                          0 |                      2.57 |                         41 |
| steps         |                      0.46 |                         23 |                      0.46 |                         23 |
| tertiary      |                     36.7  |                        504 |                     36.78 |                        489 |
| track         |                    104.91 |                        775 |                    105.47 |                        701 |
| trunk         |                     23.3  |                        288 |                     23.4  |                        263 |
| unclassified  |                     28.56 |                        294 |                     28.97 |                        280 |
| unknown       |                     15.23 |                        296 |                     16.58 |                        290 |

#### *Tokyo*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                    144.97 |                       4028 |                    145.06 |                       4031 |
| bridleway     |                      0.02 |                          1 |                      0.02 |                          1 |
| crosswalk     |                      0    |                          0 |                     43.52 |                       6024 |
| cycleway      |                     11.24 |                        191 |                     11.44 |                        189 |
| driveway      |                     12.71 |                        470 |                     12.86 |                        470 |
| footway       |                   1101.96 |                      47925 |                    699.29 |                      26010 |
| living_street |                      0.16 |                          7 |                      0.16 |                          7 |
| motorway      |                     87.18 |                        386 |                     88.77 |                        233 |
| parking_aisle |                     16.44 |                        619 |                     15.07 |                        566 |
| path          |                     34.52 |                       1049 |                     34.68 |                       1047 |
| pedestrian    |                     27.87 |                        827 |                     27.97 |                        793 |
| primary       |                    105.79 |                       2709 |                    106.8  |                       2583 |
| residential   |                    693.14 |                      20895 |                    696.28 |                      20945 |
| secondary     |                    132.65 |                       3584 |                    135.32 |                       3463 |
| sidewalk      |                      0    |                          0 |                    354.45 |                       8901 |
| steps         |                     20.71 |                       2056 |                     19.49 |                       1860 |
| tertiary      |                    235.02 |                       7650 |                    236.1  |                       7528 |
| trunk         |                     59.45 |                       1511 |                     59.87 |                       1464 |
| unclassified  |                    393.12 |                      12564 |                    395.85 |                      12576 |
| unknown       |                    126.76 |                       3712 |                    130.1  |                       3625 |
