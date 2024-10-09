# Quality criterias result between OpenStreetMap and Overture Maps Foundation datasets

The test were run on 01/10/2024 16:27, using the 2024-09-18.0 release of Overture Maps Foundation data and the OpenStreetMap data until 2024-08-31.

## General results

| **Criterion**                                | **Area**           |   **OSM Value** |   **OMF Value** |   **Difference (abs)** |
|----------------------------------------------|--------------------|-----------------|-----------------|------------------------|
| **1. Number of nodes**                       | *Hamamatsu*        |     33018       |      28543      |            4475        |
| **1. Number of nodes**                       | *Higashihiroshima* |     10412       |       9683      |             729        |
| **1. Number of nodes**                       | *Kumamoto*         |     13634       |      13204      |             430        |
| **1. Number of nodes**                       | *Morioka*          |     13171       |      12577      |             594        |
| **1. Number of nodes**                       | *Paris*            |    125177       |      98679      |           26498        |
| **1. Number of nodes**                       | *Riyadh*           |     45166       |      52226      |            7060        |
| **1. Number of nodes**                       | *Tateyama*         |      6817       |       6351      |             466        |
| **1. Number of nodes**                       | *Tokyo*            |     75099       |      67452      |            7647        |
| **10. Places density**                       | *Hamamatsu*        |       124.014   |         29.4542 |              94.5601   |
| **10. Places density**                       | *Higashihiroshima* |        20.1522  |         21.0016 |               0.849328 |
| **10. Places density**                       | *Kumamoto*         |        28.3682  |         83.0436 |              54.6754   |
| **10. Places density**                       | *Morioka*          |        32.2209  |         60.255  |              28.0342   |
| **10. Places density**                       | *Paris*            |      1272.89    |       1401.41   |             128.514    |
| **10. Places density**                       | *Riyadh*           |         9.23981 |         53.558  |              44.3182   |
| **10. Places density**                       | *Tateyama*         |        13.0745  |         12.0292 |               1.04534  |
| **10. Places density**                       | *Tokyo*            |       468.081   |        697.358  |             229.277    |
| **2. Number of edges**                       | *Hamamatsu*        |     44813       |      40338      |            4475        |
| **2. Number of edges**                       | *Higashihiroshima* |     14054       |      13313      |             741        |
| **2. Number of edges**                       | *Kumamoto*         |     19045       |      18605      |             440        |
| **2. Number of edges**                       | *Morioka*          |     18431       |      17821      |             610        |
| **2. Number of edges**                       | *Paris*            |    171866       |     143993      |           27873        |
| **2. Number of edges**                       | *Riyadh*           |     67575       |      76802      |            9227        |
| **2. Number of edges**                       | *Tateyama*         |      8496       |       8028      |             468        |
| **2. Number of edges**                       | *Tokyo*            |    110462       |     102584      |            7878        |
| **3. Total length (km)**                     | *Hamamatsu*        |      1775       |       1787      |              12        |
| **3. Total length (km)**                     | *Higashihiroshima* |       942       |        947      |               5        |
| **3. Total length (km)**                     | *Kumamoto*         |      1300       |       1313      |              13        |
| **3. Total length (km)**                     | *Morioka*          |      1178       |       1190      |              12        |
| **3. Total length (km)**                     | *Paris*            |      3708       |       3668      |              40        |
| **3. Total length (km)**                     | *Riyadh*           |      5311       |       5666      |             355        |
| **3. Total length (km)**                     | *Tateyama*         |       627       |        630      |               3        |
| **3. Total length (km)**                     | *Tokyo*            |      3207       |       3217      |              10        |
| **4. Number of connected components**        | *Hamamatsu*        |        52       |         66      |              14        |
| **4. Number of connected components**        | *Higashihiroshima* |        28       |         36      |               8        |
| **4. Number of connected components**        | *Kumamoto*         |       108       |        122      |              14        |
| **4. Number of connected components**        | *Morioka*          |        31       |         42      |              11        |
| **4. Number of connected components**        | *Paris*            |      1345       |       1266      |              79        |
| **4. Number of connected components**        | *Riyadh*           |        48       |         59      |              11        |
| **4. Number of connected components**        | *Tateyama*         |        25       |         28      |               3        |
| **4. Number of connected components**        | *Tokyo*            |       254       |        289      |              35        |
| **5. Number of strong connected components** | *Hamamatsu*        |        99       |        117      |              18        |
| **5. Number of strong connected components** | *Higashihiroshima* |        67       |         54      |              13        |
| **5. Number of strong connected components** | *Kumamoto*         |       134       |        175      |              41        |
| **5. Number of strong connected components** | *Morioka*          |       100       |         80      |              20        |
| **5. Number of strong connected components** | *Paris*            |      1888       |       1898      |              10        |
| **5. Number of strong connected components** | *Riyadh*           |       411       |        571      |             160        |
| **5. Number of strong connected components** | *Tateyama*         |        32       |         31      |               1        |
| **5. Number of strong connected components** | *Tokyo*            |       599       |        700      |             101        |
| **6. Number of isolated nodes**              | *Hamamatsu*        |        12       |          0      |              12        |
| **6. Number of isolated nodes**              | *Higashihiroshima* |         8       |          0      |               8        |
| **6. Number of isolated nodes**              | *Kumamoto*         |        10       |          0      |              10        |
| **6. Number of isolated nodes**              | *Morioka*          |         8       |          0      |               8        |
| **6. Number of isolated nodes**              | *Paris*            |        19       |          0      |              19        |
| **6. Number of isolated nodes**              | *Riyadh*           |        11       |          0      |              11        |
| **6. Number of isolated nodes**              | *Tateyama*         |         3       |          0      |               3        |
| **6. Number of isolated nodes**              | *Tokyo*            |        16       |          0      |              16        |
| **7. Overlap indicator (%)**                 | *Hamamatsu*        |       100       |         98.62   |               1.38     |
| **7. Overlap indicator (%)**                 | *Higashihiroshima* |        99.98    |         96.39   |               3.59     |
| **7. Overlap indicator (%)**                 | *Kumamoto*         |        99.97    |         98.02   |               1.95     |
| **7. Overlap indicator (%)**                 | *Morioka*          |       100       |         97.19   |               2.81     |
| **7. Overlap indicator (%)**                 | *Paris*            |        98.09    |         98.62   |               0.53     |
| **7. Overlap indicator (%)**                 | *Riyadh*           |        99.81    |         93.05   |               6.76     |
| **7. Overlap indicator (%)**                 | *Tateyama*         |       100       |         96.31   |               3.69     |
| **7. Overlap indicator (%)**                 | *Tokyo*            |        99.57    |         98.37   |               1.2      |
| **8. Number of corresponding nodes**         | *Hamamatsu*        |     27915       |      27915      |               0        |
| **8. Number of corresponding nodes**         | *Higashihiroshima* |      9392       |       9392      |               0        |
| **8. Number of corresponding nodes**         | *Kumamoto*         |     12579       |      12579      |               0        |
| **8. Number of corresponding nodes**         | *Morioka*          |     12170       |      12170      |               0        |
| **8. Number of corresponding nodes**         | *Paris*            |     96287       |      96287      |               0        |
| **8. Number of corresponding nodes**         | *Riyadh*           |     43886       |      43886      |               0        |
| **8. Number of corresponding nodes**         | *Tateyama*         |      6166       |       6166      |               0        |
| **8. Number of corresponding nodes**         | *Tokyo*            |     65824       |      65824      |               0        |
| **9. Percentage of corresponding nodes (%)** | *Hamamatsu*        |        84.54    |         97.8    |              13.26     |
| **9. Percentage of corresponding nodes (%)** | *Higashihiroshima* |        90.2     |         96.99   |               6.79     |
| **9. Percentage of corresponding nodes (%)** | *Kumamoto*         |        92.26    |         95.27   |               3.01     |
| **9. Percentage of corresponding nodes (%)** | *Morioka*          |        92.4     |         96.76   |               4.36     |
| **9. Percentage of corresponding nodes (%)** | *Paris*            |        76.92    |         97.58   |              20.66     |
| **9. Percentage of corresponding nodes (%)** | *Riyadh*           |        97.17    |         84.03   |              13.14     |
| **9. Percentage of corresponding nodes (%)** | *Tateyama*         |        90.45    |         97.09   |               6.64     |
| **9. Percentage of corresponding nodes (%)** | *Tokyo*            |        87.65    |         97.59   |               9.94     |

