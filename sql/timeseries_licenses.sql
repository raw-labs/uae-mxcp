SELECT
  DATE_TRUNC($granularity, 
    CASE 
      WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END
  ) as period,
  COUNT(*) as count,
  COUNT(DISTINCT license_pk) as unique_licenses
FROM dim_licenses_v1
WHERE CASE 
    WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
    ELSE bl_est_date_d
  END IS NOT NULL
  AND ($startDate IS NULL OR 
    CASE 
      WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END >= $startDate::DATE)
  AND ($endDate IS NULL OR 
    CASE 
      WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END <= $endDate::DATE)
  AND ($filterLicensePk IS NULL OR license_pk = $filterLicensePk)
  AND ($filterBl IS NULL OR bl = $filterBl)
  AND ($filterCbls IS NULL OR bl_cbls = $filterCbls)
  AND ($filterEmirateNameEn IS NULL OR emirate_name_en = $filterEmirateNameEn)
  AND ($filterEmirateNameAr IS NULL OR emirate_name_ar = $filterEmirateNameAr)
  AND ($filterIssuanceAuthorityEn IS NULL OR issuance_authority_en = $filterIssuanceAuthorityEn)
  AND ($filterIssuanceAuthorityAr IS NULL OR issuance_authority_ar = $filterIssuanceAuthorityAr)
  AND ($filterIssuanceAuthorityBranchEn IS NULL OR issuance_authority_branch_en = $filterIssuanceAuthorityBranchEn)
  AND ($filterIssuanceAuthorityBranchAr IS NULL OR issuance_authority_branch_ar = $filterIssuanceAuthorityBranchAr)
  AND ($filterStatusEn IS NULL OR bl_status_en = $filterStatusEn)
  AND ($EstDateFrom IS NULL OR bl_est_date_d >= $EstDateFrom::DATE)
  AND ($EstDateTo IS NULL OR bl_est_date_d <= $EstDateTo::DATE)
  AND ($ExpDateFrom IS NULL OR bl_exp_date_d >= $ExpDateFrom::DATE)
  AND ($ExpDateTo IS NULL OR bl_exp_date_d <= $ExpDateTo::DATE)
GROUP BY period
ORDER BY period DESC