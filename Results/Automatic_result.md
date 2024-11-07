# Quality criterias result between OpenStreetMap and Overture Maps Foundation datasets

The test were run on 07/11/2024 15:05, using the 2024-09-18.0 release of Overture Maps Foundation data and the OpenStreetMap data until 2024-08-31.

## General results

| **Criterion**                                | **Area**           |   **OSM Value** |   **OMF Value** |   **Difference (abs)** |
|----------------------------------------------|--------------------|-----------------|-----------------|------------------------|
| **1. Number of nodes**                       | *Hamamatsu*        |     33022       |      28547      |            4475        |
| **1. Number of nodes**                       | *Higashihiroshima* |     10420       |       9683      |             737        |
| **1. Number of nodes**                       | *Kumamoto*         |     13634       |      13204      |             430        |
| **1. Number of nodes**                       | *Morioka*          |     13178       |      12581      |             597        |
| **1. Number of nodes**                       | *Paris*            |    126007       |      99176      |           26831        |
| **1. Number of nodes**                       | *Riyadh*           |     45268       |      55652      |           10384        |
| **1. Number of nodes**                       | *Tateyama*         |      6817       |       6351      |             466        |
| **1. Number of nodes**                       | *Tokyo*            |     75434       |      67700      |            7734        |
| **10. Places density**                       | *Hamamatsu*        |       124.014   |         29.4542 |              94.5601   |
| **10. Places density**                       | *Higashihiroshima* |        20.1522  |         21.0016 |               0.849328 |
| **10. Places density**                       | *Kumamoto*         |        28.4591  |         83.0436 |              54.5845   |
| **10. Places density**                       | *Morioka*          |        32.2209  |         60.255  |              28.0342   |
| **10. Places density**                       | *Paris*            |      1283.94    |       1401.41   |             117.471    |
| **10. Places density**                       | *Riyadh*           |         9.24783 |         53.558  |              44.3102   |
| **10. Places density**                       | *Tateyama*         |        13.0745  |         12.0292 |               1.04534  |
| **10. Places density**                       | *Tokyo*            |       470.066   |        697.358  |             227.292    |
| **2. Number of edges**                       | *Hamamatsu*        |     44818       |      40343      |            4475        |
| **2. Number of edges**                       | *Higashihiroshima* |     14062       |      13313      |             749        |
| **2. Number of edges**                       | *Kumamoto*         |     19045       |      18605      |             440        |
| **2. Number of edges**                       | *Morioka*          |     18439       |      17826      |             613        |
| **2. Number of edges**                       | *Paris*            |    173248       |     144973      |           28275        |
| **2. Number of edges**                       | *Riyadh*           |     67733       |      81292      |           13559        |
| **2. Number of edges**                       | *Tateyama*         |      8496       |       8028      |             468        |
| **2. Number of edges**                       | *Tokyo*            |    110962       |     102988      |            7974        |
| **3. Total length (km)**                     | *Hamamatsu*        |      1775       |       1787      |              12        |
| **3. Total length (km)**                     | *Higashihiroshima* |       942       |        947      |               5        |
| **3. Total length (km)**                     | *Kumamoto*         |      1300       |       1313      |              13        |
| **3. Total length (km)**                     | *Morioka*          |      1178       |       1190      |              12        |
| **3. Total length (km)**                     | *Paris*            |      3727       |       3683      |              44        |
| **3. Total length (km)**                     | *Riyadh*           |      5316       |       5837      |             521        |
| **3. Total length (km)**                     | *Tateyama*         |       627       |        630      |               3        |
| **3. Total length (km)**                     | *Tokyo*            |      3213       |       3222      |               9        |
| **4. Number of connected components**        | *Hamamatsu*        |        52       |         66      |              14        |
| **4. Number of connected components**        | *Higashihiroshima* |        28       |         36      |               8        |
| **4. Number of connected components**        | *Kumamoto*         |       108       |        122      |              14        |
| **4. Number of connected components**        | *Morioka*          |        31       |         42      |              11        |
| **4. Number of connected components**        | *Paris*            |      1168       |       1103      |              65        |
| **4. Number of connected components**        | *Riyadh*           |        49       |         99      |              50        |
| **4. Number of connected components**        | *Tateyama*         |        25       |         28      |               3        |
| **4. Number of connected components**        | *Tokyo*            |       257       |        294      |              37        |
| **5. Number of strong connected components** | *Hamamatsu*        |        99       |        117      |              18        |
| **5. Number of strong connected components** | *Higashihiroshima* |        67       |         54      |              13        |
| **5. Number of strong connected components** | *Kumamoto*         |       134       |        175      |              41        |
| **5. Number of strong connected components** | *Morioka*          |       100       |         80      |              20        |
| **5. Number of strong connected components** | *Paris*            |      1709       |       1733      |              24        |
| **5. Number of strong connected components** | *Riyadh*           |       408       |        620      |             212        |
| **5. Number of strong connected components** | *Tateyama*         |        32       |         31      |               1        |
| **5. Number of strong connected components** | *Tokyo*            |       602       |        705      |             103        |
| **6. Number of isolated nodes**              | *Hamamatsu*        |        12       |          0      |              12        |
| **6. Number of isolated nodes**              | *Higashihiroshima* |         8       |          0      |               8        |
| **6. Number of isolated nodes**              | *Kumamoto*         |        10       |          0      |              10        |
| **6. Number of isolated nodes**              | *Morioka*          |         8       |          0      |               8        |
| **6. Number of isolated nodes**              | *Paris*            |        20       |          0      |              20        |
| **6. Number of isolated nodes**              | *Riyadh*           |        11       |          0      |              11        |
| **6. Number of isolated nodes**              | *Tateyama*         |         3       |          0      |               3        |
| **6. Number of isolated nodes**              | *Tokyo*            |        17       |          0      |              17        |
| **7. Overlap indicator (%)**                 | *Hamamatsu*        |       100       |         98.62   |               1.38     |
| **7. Overlap indicator (%)**                 | *Higashihiroshima* |        99.98    |         96.39   |               3.59     |
| **7. Overlap indicator (%)**                 | *Kumamoto*         |        99.97    |         98.02   |               1.95     |
| **7. Overlap indicator (%)**                 | *Morioka*          |       100       |         97.2    |               2.8      |
| **7. Overlap indicator (%)**                 | *Paris*            |        97.9     |         98.52   |               0.62     |
| **7. Overlap indicator (%)**                 | *Riyadh*           |        99.98    |         90.6    |               9.38     |
| **7. Overlap indicator (%)**                 | *Tateyama*         |       100       |         96.31   |               3.69     |
| **7. Overlap indicator (%)**                 | *Tokyo*            |        99.56    |         98.37   |               1.19     |
| **8. Number of corresponding nodes**         | *Hamamatsu*        |     27919       |      27919      |               0        |
| **8. Number of corresponding nodes**         | *Higashihiroshima* |      9392       |       9392      |               0        |
| **8. Number of corresponding nodes**         | *Kumamoto*         |     12579       |      12579      |               0        |
| **8. Number of corresponding nodes**         | *Morioka*          |     12174       |      12174      |               0        |
| **8. Number of corresponding nodes**         | *Paris*            |     96392       |      96392      |               0        |
| **8. Number of corresponding nodes**         | *Riyadh*           |     44010       |      44010      |               0        |
| **8. Number of corresponding nodes**         | *Tateyama*         |      6166       |       6166      |               0        |
| **8. Number of corresponding nodes**         | *Tokyo*            |     66069       |      66069      |               0        |
| **9. Percentage of corresponding nodes (%)** | *Hamamatsu*        |        84.55    |         97.8    |              13.25     |
| **9. Percentage of corresponding nodes (%)** | *Higashihiroshima* |        90.13    |         96.99   |               6.86     |
| **9. Percentage of corresponding nodes (%)** | *Kumamoto*         |        92.26    |         95.27   |               3.01     |
| **9. Percentage of corresponding nodes (%)** | *Morioka*          |        92.38    |         96.76   |               4.38     |
| **9. Percentage of corresponding nodes (%)** | *Paris*            |        76.5     |         97.19   |              20.69     |
| **9. Percentage of corresponding nodes (%)** | *Riyadh*           |        97.22    |         79.08   |              18.14     |
| **9. Percentage of corresponding nodes (%)** | *Tateyama*         |        90.45    |         97.09   |               6.64     |
| **9. Percentage of corresponding nodes (%)** | *Tokyo*            |        87.59    |         97.59   |              10        |

