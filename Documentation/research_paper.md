# Research paper on data quality assessment

This document is mainly notes taken from the different documents that I read.
It is not a summary of all documents nor a conclusion on which qulity criterias should be used in the end.
Some text has been written by me, some are directly picked from the original documents.

# Documents provided by Kanasugi-san

## 1. *Quality Verification of Volunteered Geographic Information Using OSM Notes Data in a Global Context*

By **Toshikazu Seto**, **Hiroshi Kanasugi** and **Yuichiro Nishimura**, in 2020.

### Goal

Analysing OSM notes (OSM notes are notes written by OSM users for different features on any topic), especially trying to identify regional difference in OSM notes.

### Work done

They have written a "script to convert OSM notes dump to a file that can be analysed on GIS and clarified the geographicla differences in the characteristics of OSM notes, mainly by country, referrring to existing studies."

Planet OSM : OSM full data archive site, where it is possible to download OSM notes dump data (.osn format).
OSM notes : contains a unique id, attributes of the firest user to the post and a timestamp / Features of OSM notes properties contains the OSM notes id, lat, lon, timestamp and info about the username, user id and post status.
Possible to transform OSM notes into GIS data with OSM XML formatted transformable script.

OSM Notes provides a good analysis but may not be enough to assess data qulity assessment.
This is particularly true for our case : we are trying to find quality criterias for both OSM and OvertureMap data, so using OSM notes is not sufficient for out study (we cannot use it for OvertureMap data).

These research could be probably continued now as more and more AI tools could be used to analyse the content of the text.