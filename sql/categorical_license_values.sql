SELECT 'license_branch_flag' AS field, value FROM (
  SELECT license_branch_flag AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE license_branch_flag IS NOT NULL
  GROUP BY license_branch_flag
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'license_branch_flag')
UNION ALL
SELECT 'owner_gender', value FROM (
  SELECT owner_gender AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE owner_gender IS NOT NULL
  GROUP BY owner_gender
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'owner_gender')
UNION ALL
SELECT 'bl_status_en', value FROM (
  SELECT bl_status_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE bl_status_en IS NOT NULL
  GROUP BY bl_status_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'bl_status_en')
UNION ALL
SELECT 'bl_status_ar', value FROM (
  SELECT bl_status_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE bl_status_ar IS NOT NULL
  GROUP BY bl_status_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'bl_status_ar')
UNION ALL
SELECT 'emirate_name_en', value FROM (
  SELECT emirate_name_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE emirate_name_en IS NOT NULL
  GROUP BY emirate_name_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'emirate_name_en')
UNION ALL
SELECT 'emirate_name_ar', value FROM (
  SELECT emirate_name_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE emirate_name_ar IS NOT NULL
  GROUP BY emirate_name_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'emirate_name_ar')
UNION ALL
SELECT 'issuance_authority_branch_ar', value FROM (
  SELECT issuance_authority_branch_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE issuance_authority_branch_ar IS NOT NULL
  GROUP BY issuance_authority_branch_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'issuance_authority_branch_ar')
UNION ALL
SELECT 'parent_license_issuance_authority_ar', value FROM (
  SELECT parent_license_issuance_authority_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE parent_license_issuance_authority_ar IS NOT NULL
  GROUP BY parent_license_issuance_authority_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'parent_license_issuance_authority_ar')
UNION ALL
SELECT 'parent_license_issuance_authority_en', value FROM (
  SELECT parent_license_issuance_authority_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE parent_license_issuance_authority_en IS NOT NULL
  GROUP BY parent_license_issuance_authority_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'parent_license_issuance_authority_en')
UNION ALL
SELECT 'relationship_type_en', value FROM (
  SELECT relationship_type_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE relationship_type_en IS NOT NULL
  GROUP BY relationship_type_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'relationship_type_en')
UNION ALL
SELECT 'relationship_type_ar', value FROM (
  SELECT relationship_type_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE relationship_type_ar IS NOT NULL
  GROUP BY relationship_type_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'relationship_type_ar')
UNION ALL
SELECT 'bl_type_en', value FROM (
  SELECT bl_type_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE bl_type_en IS NOT NULL
  GROUP BY bl_type_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'bl_type_en')
UNION ALL
SELECT 'bl_type_ar', value FROM (
  SELECT bl_type_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE bl_type_ar IS NOT NULL
  GROUP BY bl_type_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'bl_type_ar')
UNION ALL
SELECT 'bl_legal_type_en', value FROM (
  SELECT bl_legal_type_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE bl_legal_type_en IS NOT NULL
  GROUP BY bl_legal_type_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'bl_legal_type_en')
UNION ALL
SELECT 'bl_legal_type_ar', value FROM (
  SELECT bl_legal_type_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE bl_legal_type_ar IS NOT NULL
  GROUP BY bl_legal_type_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'bl_legal_type_ar')
UNION ALL
SELECT 'owner_nationality_en', value FROM (
  SELECT owner_nationality_en AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE owner_nationality_en IS NOT NULL
  GROUP BY owner_nationality_en
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'owner_nationality_en')
UNION ALL
SELECT 'owner_nationality_ar', value FROM (
  SELECT owner_nationality_ar AS value, COUNT(*) AS freq
  FROM dim_licenses
  WHERE owner_nationality_ar IS NOT NULL
  GROUP BY owner_nationality_ar
  ORDER BY freq DESC
  LIMIT 500
)
WHERE ($field IS NULL OR $field = 'owner_nationality_ar'); 