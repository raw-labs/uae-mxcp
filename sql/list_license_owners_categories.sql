SELECT DISTINCT
  CASE 
    WHEN $field = 'owner_pk' THEN owner_pk
    WHEN $field = 'license_pk' THEN license_pk
    WHEN $field = 'owner_gender' THEN owner_gender
    WHEN $field = 'nationality' THEN nationality
    WHEN $field = 'owner_type' THEN owner_type
    WHEN $field = 'email' THEN email
    WHEN $field = 'is_primary_owner' THEN is_primary_owner
    WHEN $field = 'is_active' THEN is_active
    WHEN $field = 'requires_approval' THEN requires_approval
  END as value,
  CASE 
    WHEN $includeCount THEN COUNT(*)
    ELSE NULL
  END as count
FROM fact_license_owners_v1
WHERE CASE 
    WHEN $field = 'owner_pk' THEN owner_pk
    WHEN $field = 'license_pk' THEN license_pk
    WHEN $field = 'owner_gender' THEN owner_gender
    WHEN $field = 'nationality' THEN nationality
    WHEN $field = 'owner_type' THEN owner_type
    WHEN $field = 'email' THEN email
    WHEN $field = 'is_primary_owner' THEN is_primary_owner
    WHEN $field = 'is_active' THEN is_active
    WHEN $field = 'requires_approval' THEN requires_approval
  END IS NOT NULL
GROUP BY value
ORDER BY count DESC NULLS LAST, value