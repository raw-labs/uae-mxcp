SELECT DISTINCT
  CASE 
    WHEN $field = 'license_pk' THEN license_pk
    WHEN $field = 'bl' THEN bl
    WHEN $field = 'bl_cbls' THEN bl_cbls
    WHEN $field = 'emirate_name_en' THEN emirate_name_en
    WHEN $field = 'emirate_name_ar' THEN emirate_name_ar
    WHEN $field = 'issuance_authority_en' THEN issuance_authority_en
    WHEN $field = 'issuance_authority_ar' THEN issuance_authority_ar
    WHEN $field = 'issuance_authority_branch_en' THEN issuance_authority_branch_en
    WHEN $field = 'issuance_authority_branch_ar' THEN issuance_authority_branch_ar
    WHEN $field = 'bl_status_en' THEN bl_status_en
    WHEN $field = 'bl_status_ar' THEN bl_status_ar
    WHEN $field = 'bl_name_en' THEN bl_name_en
    WHEN $field = 'bl_name_ar' THEN bl_name_ar
    WHEN $field = 'bl_legal_type_en' THEN bl_legal_type_en
    WHEN $field = 'bl_legal_type_ar' THEN bl_legal_type_ar
    WHEN $field = 'bl_type_en' THEN bl_type_en
    WHEN $field = 'bl_type_ar' THEN bl_type_ar
    WHEN $field = 'license_branch_flag' THEN license_branch_flag
    WHEN $field = 'parent_license_issuance_authority_en' THEN parent_license_issuance_authority_en
    WHEN $field = 'parent_license_issuance_authority_ar' THEN parent_license_issuance_authority_ar
    WHEN $field = 'relationship_type_en' THEN relationship_type_en
    WHEN $field = 'relationship_type_ar' THEN relationship_type_ar
    WHEN $field = 'owner_nationality_ar' THEN owner_nationality_ar
    WHEN $field = 'owner_gender' THEN owner_gender
    WHEN $field = 'owner_nationality_en' THEN owner_nationality_en
    WHEN $field = 'business_activity_desc_en' THEN business_activity_desc_en
    WHEN $field = 'business_activity_desc_ar' THEN business_activity_desc_ar
    WHEN $field = 'license_latitude' THEN license_latitude
    WHEN $field = 'license_longitude' THEN license_longitude
    WHEN $field = 'license_latitude_1' THEN license_latitude_1
    WHEN $field = 'license_longitude_1' THEN license_longitude_1
  END as value,
  CASE 
    WHEN $includeCount THEN COUNT(*)
    ELSE NULL
  END as count
FROM dim_licenses_v1
WHERE CASE 
    WHEN $field = 'license_pk' THEN license_pk
    WHEN $field = 'bl' THEN bl
    WHEN $field = 'bl_cbls' THEN bl_cbls
    WHEN $field = 'emirate_name_en' THEN emirate_name_en
    WHEN $field = 'emirate_name_ar' THEN emirate_name_ar
    WHEN $field = 'issuance_authority_en' THEN issuance_authority_en
    WHEN $field = 'issuance_authority_ar' THEN issuance_authority_ar
    WHEN $field = 'issuance_authority_branch_en' THEN issuance_authority_branch_en
    WHEN $field = 'issuance_authority_branch_ar' THEN issuance_authority_branch_ar
    WHEN $field = 'bl_status_en' THEN bl_status_en
    WHEN $field = 'bl_status_ar' THEN bl_status_ar
    WHEN $field = 'bl_name_en' THEN bl_name_en
    WHEN $field = 'bl_name_ar' THEN bl_name_ar
    WHEN $field = 'bl_legal_type_en' THEN bl_legal_type_en
    WHEN $field = 'bl_legal_type_ar' THEN bl_legal_type_ar
    WHEN $field = 'bl_type_en' THEN bl_type_en
    WHEN $field = 'bl_type_ar' THEN bl_type_ar
    WHEN $field = 'license_branch_flag' THEN license_branch_flag
    WHEN $field = 'parent_license_issuance_authority_en' THEN parent_license_issuance_authority_en
    WHEN $field = 'parent_license_issuance_authority_ar' THEN parent_license_issuance_authority_ar
    WHEN $field = 'relationship_type_en' THEN relationship_type_en
    WHEN $field = 'relationship_type_ar' THEN relationship_type_ar
    WHEN $field = 'owner_nationality_ar' THEN owner_nationality_ar
    WHEN $field = 'owner_gender' THEN owner_gender
    WHEN $field = 'owner_nationality_en' THEN owner_nationality_en
    WHEN $field = 'business_activity_desc_en' THEN business_activity_desc_en
    WHEN $field = 'business_activity_desc_ar' THEN business_activity_desc_ar
    WHEN $field = 'license_latitude' THEN license_latitude
    WHEN $field = 'license_longitude' THEN license_longitude
    WHEN $field = 'license_latitude_1' THEN license_latitude_1
    WHEN $field = 'license_longitude_1' THEN license_longitude_1
  END IS NOT NULL
GROUP BY value
ORDER BY count DESC NULLS LAST, value