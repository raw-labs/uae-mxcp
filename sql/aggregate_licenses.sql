SELECT
  -- Dynamically select group_1
  CASE
    WHEN $group_by = 'emirate_name_en' THEN emirate_name_en
    WHEN $group_by = 'bl_status_en' THEN bl_status_en
    WHEN $group_by = 'bl_type_en' THEN bl_type_en
    WHEN $group_by = 'bl_legal_type_en' THEN bl_legal_type_en
    WHEN $group_by = 'owner_nationality_en' THEN owner_nationality_en
    WHEN $group_by = 'relationship_type_en' THEN relationship_type_en
    WHEN $group_by = 'owner_gender' THEN owner_gender
    ELSE NULL
  END AS group_1,
  -- Dynamically select group_2 if present
  CASE
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'emirate_name_en' THEN emirate_name_en
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'bl_status_en' THEN bl_status_en
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'bl_type_en' THEN bl_type_en
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'bl_legal_type_en' THEN bl_legal_type_en
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'owner_nationality_en' THEN owner_nationality_en
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'relationship_type_en' THEN relationship_type_en
    WHEN strpos($group_by, ',') > 0 AND split_part($group_by, ',', 2) = 'owner_gender' THEN owner_gender
    ELSE NULL
  END AS group_2,
  CASE WHEN strpos($metrics, 'count') > 0 THEN COUNT(*) END AS count,
  CASE WHEN strpos($metrics, 'distinct_count') > 0 THEN COUNT(DISTINCT license_pk) END AS distinct_count
FROM dim_licenses
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
  AND ($owner_gender IS NULL OR owner_gender = $owner_gender)
  AND ($bl_est_date_d_from IS NULL OR bl_est_date_d >= $bl_est_date_d_from)
  AND ($bl_est_date_d_to IS NULL OR bl_est_date_d <= $bl_est_date_d_to)
  AND ($bl_exp_date_d_from IS NULL OR bl_exp_date_d >= $bl_exp_date_d_from)
  AND ($bl_exp_date_d_to IS NULL OR bl_exp_date_d <= $bl_exp_date_d_to)
GROUP BY group_1, group_2
ORDER BY count DESC
LIMIT $page_size OFFSET (($page - 1) * $page_size); 