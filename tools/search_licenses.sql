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
  AND ($issuance_authority_branch_en IS NULL OR issuance_authority_branch_en = $issuance_authority_branch_en)
  AND ($issuance_authority_branch_en_like IS NULL OR issuance_authority_branch_en ILIKE '%' || $issuance_authority_branch_en_like || '%')
  AND ($issuance_authority_branch_ar IS NULL OR issuance_authority_branch_ar = $issuance_authority_branch_ar)
  AND ($issuance_authority_branch_ar_like IS NULL OR issuance_authority_branch_ar ILIKE '%' || $issuance_authority_branch_ar_like || '%')
  AND ($bl_num IS NULL OR bl = $bl_num)
  AND ($bl_num_like IS NULL OR bl ILIKE '%' || $bl_num_like || '%')
  AND ($bl_cbls_num IS NULL OR bl_cbls = $bl_cbls_num)
  AND ($bl_cbls_num_like IS NULL OR bl_cbls ILIKE '%' || $bl_cbls_num_like || '%')
  AND ($bl_name_ar IS NULL OR bl_name_ar = $bl_name_ar)
  AND ($bl_name_ar_like IS NULL OR bl_name_ar ILIKE '%' || $bl_name_ar_like || '%')
  AND ($bl_name_en IS NULL OR bl_name_en = $bl_name_en)
  AND ($bl_name_en_like IS NULL OR bl_name_en ILIKE '%' || $bl_name_en_like || '%')
  AND ($bl_est_date_from IS NULL OR bl_est_date_d >= $bl_est_date_from::DATE)
  AND ($bl_est_date_to IS NULL OR bl_est_date_d <= $bl_est_date_to::DATE)
  AND ($bl_exp_date_from IS NULL OR bl_exp_date_d >= $bl_exp_date_from::DATE)
  AND ($bl_exp_date_to IS NULL OR bl_exp_date_d <= $bl_exp_date_to::DATE)
  AND ($bl_status_en IS NULL OR bl_status_en = $bl_status_en)
  AND ($bl_status_en_like IS NULL OR bl_status_en ILIKE '%' || $bl_status_en_like || '%')
  AND ($bl_status_ar IS NULL OR bl_status_ar = $bl_status_ar)
  AND ($bl_status_ar_like IS NULL OR bl_status_ar ILIKE '%' || $bl_status_ar_like || '%')
  AND ($bl_legal_type_en IS NULL OR bl_legal_type_en = $bl_legal_type_en)
  AND ($bl_legal_type_en_like IS NULL OR bl_legal_type_en ILIKE '%' || $bl_legal_type_en_like || '%')
  AND ($bl_legal_type_ar IS NULL OR bl_legal_type_ar = $bl_legal_type_ar)
  AND ($bl_legal_type_ar_like IS NULL OR bl_legal_type_ar ILIKE '%' || $bl_legal_type_ar_like || '%')
  AND ($bl_type_en IS NULL OR bl_type_en = $bl_type_en)
  AND ($bl_type_en_like IS NULL OR bl_type_en ILIKE '%' || $bl_type_en_like || '%')
  AND ($bl_type_ar IS NULL OR bl_type_ar = $bl_type_ar)
  AND ($bl_type_ar_like IS NULL OR bl_type_ar ILIKE '%' || $bl_type_ar_like || '%')
  AND ($bl_full_address IS NULL OR bl_full_address = $bl_full_address)
  AND ($bl_full_address_like IS NULL OR bl_full_address ILIKE '%' || $bl_full_address_like || '%')
  AND ($license_latitude_min IS NULL OR lat_dd >= $license_latitude_min)
  AND ($license_latitude_max IS NULL OR lat_dd <= $license_latitude_max)
  AND ($license_longitude_min IS NULL OR lon_dd >= $license_longitude_min)
  AND ($license_longitude_max IS NULL OR lon_dd <= $license_longitude_max)
  AND ($license_branch_flag IS NULL OR license_branch_flag = $license_branch_flag)
  AND ($parent_licence_license_number IS NULL OR parent_licence_license_number = $parent_licence_license_number)
  AND ($parent_licence_license_number_like IS NULL OR parent_licence_license_number ILIKE '%' || $parent_licence_license_number_like || '%')
  AND ($parent_license_issuance_authority_en IS NULL OR parent_license_issuance_authority_en = $parent_license_issuance_authority_en)
  AND ($parent_license_issuance_authority_en_like IS NULL OR parent_license_issuance_authority_en ILIKE '%' || $parent_license_issuance_authority_en_like || '%')
  AND ($parent_license_issuance_authority_ar IS NULL OR parent_license_issuance_authority_ar = $parent_license_issuance_authority_ar)
  AND ($parent_license_issuance_authority_ar_like IS NULL OR parent_license_issuance_authority_ar ILIKE '%' || $parent_license_issuance_authority_ar_like || '%')
  AND ($relationship_type_en IS NULL OR relationship_type_en = $relationship_type_en)
  AND ($relationship_type_en_like IS NULL OR relationship_type_en ILIKE '%' || $relationship_type_en_like || '%')
  AND ($relationship_type_ar IS NULL OR relationship_type_ar = $relationship_type_ar)
  AND ($relationship_type_ar_like IS NULL OR relationship_type_ar ILIKE '%' || $relationship_type_ar_like || '%')
  AND ($owner_nationality_en IS NULL OR owner_nationality_en = $owner_nationality_en)
  AND ($owner_nationality_en_like IS NULL OR owner_nationality_en ILIKE '%' || $owner_nationality_en_like || '%')
  AND ($owner_nationality_ar IS NULL OR owner_nationality_ar = $owner_nationality_ar)
  AND ($owner_nationality_ar_like IS NULL OR owner_nationality_ar ILIKE '%' || $owner_nationality_ar_like || '%')
  AND ($owner_gender IS NULL OR owner_gender = $owner_gender)
  AND ($business_activity_code IS NULL OR business_activity_code = $business_activity_code)
  AND ($business_activity_code_like IS NULL OR business_activity_code ILIKE '%' || $business_activity_code_like || '%')
  AND ($business_activity_desc_en IS NULL OR business_activity_desc_en = $business_activity_desc_en)
  AND ($business_activity_desc_en_like IS NULL OR business_activity_desc_en ILIKE '%' || $business_activity_desc_en_like || '%')
  AND ($business_activity_desc_ar IS NULL OR business_activity_desc_ar = $business_activity_desc_ar)
  AND ($business_activity_desc_ar_like IS NULL OR business_activity_desc_ar ILIKE '%' || $business_activity_desc_ar_like || '%')
ORDER BY bl_est_date_d DESC
LIMIT $page_size OFFSET (($page - 1) * $page_size); 