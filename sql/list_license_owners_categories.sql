SELECT DISTINCT
  CASE 
    WHEN $field = 'owner_pk' THEN CAST(owner_pk AS VARCHAR)
    WHEN $field = 'license_pk' THEN CAST(license_pk AS VARCHAR)
    WHEN $field = 'owner_gender' THEN CAST(owner_gender AS VARCHAR)
    WHEN $field = 'nationality' THEN CAST(nationality AS VARCHAR)
    WHEN $field = 'owner_type' THEN CAST(owner_type AS VARCHAR)
    WHEN $field = 'email' THEN CAST(email AS VARCHAR)
    WHEN $field = 'is_primary_owner' THEN CAST(is_primary_owner AS VARCHAR)
    WHEN $field = 'is_active' THEN CAST(is_active AS VARCHAR)
    WHEN $field = 'requires_approval' THEN CAST(requires_approval AS VARCHAR)
  END as value,
  CASE 
    WHEN $includeCount THEN COUNT(*)
    ELSE NULL
  END as count
FROM fact_license_owners
WHERE CASE 
    WHEN $field = 'owner_pk' THEN CAST(owner_pk AS VARCHAR)
    WHEN $field = 'license_pk' THEN CAST(license_pk AS VARCHAR)
    WHEN $field = 'owner_gender' THEN CAST(owner_gender AS VARCHAR)
    WHEN $field = 'nationality' THEN CAST(nationality AS VARCHAR)
    WHEN $field = 'owner_type' THEN CAST(owner_type AS VARCHAR)
    WHEN $field = 'email' THEN CAST(email AS VARCHAR)
    WHEN $field = 'is_primary_owner' THEN CAST(is_primary_owner AS VARCHAR)
    WHEN $field = 'is_active' THEN CAST(is_active AS VARCHAR)
    WHEN $field = 'requires_approval' THEN CAST(requires_approval AS VARCHAR)
  END IS NOT NULL
GROUP BY value
ORDER BY count DESC NULLS LAST, value