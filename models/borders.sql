SELECT *
FROM {{ source('external', 'raw_country_borders') }}