## Specific results

### Total kilometer of roads by class

#### *Hamamatsu*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     14.41 |                        341 |                     14.12 |                        331 |
| crosswalk     |                      0    |                          0 |                      9.69 |                       1479 |
| driveway      |                     19.94 |                        623 |                     20.03 |                        606 |
| footway       |                    282.93 |                      10383 |                    173.72 |                       3612 |
| motorway      |                      8.81 |                         39 |                      8.84 |                         20 |
| parking_aisle |                    112.42 |                       5640 |                    112.11 |                       4961 |
| path          |                     37.14 |                       1004 |                     37.34 |                        873 |
| pedestrian    |                      2.54 |                         42 |                      2.65 |                         39 |
| primary       |                     39.02 |                        878 |                     39.19 |                        851 |
| residential   |                    586.56 |                      12918 |                    589.86 |                      12797 |
| secondary     |                     23.59 |                        669 |                     23.7  |                        653 |
| service       |                      0    |                          0 |                     61.7  |                       1439 |
| sidewalk      |                      0    |                          0 |                    101.61 |                       2331 |
| steps         |                      4.41 |                        410 |                      4.43 |                        403 |
| tertiary      |                    179.86 |                       4240 |                    180.88 |                       4118 |
| track         |                     66.23 |                        726 |                     66.83 |                        666 |
| trunk         |                     26.57 |                        536 |                     27.01 |                        535 |
| unclassified  |                    309.99 |                       4874 |                    313.14 |                       4629 |
| unknown       |                     59.66 |                       1495 |                      0    |                          0 |

