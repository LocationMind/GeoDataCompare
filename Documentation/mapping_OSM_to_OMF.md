# Mapping OpenStreetMap (OSM) classes to OvertureMap Foundation (OMF) classes (road data)

# OMF Classes

OMF road data have 21 different classes, not always represented as a possible value for the highway key in OSM data. The classes are these one :

- [Mapping OpenStreetMap (OSM) classes to OvertureMap Foundation (OMF) classes (road data)](#mapping-openstreetmap-osm-classes-to-overturemap-foundation-omf-classes-road-data)
- [OMF Classes](#omf-classes)
  - [`motorway` class](#motorway-class)
  - [`trunk` class](#trunk-class)
  - [`primary` class](#primary-class)
  - [`secondary` class](#secondary-class)
  - [`tertiary` class](#tertiary-class)
  - [`residential` class](#residential-class)
  - [`living_street` class](#living_street-class)
  - [`unclassified` class](#unclassified-class)
  - [`parking_aisle` class](#parking_aisle-class)
  - [`driveway` class](#driveway-class)
  - [`alley` class](#alley-class)
  - [`pedestrian` class](#pedestrian-class)
  - [`footway` class](#footway-class)
  - [`sidewalk` class](#sidewalk-class)
  - [`crosswalk` class](#crosswalk-class)
  - [`steps` class](#steps-class)
  - [`path` class](#path-class)
  - [`track` class](#track-class)
  - [`cycleway` class](#cycleway-class)
  - [`bridleway` class](#bridleway-class)
  - [`unknown` class](#unknown-class)

For each class, we will try to find ways to map OSM data to it.
Sometimes it will be really easy as it is directly in the highway tag, sometimes a little bit more complicated as it is in highway tag and other tags too.

## `motorway` class

In OSM data, we can find the tag `highway=motorway` for the main motorway and `highway=motorway_link` for motorways links.
These values can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `trunk` class

In OSM data, we can find the tag `highway=trunk` for the main trunk roads and `highway=trunk_link` for trunk road links.
These values can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `primary` class

In OSM data, we can find the tag `highway=primary` for the main primary roads and `highway=primary_link` for primary road links.
These values can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `secondary` class

In OSM data, we can find the tag `highway=secondary` for the main secondary roads and `highway=secondary_link` for secondary road links.
These values can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `tertiary` class

In OSM data, we can find the tag `highway=tertiary` for the main tertiary roads and `highway=tertiary_link` for tertiary road links.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `residential` class

In OSM data, we can find the tag `highway=residential` for residential roads.
Also, the tag `abutters=residential` can also be used combined with other value of `highway`, such as `highway=unclassified` and `abutters=residential`.
The residential class can be find in OSMnx integrated data, but the first graph analysis made on the total length kilometer by classes shows that there is a little difference between the OSM and OMF data (see [these results](./Comparison-OSM-OvertureMap_PgRouting.md#total-kilometer-of-roads-by-type)).
It could be useful to have a look inside those results to see why this difference exists, and if it could have an impact on the mapping or if it is just 

## `living_street` class

In OSM data, we can find the tag `highway=living_street` for living streets.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `unclassified` class

In OSM data, we can find the tag `highway=unclassified` for unclassified roads.
Unclassified roads are different from unknown roads, it refers to roads with less importance than tertiary roads.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

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

In OSM data, we can find the tag `highway=pedestrian` for pedestrian ways.
The `alley` class does not exist directly in OSMnx integrated data, but by combining the value of the class and service attribute, we might be able to find it again.

## `footway` class

In OSM data, we can find the tag `highway=footway` for footways, ie "minor pathways which are used mainly or exclusively by pedestrians" (https://wiki.openstreetmap.org/wiki/Tag:highway%3Dfootway).
However, if the key `footway` is used, then it should not be mapped with the `footway` class, but with the class defined by the tag `footway=*`, such as sidewalk or crossings for instance.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `sidewalk` class

In OSM data, we can find the tag `highway=footway` or `highway=path` used with `footway=sidewalk` for sidewalks.
However, there are no information about the `footway` value in OSMnx integrated data.
It will be necessary to find a way to get this information again (maybe by using the OSM id of the road).

## `crosswalk` class

In OSM data, we can find the tag `highway=footway` or `highway=path` used with `footway=crossing` for sidewalks.
However, there are no information about the `footway` value in OSMnx integrated data.
It will be necessary to find a way to get this information again (maybe by using the OSM id of the road).
Another possibility could be to used nodes information, as some nodes have in their `highway` attribute a value equals to `crossing`, indicating that the node correspond to a crosswalk.
But this information is not always indicated in the node attributes, so the OSM id might be the way to use it.

## `steps` class

In OSM data, we can find the tag `highway=steps` for steps.
This value seems to be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.
However, the first results on the number of kilometer for each class shown a difference between the number of steps in both dataset, up to 10 kilometers.
Because of this difference, it might be possible that other tags or things like that might be used and that step roads are mapped in another class.

## `path` class

In OSM data, we can find the tag `highway=path` for generic paths.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `track` class

In OSM data, we can find the tag `highway=track` for tracks.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `cycleway` class

In OSM data, we can find the tag `highway=cycleway` for cycleways.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `bridleway` class

In OSM data, we can find the tag `highway=bridleway` for bridleways, ie ways for horse riding mainly.
This value can also be find in OSMnx integrated data, directly in the class attribute, so the mapping should be easy.

## `unknown` class

Unknown class does not exist in OSM data.
However, when comparing OSM and OMF data quickly, I noticed that most of the `unknown` road in OMF dataset were roads with `service` class and no value in `service` attribute in OSM data.
It is not always true, but most of the time it is.