## Specific results

### Total kilometer of roads by class

#### *Hamamatsu*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      0.09 |                          4 |
| alley         |                     14.41 |                        341 |                     14.12 |                        331 |
| crosswalk     |                      0    |                          0 |                      9.69 |                       1479 |
| driveway      |                     19.94 |                        623 |                     20.03 |                        606 |
| footway       |                    282.93 |                      10383 |                    173.72 |                       3612 |
| motorway      |                      8.81 |                         39 |                      8.84 |                         20 |
| parking_aisle |                    112.42 |                       5640 |                    112.11 |                       4961 |
| path          |                     37.14 |                       1004 |                     37.33 |                        871 |
| pedestrian    |                      2.54 |                         42 |                      2.65 |                         39 |
| primary       |                     39.02 |                        878 |                     39.19 |                        851 |
| residential   |                    586.56 |                      12918 |                    589.78 |                      12795 |
| secondary     |                     23.59 |                        669 |                     23.7  |                        653 |
| service       |                      0    |                          0 |                     61.69 |                       1434 |
| sidewalk      |                      0    |                          0 |                    101.61 |                       2331 |
| steps         |                      4.41 |                        410 |                      4.43 |                        403 |
| tertiary      |                    179.86 |                       4240 |                    180.88 |                       4118 |
| track         |                     66.23 |                        726 |                     66.83 |                        666 |
| trunk         |                     26.57 |                        536 |                     27.01 |                        535 |
| unclassified  |                    309.99 |                       4874 |                    313.14 |                       4629 |
| unknown       |                     59.64 |                       1490 |                      0    |                          0 |

