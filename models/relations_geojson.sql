select 
    osm_relations.id,
    osm_relations.name,
    osm_relations.geom as geom,
    nom.country as country_code_2,
    count(rel.osm_id) as waterway_crossings
from {{ ref("osm_relations") }} as osm_relations
left join {{ ref("nominatim_parsed") }} as nom
on osm_relations.osm_id = nom.osm_id
join {{ ref("relations") }} as rel
on osm_relations.osm_id = rel.osm_id
group by osm_relations.id, osm_relations.name, osm_relations.geom, nom.country