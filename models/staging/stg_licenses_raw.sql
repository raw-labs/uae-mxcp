{{ config(materialized='view') }}

WITH src AS (
    SELECT * FROM {{ ref('src_licenses') }}
)

SELECT
    -- every original column …
    src.*,

    -- … then REPLACE the two that need cleaning
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
      src.license_latitude,  'º','°'),'˚','°'),'′',''''),'’',''''),'″','"'),'”','"')
      AS license_latitude,

    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
      src.license_longitude, 'º','°'),'˚','°'),'′',''''),'’',''''),'″','"'),'”','"')
      AS license_longitude
FROM src
-- DuckDB’s SELECT list rules: later columns override earlier ones,
-- so the cleaned versions replace the raw duplicates automatically.
