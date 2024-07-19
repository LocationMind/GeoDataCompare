curl -v -u admin:geoserver -XPOST -d "<workspace><name>test</name></workspace>" -H "Content-type: text/xml"  http://localhost:8080/geoserver/rest/workspaces
curl -v -u admin:geoserver -XPOST -T connect_omf.xml -H "Content-type: text/xml" http://localhost:8080/geoserver/rest/workspaces/test/datastores
curl -v -u admin:geoserver -XPOST -H "Content-type: text/xml" -d "<featureType><name>edge_with_cost_tokyo_omf</name><nativeName>edge_with_cost_tokyo</nativeName><title>edge_with_cost_tokyo_omf</title></featureType>" http://localhost:8080/geoserver/rest/workspaces/test/datastores/pgrouting_omf/featuretypes
curl -v -u admin:geoserver -XPOST -H "Content-type: text/xml" -d "<featureType><name>node_tokyo_omf</name><nativeName>node_tokyo</nativeName><title>node_tokyo_omf</title></featureType>" http://localhost:8080/geoserver/rest/workspaces/test/datastores/pgrouting_omf/featuretypes
curl -v -u admin:geoserver -XPOST -H  "accept: application/json" -H  "content-type: application/xml" -d "<rules><rule resource=\"pgrouting_omf.edge_with_cost_tokyo_omf .r\">*</rule></rules>" http://localhost:8080/geoserver/rest/security/acl/layers
curl -v -u admin:geoserver -XPOST -H  "accept: application/json" -H  "content-type: application/xml" -d "<rules><rule resource=\"pgrouting_omf.node_tokyo_omf .r\">*</rule></rules>" http://localhost:8080/geoserver/rest/security/acl/layers