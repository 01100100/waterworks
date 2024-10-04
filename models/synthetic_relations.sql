WITH features AS (
  SELECT
    datetime,
    strava_activity_id,
    strava_owner_id,
    unnest(intersecting_waterways.features) AS feature
  FROM {{ ref('staging') }}
  {% if is_incremental() %}

WHERE datetime >= (select max(modelled_at) from {{ this }} )

{% endif %}
)

SELECT
  feature.id,
  features.strava_activity_id,
  features.strava_owner_id,
  feature.properties->>'name' AS name,
  feature.properties as properties,
  -- if there is collectedProperties, 
  st_geomfromgeojson(feature.geometry) AS geom,
  datetime as modelled_at
FROM features
WHERE feature.id LIKE 'syntheticRelation/%'
