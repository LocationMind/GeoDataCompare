# Mapping OpenStreetMap (OSM) classes to OvertureMap Foundation (OMF) classes (road data)

# OMF Classes

OMF road data have 18 different classes, not always represented as a possible value for the highway key in OSM data. The classes are these one :


`motorway`

`primary`

`secondary`

`tertiary`

`residential`

`living_street`

`trunk`

`unclassified`

`parking_aisle`

`driveway`

`alley`

`pedestrian`

`footway`

`sidewalk`

`crosswalk`

`steps`

`path`

`track`

`cycleway`

`bridleway`

`unknown`

For each class, we will try to find ways to map OSM data to it.
Sometimes it will be really easy as it is directly in the highway tag, sometimes a little bit more complicated as it is in highway tag and other tags too.

## `motorway` class

In OSM data, we can find the tag `highway=motorway` for the main motorway and `highway=motorway_link` for motorways links.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `primary` class

In OSM data, we can find the tag `highway=primary` for the main primary roads and `highway=primary_link` for primary road links.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `secondary` class

In OSM data, we can find the tag `highway=secondary` for the main secondary roads and `highway=secondary_link` for secondary road links.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `tertiary` class

In OSM data, we can find the tag `highway=tertiary` for tertiary roads.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `residential` class

In OSM data, we can find the tag `highway=residential` for residential roads.
Also, the tag `abutters=residential` can also be used combined with other value of `highway`, such as `highway=unclassified` and `abutters=residential`.
The residential class can be find in OSMnx integrated data, but the first graph analysis made on the total length kilometer by classes shows that there is a little difference between the OSM and OMF data (see [these results](./Comparison-OSM-OvertureMap_PgRouting.md#total-kilometer-of-roads-by-type)).
It could be useful to have a look inside those results to see why this difference exists, and if it could have an impact on the mapping or if it is just 

## `living_street` class

In OSM data, we can find the tag `highway=living_street` for living streets.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `trunk` class

In OSM data, we can find the tag `highway=trunk` for the main trunk roads and `highway=trunk_link` for trunk road links.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `unclassified` class

In OSM data, we can find the tag `highway=unclassified` for unclassified roads.
Unclassified roads are different from unknown roads, it refers to roads with less importance than tertiary roads.
These can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `parking_aisle` class

In OSM data, we can find the tag `highway=service` used with `service=parking_aisle` for parking aisle.
The `parking_aisle` class does not exist directly in OSMnx integrated data, but by combining the value of the class and service attribute, we might be able to find it again.

## `driveway` class

In OSM data, we can find the tag `highway=service` used with `service=driveway` for driveway.
The `driveway` class does not exist directly in OSMnx integrated data, but by combining the value of the class and service attribute, we might be able to find it again.

## `alley` class

In OSM data, we can find the tag `highway=service` used with `service=alley` for alley.
The `alley` class does not exist directly in OSMnx integrated data, but by combining the value of the class and service attribute, we might be able to find it again.

## `pedestrian` class

In OSM data, we can find the tag `highway=pedestrian` for pedestrian ways. Also
The `alley` class does not exist directly in OSMnx integrated data, but by combining the value of the class and service attribute, we might be able to find it again.

## `footway` class



## `sidewalk` class



## `crosswalk` class



## `steps` class



## `path` class



## `track` class



## `cycleway` class



## `bridleway` class



## `unknown` class