#### *Higashihiroshima*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      1.45 |                          6 |
| alley         |                      0.49 |                          8 |                      0.49 |                          8 |
| crosswalk     |                      0    |                          0 |                      2.21 |                        288 |
| cycleway      |                      2.93 |                         30 |                      2.93 |                         28 |
| driveway      |                      4.96 |                        174 |                      4.96 |                        176 |
| footway       |                     95.8  |                       2036 |                     34.11 |                        809 |
| motorway      |                     16.51 |                         39 |                     17.13 |                         16 |
| parking_aisle |                     25.93 |                        843 |                     24.63 |                        806 |
| path          |                     50.36 |                        589 |                     50.38 |                        559 |
| pedestrian    |                      0.49 |                         11 |                      0.49 |                         11 |
| primary       |                     13.56 |                        135 |                     13.65 |                        127 |
| residential   |                    325.15 |                       4656 |                    326.47 |                       4529 |
| secondary     |                     23.23 |                        289 |                     23.37 |                        278 |
| service       |                      0    |                          0 |                     62.18 |                       1170 |
| sidewalk      |                      0    |                          0 |                     59.53 |                        720 |
| steps         |                      1.82 |                        140 |                      1.73 |                        126 |
| tertiary      |                     87.21 |                       1299 |                     87.93 |                       1234 |
| track         |                     22.16 |                        180 |                     21.95 |                        171 |
| trunk         |                     39.9  |                        349 |                     40.19 |                        313 |
| unclassified  |                    169.9  |                       2088 |                    170.46 |                       1938 |
| unknown       |                     60.76 |                       1188 |                      0    |                          0 |

#### *Kumamoto*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     21.18 |                        403 |                     21.45 |                        406 |
| crosswalk     |                      0    |                          0 |                      2.67 |                        252 |
| cycleway      |                      4.32 |                         34 |                      4.32 |                         34 |
| driveway      |                      2.84 |                         57 |                      2.89 |                         58 |
| footway       |                     84.17 |                       1673 |                     36.04 |                        657 |
| motorway      |                      0.1  |                          2 |                      0.41 |                          4 |
| parking_aisle |                      7.34 |                        200 |                      7.27 |                        203 |
| path          |                     44.6  |                        348 |                     44.79 |                        316 |
| pedestrian    |                      2.25 |                         70 |                      2.26 |                         59 |
| primary       |                     29.91 |                        347 |                     30.49 |                        343 |
| residential   |                    280.19 |                       4203 |                    282.91 |                       4194 |
| secondary     |                     43.54 |                        518 |                     43.7  |                        493 |
| service       |                      0    |                          0 |                     57.5  |                        956 |
| sidewalk      |                      0    |                          0 |                     45.77 |                        538 |
| steps         |                      0.95 |                         93 |                      1.01 |                         94 |
| tertiary      |                    111.51 |                       1534 |                    113.13 |                       1547 |
| track         |                     60.22 |                        314 |                     61.64 |                        328 |
| trunk         |                     51.04 |                        486 |                     51.55 |                        450 |
| unclassified  |                    497.8  |                       7781 |                    503.14 |                       7673 |
| unknown       |                     57.55 |                        982 |                      0    |                          0 |

