SELECT
  license_pk,
  emirate_name_en,
  emirate_name_ar,
  issuance_authority_en,
  issuance_authority_ar,
  issuance_authority_branch_en,
  issuance_authority_branch_ar,
  bl,
  bl_cbls,
  bl_name_ar,
  bl_name_en,
  bl_est_date,
  bl_exp_date,
  bl_status_en,
  bl_status_ar,
  bl_legal_type_en,
  bl_legal_type_ar,
  bl_type_en,
  bl_type_ar,
  bl_full_address,
  license_latitude,
  license_longitude,
  license_branch_flag,
  parent_licence_license_number,
  parent_license_issuance_authority_en,
  parent_license_issuance_authority_ar,
  relationship_type_en,
  relationship_type_ar,
  owner_nationality_en,
  owner_nationality_ar,
  owner_gender,
  business_activity_code,
  business_activity_desc_en,
  business_activity_desc_ar,
  license_latitude_1,
  license_longitude_1,
  CAST(bl_est_date_d AS VARCHAR) AS bl_est_date_d,
  CAST(bl_exp_date_d AS VARCHAR) AS bl_exp_date_d,
  NULLIF(lat_dd, 'nan') AS lat_dd,
  NULLIF(lon_dd, 'nan') AS lon_dd
FROM dim_licenses_v1
WHERE 1=1
  AND ($emirate_name_en IS NULL OR emirate_name_en = $emirate_name_en)
  AND ($emirate_name_en_like IS NULL OR emirate_name_en ILIKE '%' || $emirate_name_en_like || '%')
  AND ($emirate_name_ar IS NULL OR emirate_name_ar = $emirate_name_ar)
  AND ($emirate_name_ar_like IS NULL OR emirate_name_ar ILIKE '%' || $emirate_name_ar_like || '%')
  AND ($issuance_authority_en IS NULL OR issuance_authority_en = $issuance_authority_en)
  AND ($issuance_authority_en_like IS NULL OR issuance_authority_en ILIKE '%' || $issuance_authority_en_like || '%')
  AND ($issuance_authority_ar IS NULL OR issuance_authority_ar = $issuance_authority_ar)
  AND ($issuance_authority_ar_like IS NULL OR issuance_authority_ar ILIKE '%' || $issuance_authority_ar_like || '%')
  AND ($bl IS NULL OR bl = $bl)
  AND ($bl_like IS NULL OR bl ILIKE '%' || $bl_like || '%')
  AND ($bl_status_en IS NULL OR bl_status_en = $bl_status_en)
  AND ($bl_type_en IS NULL OR bl_type_en = $bl_type_en)
  AND ($bl_legal_type_en IS NULL OR bl_legal_type_en = $bl_legal_type_en)
  AND ($owner_nationality_en IS NULL OR owner_nationality_en = $owner_nationality_en)
  AND ($relationship_type_en IS NULL OR relationship_type_en = $relationship_type_en)
  AND ($bl_est_date_d_from IS NULL OR bl_est_date_d >= $bl_est_date_d_from)
  AND ($bl_est_date_d_to IS NULL OR bl_est_date_d <= $bl_est_date_d_to)
  AND ($bl_exp_date_d_from IS NULL OR bl_exp_date_d >= $bl_exp_date_d_from)
  AND ($bl_exp_date_d_to IS NULL OR bl_exp_date_d <= $bl_exp_date_d_to)
  AND (
    $bbox IS NULL OR (
      lat_dd IS NOT NULL AND lon_dd IS NOT NULL AND
      lon_dd >= split_part($bbox, ',', 1)::DOUBLE AND
      lat_dd >= split_part($bbox, ',', 2)::DOUBLE AND
      lon_dd <= split_part($bbox, ',', 3)::DOUBLE AND
      lat_dd <= split_part($bbox, ',', 4)::DOUBLE
    )
  )
ORDER BY bl_est_date_d DESC
LIMIT $page_size OFFSET (($page - 1) * $page_size); 