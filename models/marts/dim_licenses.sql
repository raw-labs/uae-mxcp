{{ config(materialized='table', tags=["marts"]) }}

{% set dms_to_dd %}
CREATE OR REPLACE MACRO dms_to_dd(dms) AS (
    CASE
        WHEN dms IS NULL THEN NULL
        ELSE (
            WITH p AS (
                SELECT
                    NULLIF(regexp_extract(dms,'([0-9]+)',1),'')::DOUBLE            AS deg ,
                    NULLIF(regexp_extract(dms,'[0-9]+.*?([0-9]+)',1),'')::DOUBLE   AS minu ,
                    NULLIF(regexp_extract(dms,'([0-9.]+)[^0-9]*[NSEW]',1),'')::DOUBLE AS sec ,
                    regexp_extract(dms,'([NSEW])$',1)                              AS hemi
            )
            SELECT
                CASE
                    WHEN deg IS NULL OR minu IS NULL OR sec IS NULL OR hemi = ''
                    THEN NULL                       -- malformed DMS → NULL
                    ELSE
                        (CASE WHEN hemi IN ('S','W') THEN -1 ELSE 1 END) *
                        (deg + minu/60 + sec/3600)
                END
            FROM p
        )
    END
);
{% endset %}

{% do run_query(dms_to_dd) %}

SELECT
    -- corrected field name (bl_num) -> now corrected to include activity to create a unique PK
    md5(
        COALESCE(issuance_authority_en, '') || '|' ||
        COALESCE(bl, '') || '|' ||
        COALESCE(business_activity_code, '') || '|' ||
        COALESCE(business_activity_desc_en, '')
    ) AS license_pk,
    s.*,

    -- proper DATEs
    STRPTIME(bl_est_date, '%d/%m/%Y')::DATE            AS bl_est_date_d,
    STRPTIME(bl_exp_date, '%d/%m/%Y')::DATE            AS bl_exp_date_d,

    -- decimal degrees (safe macro)
    dms_to_dd(license_latitude)                        AS lat_dd,
    dms_to_dd(license_longitude)                       AS lon_dd
FROM {{ ref('stg_licenses_raw') }} AS s