#### *Higashihiroshima*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      0.49 |                          8 |                      0.49 |                          8 |
| crosswalk     |                      0    |                          0 |                      2.21 |                        288 |
| cycleway      |                      2.93 |                         30 |                      2.93 |                         28 |
| driveway      |                      4.96 |                        174 |                      4.96 |                        176 |
| footway       |                     95.8  |                       2038 |                     34.11 |                        809 |
| motorway      |                     16.51 |                         39 |                     17.13 |                         16 |
| parking_aisle |                     25.93 |                        843 |                     24.63 |                        806 |
| path          |                     50.36 |                        589 |                     50.67 |                        561 |
| pedestrian    |                      0.49 |                         11 |                      0.49 |                         11 |
| primary       |                     13.56 |                        135 |                     13.65 |                        127 |
| residential   |                    325.15 |                       4656 |                    326.47 |                       4529 |
| secondary     |                     23.23 |                        295 |                     23.36 |                        278 |
| service       |                      0    |                          0 |                     62.18 |                       1170 |
| sidewalk      |                      0    |                          0 |                     59.53 |                        720 |
| steps         |                      1.82 |                        140 |                      1.73 |                        126 |
| tertiary      |                     87.21 |                       1299 |                     87.93 |                       1234 |
| track         |                     22.16 |                        180 |                     22.35 |                        173 |
| trunk         |                     39.9  |                        349 |                     40.19 |                        313 |
| unclassified  |                    169.9  |                       2088 |                    171.21 |                       1940 |
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
| alley         |                     23.71 |                        528 |                     23.74 |                        526 |
| crosswalk     |                      0    |                          0 |                      6.27 |                        835 |
| cycleway      |                      8.16 |                         26 |                      8.21 |                         19 |
| driveway      |                      0.35 |                         10 |                      0.35 |                          8 |
| footway       |                    144.62 |                       3367 |                     46.3  |                        855 |
| motorway      |                     22.66 |                        126 |                     22.88 |                         49 |
| parking_aisle |                      8.48 |                        243 |                      8.47 |                        235 |
| path          |                     33.51 |                        451 |                     33.82 |                        444 |
| pedestrian    |                      9.65 |                        160 |                      9.84 |                        150 |
| primary       |                     25.45 |                        275 |                     25.67 |                        261 |
| residential   |                    344.51 |                       4789 |                    347.99 |                       4802 |
| secondary     |                     14.21 |                        210 |                     14.21 |                        199 |
| service       |                      0    |                          0 |                     42.33 |                        920 |
| sidewalk      |                      0    |                          0 |                     94.09 |                       1395 |
| steps         |                      3.08 |                        162 |                      3.12 |                        160 |
| tertiary      |                    136.65 |                       1878 |                    137.75 |                       1818 |
| track         |                     26.2  |                        174 |                     26.59 |                        173 |
| trunk         |                     38.79 |                        399 |                     39.58 |                        335 |
| unclassified  |                    296.04 |                       4730 |                    297.57 |                       4640 |
| unknown       |                     41.83 |                        911 |                      1.05 |                          2 |

