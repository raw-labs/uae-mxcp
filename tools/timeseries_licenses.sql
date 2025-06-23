SELECT
  CAST(date_trunc(
    $interval,
    CASE
      WHEN $date_field = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $date_field = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE NULL
    END
  ) AS VARCHAR) AS period,
  CASE WHEN strpos($metrics, 'count') > 0 THEN COUNT(*) END AS count,
  CASE WHEN strpos($metrics, 'distinct_count') > 0 THEN COUNT(DISTINCT license_pk) END AS distinct_count
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
  -- add more filters as needed from search_licenses.sql
GROUP BY period
ORDER BY period
LIMIT $page_size OFFSET (($page - 1) * $page_size); 