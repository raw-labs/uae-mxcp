SELECT
  CASE 
    WHEN $groupByField = 'bl_full_address' THEN bl_full_address
    ELSE bl_full_address
  END as location,
  COUNT(*) as count,
  COUNT(DISTINCT license_pk) as unique_records,
  CASE 
    WHEN $includeCoordinates THEN AVG(relationship_type_en)
    ELSE NULL
  END as avg_latitude,
  CASE 
    WHEN $includeCoordinates THEN AVG(license_longitude)
    ELSE NULL
  END as avg_longitude,
  CASE 
    WHEN $includeCoordinates THEN MIN(relationship_type_en)
    ELSE NULL
  END as min_latitude,
  CASE 
    WHEN $includeCoordinates THEN MAX(relationship_type_en)
    ELSE NULL
  END as max_latitude,
  CASE 
    WHEN $includeCoordinates THEN MIN(license_longitude)
    ELSE NULL
  END as min_longitude,
  CASE 
    WHEN $includeCoordinates THEN MAX(license_longitude)
    ELSE NULL
  END as max_longitude
FROM dim_licenses_v1
WHERE CASE 
    WHEN $groupByField = 'bl_full_address' THEN bl_full_address
    ELSE bl_full_address
  END IS NOT NULL
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
  AND ($boundingBox.minLat IS NULL OR relationship_type_en >= $boundingBox.minLat)
  AND ($boundingBox.maxLat IS NULL OR relationship_type_en <= $boundingBox.maxLat)
  AND ($boundingBox.minLon IS NULL OR license_longitude >= $boundingBox.minLon)
  AND ($boundingBox.maxLon IS NULL OR license_longitude <= $boundingBox.maxLon)
GROUP BY location
ORDER BY count DESC