#### *Paris*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                     24.44 |                        848 |                     24.45 |                        689 |
| crosswalk     |                      0    |                          0 |                     70.56 |                      16013 |
| cycleway      |                    179    |                       5567 |                    180.35 |                       5193 |
| driveway      |                     18.49 |                        757 |                     18.28 |                        632 |
| footway       |                   2152.3  |                     118490 |                    508.9  |                      33619 |
| living_street |                     45.33 |                       1565 |                     45.83 |                       1520 |
| motorway      |                      0.03 |                          2 |                      0.04 |                          3 |
| parking_aisle |                     30.34 |                       1150 |                     28.8  |                       1019 |
| path          |                      9.93 |                        318 |                     10.07 |                        310 |
| pedestrian    |                    101.57 |                       3502 |                    102.06 |                       3234 |
| primary       |                    139.61 |                       4063 |                    140.79 |                       3830 |
| residential   |                    547.18 |                      17522 |                    550.66 |                      17160 |
| secondary     |                    107.94 |                       3575 |                    109.18 |                       3419 |
| service       |                      0    |                          0 |                    191.7  |                       5520 |
| sidewalk      |                      0    |                          0 |                   1533.22 |                      44959 |
| steps         |                     39.4  |                       4924 |                     24.49 |                       3436 |
| tertiary      |                    100.5  |                       3456 |                    101.69 |                       3339 |
| track         |                      0.72 |                          7 |                      0.72 |                          5 |
| trunk         |                      9.34 |                         69 |                     10.34 |                         47 |
| unclassified  |                     26.01 |                        933 |                     27.44 |                        954 |
| unknown       |                    194.1  |                       6500 |                      3.12 |                         72 |

#### *Riyadh*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                      1.58 |                         19 |                      1.61 |                         20 |
| driveway      |                     29.01 |                        356 |                     28.87 |                        439 |
| footway       |                     34.78 |                        526 |                     34.92 |                        535 |
| living_street |                     24.51 |                        268 |                     25.7  |                        317 |
| motorway      |                    133.03 |                        436 |                    136.46 |                        347 |
| parking_aisle |                     58.59 |                       1074 |                     56.78 |                       1114 |
| path          |                      0.48 |                         15 |                      0.48 |                         15 |
| pedestrian    |                      6.22 |                         53 |                      7.08 |                         64 |
| primary       |                    458.58 |                       4245 |                    464.27 |                       4410 |
| residential   |                   3141.32 |                      43336 |                   3278.37 |                      49030 |
| secondary     |                    361.61 |                       4061 |                    365.57 |                       4406 |
| service       |                      0    |                          0 |                    630.78 |                      10141 |
| sidewalk      |                      0    |                          0 |                      0.15 |                          4 |
| steps         |                      1.31 |                         58 |                      1.29 |                         55 |
| tertiary      |                    561.31 |                       6547 |                    571.55 |                       7323 |
| track         |                      0.81 |                         10 |                      0.84 |                         11 |
| trunk         |                     38.33 |                        160 |                     39.3  |                        131 |
| unclassified  |                     73.58 |                        721 |                     76.32 |                        871 |
| unknown       |                    390.06 |                       5848 |                    116.16 |                       2059 |

#### *Tateyama*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
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
| track         |                    104.91 |                        775 |                    105.47 |                        701 |
| trunk         |                     23.3  |                        288 |                     23.4  |                        263 |
| unclassified  |                     28.56 |                        294 |                     28.97 |                        280 |
| unknown       |                     15.34 |                        298 |                      0    |                          0 |

#### *Tokyo*:

| class         |   OSM - Total length (km) |   OSM - Number of entities |   OMF - Total length (km) |   OMF - Number of entities |
|---------------|---------------------------|----------------------------|---------------------------|----------------------------|
| alley         |                    145.37 |                       4051 |                    146.05 |                       4070 |
| bridleway     |                      0.02 |                          1 |                      0.02 |                          1 |
| crosswalk     |                      0    |                          0 |                     51.88 |                       7231 |
| cycleway      |                     11.24 |                        191 |                     11.44 |                        189 |
| driveway      |                     12.63 |                        469 |                     12.9  |                        473 |
| footway       |                   1109.13 |                      48414 |                    451.76 |                      18325 |
| living_street |                      0.16 |                          7 |                      0.16 |                          7 |
| motorway      |                     87.28 |                        388 |                     88.87 |                        233 |
| parking_aisle |                     16.52 |                        627 |                     15.45 |                        587 |
| path          |                     34.52 |                       1050 |                     34.68 |                       1048 |
| pedestrian    |                     27.82 |                        829 |                     27.92 |                        797 |
| primary       |                    105.79 |                       2713 |                    106.8  |                       2585 |
| residential   |                    694.46 |                      20974 |                    697.66 |                      21028 |
| secondary     |                    132.79 |                       3594 |                    135.37 |                       3471 |
| service       |                      0    |                          0 |                    129.11 |                       3632 |
| sidewalk      |                      0    |                          0 |                    601.24 |                      15802 |
| steps         |                     21.08 |                       2111 |                     19.72 |                       1873 |
| tertiary      |                    236.44 |                       7729 |                    237.51 |                       7613 |
| trunk         |                     59.45 |                       1513 |                     59.87 |                       1466 |
| unclassified  |                    390.43 |                      12541 |                    393.14 |                      12555 |
| unknown       |                    127.27 |                       3760 |                      0.34 |                          2 |
