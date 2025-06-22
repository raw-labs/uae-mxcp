{{ config(materialized='view') }}

-- Generate synthetic license owners data for testing multi-model functionality
WITH license_sample AS (
  SELECT DISTINCT license_pk 
  FROM {{ ref('dim_licenses') }}
  LIMIT 20  -- Use small subset for testing
),

owners_data AS (
  SELECT 
    'OWN-' || LPAD(CAST(ROW_NUMBER() OVER (ORDER BY license_pk, bl, bl_name_en, bl_est_date) AS VARCHAR), 6, '0') AS owner_pk,
    license_pk,
    
    CASE (CAST(SUBSTR(license_pk, -1) AS INTEGER) % 10)
      WHEN 0 THEN 'Ahmed Al Rashid'
      WHEN 1 THEN 'Fatima Al Zahra'
      WHEN 2 THEN 'Mohammed Hassan'
      WHEN 3 THEN 'Aisha Abdullah'
      WHEN 4 THEN 'Omar Al Maktoum'
      WHEN 5 THEN 'Layla Al Qasimi'
      WHEN 6 THEN 'Khalid Al Nahyan'
      WHEN 7 THEN 'Mariam Al Shamsi'
      WHEN 8 THEN 'Saeed Al Mansoori'
      ELSE 'Noura Al Suwaidi'
    END AS owner_name,
    
    CASE 
      WHEN owner_name LIKE '%Fatima%' OR owner_name LIKE '%Aisha%' 
           OR owner_name LIKE '%Layla%' OR owner_name LIKE '%Mariam%'
           OR owner_name LIKE '%Noura%'
      THEN 'Female'
      ELSE 'Male'
    END AS owner_gender,
    
    CASE (CAST(SUBSTR(license_pk, -2, 1) AS INTEGER) % 5)
      WHEN 0, 1, 2 THEN 'UAE'
      WHEN 3 THEN 'India'
      ELSE 'Other'
    END AS nationality,
    
    'Primary' AS owner_type,
    75.0 AS ownership_percentage,
    '+971-50-1234567' AS phone_number,
    LOWER(REPLACE(owner_name, ' ', '.')) || '@gmail.com' AS email,
    CASE WHEN nationality = 'UAE' THEN '784-1990-1234567-1' ELSE NULL END AS emirates_id,
    DATE('2020-01-01') AS owner_registration_date,
    true AS is_primary_owner,
    true AS is_active,
    false AS requires_approval,
    CURRENT_TIMESTAMP AS created_at,
    'data_generator' AS created_by
    
  FROM license_sample
)

SELECT * FROM owners_data 