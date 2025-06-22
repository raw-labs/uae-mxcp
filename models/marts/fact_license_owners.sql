{{ config(
    materialized='table',
    contract={'enforced': true}
) }}

-- License owners fact table - contains ownership information for business licenses
SELECT 
  owner_pk,
  license_pk,
  owner_name,
  owner_gender,
  nationality,
  owner_type,
  ownership_percentage,
  phone_number,
  email,
  emirates_id,
  owner_registration_date,
  is_primary_owner,
  is_active,
  requires_approval,
  created_at,
  created_by
FROM {{ ref('stg_license_owners') }} 