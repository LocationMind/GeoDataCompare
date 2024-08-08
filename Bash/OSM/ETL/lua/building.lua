local building = osm2pgsql.define_area_table('building', {
    -- Define an autoincrementing id column, QGIS likes a unique id on the table
    { column = 'id', sql_type = 'serial', create_only = true },
    { column = 'geom', type = 'multipolygon', not_null = true, projection = 4326},
    -- Add columns for tags
    { column = 'building', type = 'text' },
    { column = 'height', type = 'text' }
}, { indexes = {
    -- So we get an index on the id column
    { column = 'id', method = 'btree', unique = true },
    -- If we define any indexes we don't get the default index on the geometry
    -- column, so we add it here.
    { column = 'geom', method = 'gist' }
}})

function osm2pgsql.process_way(object)
    if object.is_closed and object.tags.building then
        building:insert({
            geom = object:as_polygon():transform(4326),
            building = object.tags.building,  -- Example: Assuming 'building' tag
            height = object.tags.height  -- Example: Assuming 'height' tag
        })
    end
end

function osm2pgsql.process_relation(object)
    if object.tags.type == 'multipolygon' and object.tags.building then
        -- From the relation we get multipolygons...
        local mp = object:as_multipolygon():transform(4326)
        -- ...and split them into polygons which we insert into the table
        for geom in mp:geometries() do
            building:insert({
                geom = geom,
                building = object.tags.building,  -- Example: Assuming 'building' tag
                height = object.tags.height  -- Example: Assuming 'height' tag
            })
        end
    end
end