#### *Morioka*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      0.3  |                          4 |
| alley         |                     23.71 |                        528 |                     23.74 |                        526 |
| crosswalk     |                      0    |                          0 |                      6.27 |                        835 |
| cycleway      |                      8.16 |                         26 |                      8.21 |                         19 |
| driveway      |                      0.35 |                         10 |                      0.35 |                          8 |
| footway       |                    144.53 |                       3365 |                     46.21 |                        854 |
| motorway      |                     22.66 |                        126 |                     22.88 |                         49 |
| parking_aisle |                      8.48 |                        243 |                      8.47 |                        235 |
| path          |                     33.51 |                        451 |                     33.82 |                        444 |
| pedestrian    |                      9.65 |                        160 |                      9.84 |                        150 |
| primary       |                     25.45 |                        275 |                     25.67 |                        261 |
| residential   |                    344.3  |                       4787 |                    347.56 |                       4798 |
| secondary     |                     14.21 |                        210 |                     14.21 |                        199 |
| service       |                      0    |                          0 |                     42.33 |                        920 |
| sidewalk      |                      0    |                          0 |                     94.09 |                       1394 |
| steps         |                      3.08 |                        162 |                      3.12 |                        160 |
| tertiary      |                    136.65 |                       1878 |                    137.75 |                       1818 |
| track         |                     26.2  |                        174 |                     26.59 |                        173 |
| trunk         |                     38.79 |                        399 |                     39.58 |                        335 |
| unclassified  |                    296.04 |                       4726 |                    297.48 |                       4637 |
| unknown       |                     41.83 |                        911 |                      1.05 |                          2 |

#### *Paris*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      0.18 |                          6 |
| alley         |                     24.51 |                        850 |                     24.5  |                        692 |
| crosswalk     |                      0    |                          0 |                     70.48 |                      16002 |
| cycleway      |                    177.07 |                       5502 |                    178.42 |                       5131 |
| driveway      |                     18.38 |                        749 |                     18.17 |                        626 |
| footway       |                   2138.81 |                     117400 |                    507.79 |                      33458 |
| living_street |                     44.83 |                       1545 |                     45.33 |                       1501 |
| motorway      |                      0.03 |                          2 |                      0.04 |                          3 |
| parking_aisle |                     30.32 |                       1142 |                     28.79 |                       1015 |
| path          |                      9.87 |                        314 |                     10.01 |                        307 |
| pedestrian    |                    100.5  |                       3435 |                    101.04 |                       3181 |
| primary       |                    138.28 |                       4036 |                    139.46 |                       3815 |
| residential   |                    546.22 |                      17430 |                    550.89 |                      17151 |
| secondary     |                    106.28 |                       3535 |                    107.43 |                       3377 |
| service       |                      0    |                          0 |                    191.39 |                       5480 |
| sidewalk      |                      0    |                          0 |                   1523.6  |                      44341 |
| steps         |                     39.37 |                       4915 |                     24.45 |                       3427 |
| tertiary      |                    101.51 |                       3480 |                    102.7  |                       3370 |
| track         |                      0.72 |                          7 |                      0.72 |                          5 |
| trunk         |                      9.34 |                         69 |                     10.34 |                         47 |
| unclassified  |                     28.08 |                       1011 |                     28.15 |                        979 |
| unknown       |                    193.73 |                       6444 |                      3.36 |                         79 |

