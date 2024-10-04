WITH count_of_countries_with_waterways_crossed AS (
    SELECT
        count(country) AS count
    FROM {{ ref("country") }}
    WHERE country.waterway_realtions_crossed > 0
),
count_of_relations AS (
    SELECT
        count(osm_id) AS count
    FROM {{ ref("osm_relations") }}
),
count_of_strava_users AS (
    SELECT
        count(strava_owner_id) AS count
    FROM {{ ref("owner") }}
),
count_of_strava_activities AS (
    SELECT
        count(distinct strava_activity_id) AS count
    FROM {{ ref("staging") }}
),
count_of_relation_crossing AS (
    SELECT
        count(*) AS count
    FROM {{ ref("relations") }}
)

SELECT
    (SELECT count FROM count_of_countries_with_waterways_crossed) AS count_of_countries,
    (SELECT count FROM count_of_relations) AS count_of_relations,
    (SELECT count FROM count_of_strava_users) AS count_of_strava_users,
    (SELECT count FROM count_of_strava_activities) AS count_of_strava_activities,
    (SELECT count FROM count_of_relation_crossing) AS count_of_relation_crossing