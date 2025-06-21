SELECT
  CASE 
    WHEN $groupByField = 'emirate_name_en' THEN emirate_name_en
    WHEN $groupByField = 'emirate_name_ar' THEN emirate_name_ar
    WHEN $groupByField = 'issuance_authority_en' THEN issuance_authority_en
    WHEN $groupByField = 'issuance_authority_ar' THEN issuance_authority_ar
    WHEN $groupByField = 'bl_full_address' THEN bl_full_address
    ELSE emirate_name_en
  END as location,
  COUNT(*) as count,
  COUNT(DISTINCT license_pk) as unique_licenses,
  CASE 
    WHEN $includeCoordinates THEN AVG(lat_dd)
    ELSE NULL
  END as avg_latitude,
  CASE 
    WHEN $includeCoordinates THEN AVG(lon_dd)
    ELSE NULL
  END as avg_longitude,
  CASE 
    WHEN $includeCoordinates THEN MIN(lat_dd)
    ELSE NULL
  END as min_latitude,
  CASE 
    WHEN $includeCoordinates THEN MAX(lat_dd)
    ELSE NULL
  END as max_latitude,
  CASE 
    WHEN $includeCoordinates THEN MIN(lon_dd)
    ELSE NULL
  END as min_longitude,
  CASE 
    WHEN $includeCoordinates THEN MAX(lon_dd)
    ELSE NULL
  END as max_longitude
FROM dim_licenses_v1
WHERE CASE 
    WHEN $groupByField = 'emirate_name_en' THEN emirate_name_en
    WHEN $groupByField = 'emirate_name_ar' THEN emirate_name_ar
    WHEN $groupByField = 'issuance_authority_en' THEN issuance_authority_en
    WHEN $groupByField = 'issuance_authority_ar' THEN issuance_authority_ar
    WHEN $groupByField = 'bl_full_address' THEN bl_full_address
    ELSE emirate_name_en
  END IS NOT NULL
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
  AND ($boundingBox.minLat IS NULL OR lat_dd >= $boundingBox.minLat)
  AND ($boundingBox.maxLat IS NULL OR lat_dd <= $boundingBox.maxLat)
  AND ($boundingBox.minLon IS NULL OR lon_dd >= $boundingBox.minLon)
  AND ($boundingBox.maxLon IS NULL OR lon_dd <= $boundingBox.maxLon)
GROUP BY location
ORDER BY count DESC