#### *Riyadh*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      1.34 |                         20 |
| alley         |                      1.58 |                         19 |                      1.61 |                         20 |
| driveway      |                     29.01 |                        356 |                     28.58 |                        419 |
| footway       |                     34.64 |                        522 |                     34.78 |                        530 |
| living_street |                     24.51 |                        268 |                     25.53 |                        302 |
| motorway      |                    133.03 |                        436 |                    136.24 |                        341 |
| parking_aisle |                     58.61 |                       1074 |                     56.76 |                       1086 |
| path          |                      0.48 |                         15 |                      0.48 |                         15 |
| pedestrian    |                      6.22 |                         53 |                      7.08 |                         62 |
| primary       |                    445.04 |                       4159 |                    450.3  |                       4175 |
| residential   |                   3140.02 |                      43295 |                   3275.52 |                      48161 |
| secondary     |                    361.18 |                       4031 |                    365.3  |                       4245 |
| service       |                      0    |                          0 |                    589.54 |                       9309 |
| sidewalk      |                      0    |                          0 |                      0.15 |                          4 |
| steps         |                      1.31 |                         58 |                      1.29 |                         55 |
| tertiary      |                    563.85 |                       6540 |                    573.89 |                       7071 |
| track         |                      0.81 |                         10 |                      0.84 |                         11 |
| trunk         |                     38.33 |                        156 |                     39.33 |                        133 |
| unclassified  |                     73.58 |                        718 |                     76.36 |                        834 |
| unknown       |                    398.52 |                       5865 |                      0.56 |                          9 |

#### *Tateyama*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      0.25 |                          2 |
| alley         |                     33.64 |                        527 |                     33.53 |                        510 |
| crosswalk     |                      0    |                          0 |                      2.76 |                        549 |
| driveway      |                      3.7  |                         75 |                      3.59 |                         70 |
| footway       |                     13.01 |                        792 |                      5.66 |                         99 |
| parking_aisle |                      6.86 |                        145 |                      6.36 |                        140 |
| path          |                     64.59 |                        345 |                     64.85 |                        313 |
| pedestrian    |                      0.05 |                          2 |                      0.05 |                          2 |
| primary       |                      6.09 |                         67 |                      6.14 |                         59 |
| residential   |                    264.45 |                       3887 |                    265.12 |                       3722 |
| secondary     |                     24.72 |                        473 |                     24.78 |                        447 |
| service       |                      0    |                          0 |                     16.56 |                        289 |
| sidewalk      |                      0    |                          0 |                      4.6  |                         71 |
| steps         |                      0.46 |                         24 |                      0.46 |                         24 |
| tertiary      |                     36.7  |                        504 |                     36.78 |                        489 |
| track         |                    104.91 |                        775 |                    105.22 |                        699 |
| trunk         |                     23.3  |                        288 |                     23.4  |                        263 |
| unclassified  |                     28.56 |                        294 |                     28.97 |                        280 |
| unknown       |                     15.34 |                        298 |                      0    |                          0 |

#### *Tokyo*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| None          |                      0    |                          0 |                      0.79 |                         10 |
| alley         |                    145.02 |                       4035 |                    145.7  |                       4054 |
| bridleway     |                      0.02 |                          1 |                      0.02 |                          1 |
| crosswalk     |                      0    |                          0 |                     51.3  |                       7134 |
| cycleway      |                     11.24 |                        191 |                     11.44 |                        189 |
| driveway      |                     12.63 |                        469 |                     12.9  |                        473 |
| footway       |                   1104    |                      48111 |                    451.09 |                      18294 |
| living_street |                      0.16 |                          7 |                      0.16 |                          7 |
| motorway      |                     87.28 |                        387 |                     88.38 |                        231 |
| parking_aisle |                     16.52 |                        627 |                     15.45 |                        587 |
| path          |                     34.52 |                       1050 |                     34.68 |                       1048 |
| pedestrian    |                     27.82 |                        828 |                     27.92 |                        796 |
| primary       |                    105.79 |                       2710 |                    106.8  |                       2582 |
| residential   |                    694.29 |                      20945 |                    697.43 |                      20996 |
| secondary     |                    132.79 |                       3593 |                    135.29 |                       3469 |
| service       |                      0    |                          0 |                    128.82 |                       3588 |
| sidewalk      |                      0    |                          0 |                    597.58 |                      15679 |
| steps         |                     20.82 |                       2061 |                     19.62 |                       1866 |
| tertiary      |                    234.88 |                       7662 |                    235.96 |                       7546 |
| trunk         |                     59.45 |                       1513 |                     59.87 |                       1466 |
| unclassified  |                    392.17 |                      12553 |                    394.88 |                      12566 |
| unknown       |                    127.09 |                       3719 |                      0.34 |                          2 |
