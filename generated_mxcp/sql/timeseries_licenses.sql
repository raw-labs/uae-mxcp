SELECT
  DATE_TRUNC($granularity, 
    CASE 
    WHEN $timeField = 'bl_est_date' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date' THEN bl_exp_date_d
    WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END
  ) as period,
  COUNT(*) as count,
  COUNT(DISTINCT license_pk) as unique_records
FROM dim_licenses_v1
WHERE CASE 
    WHEN $timeField = 'bl_est_date' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date' THEN bl_exp_date_d
    WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
  END IS NOT NULL
  AND ($startDate IS NULL OR 
    CASE 
    WHEN $timeField = 'bl_est_date' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date' THEN bl_exp_date_d
    WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END >= $startDate::DATE)
  AND ($endDate IS NULL OR 
    CASE 
    WHEN $timeField = 'bl_est_date' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date' THEN bl_exp_date_d
    WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END <= $endDate::DATE)
  AND ($LicensePk IS NULL OR license_pk = $LicensePk)
  AND ($Bl IS NULL OR bl = $Bl)
  AND ($BlCbls IS NULL OR bl_cbls = $BlCbls)
  AND ($EmirateNameEn IS NULL OR emirate_name_en = $EmirateNameEn)
  AND ($EmirateNameAr IS NULL OR emirate_name_ar = $EmirateNameAr)
  AND ($IssuanceAuthorityEn IS NULL OR issuance_authority_en = $IssuanceAuthorityEn)
  AND ($IssuanceAuthorityAr IS NULL OR issuance_authority_ar = $IssuanceAuthorityAr)
  AND ($IssuanceAuthorityBranchEn IS NULL OR issuance_authority_branch_en = $IssuanceAuthorityBranchEn)
  AND ($IssuanceAuthorityBranchAr IS NULL OR issuance_authority_branch_ar = $IssuanceAuthorityBranchAr)
  AND ($BlStatusEn IS NULL OR bl_status_en = $BlStatusEn)
  AND ($BlEstDateDFrom IS NULL OR bl_est_date_d >= $BlEstDateDFrom::DATE)
  AND ($BlEstDateDTo IS NULL OR bl_est_date_d <= $BlEstDateDTo::DATE)
  AND ($BlExpDateDFrom IS NULL OR bl_exp_date_d >= $BlExpDateDFrom::DATE)
  AND ($BlExpDateDTo IS NULL OR bl_exp_date_d <= $BlExpDateDTo::DATE)
GROUP BY period
ORDER BY period DESC