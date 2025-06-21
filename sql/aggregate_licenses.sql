SELECT
  CASE WHEN $groupByLicensePk THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN $groupByBl THEN bl ELSE 'All' END as bl,
  CASE WHEN $groupByCbls THEN bl_cbls ELSE 'All' END as bl_cbls,
  CASE WHEN $groupByEmirateNameEn THEN emirate_name_en ELSE 'All' END as emirate_name_en,
  CASE WHEN $groupByEmirateNameAr THEN emirate_name_ar ELSE 'All' END as emirate_name_ar,
  CASE WHEN $groupByIssuanceAuthorityEn THEN issuance_authority_en ELSE 'All' END as issuance_authority_en,
  CASE WHEN $groupByIssuanceAuthorityAr THEN issuance_authority_ar ELSE 'All' END as issuance_authority_ar,
  CASE WHEN $groupByIssuanceAuthorityBranchEn THEN issuance_authority_branch_en ELSE 'All' END as issuance_authority_branch_en,
  CASE WHEN $groupByIssuanceAuthorityBranchAr THEN issuance_authority_branch_ar ELSE 'All' END as issuance_authority_branch_ar,
  CASE WHEN $groupByStatusEn THEN bl_status_en ELSE 'All' END as bl_status_en,
  CASE WHEN $groupByStatusAr THEN bl_status_ar ELSE 'All' END as bl_status_ar,
  CASE WHEN $groupByNameEn THEN bl_name_en ELSE 'All' END as bl_name_en,
  CASE WHEN $groupByNameAr THEN bl_name_ar ELSE 'All' END as bl_name_ar,
  CASE WHEN $groupByLegalTypeEn THEN bl_legal_type_en ELSE 'All' END as bl_legal_type_en,
  CASE WHEN $groupByLegalTypeAr THEN bl_legal_type_ar ELSE 'All' END as bl_legal_type_ar,
  CASE WHEN $groupByTypeEn THEN bl_type_en ELSE 'All' END as bl_type_en,
  CASE WHEN $groupByTypeAr THEN bl_type_ar ELSE 'All' END as bl_type_ar,
  CASE WHEN $groupByLicenseBranchFlag THEN license_branch_flag ELSE 'All' END as license_branch_flag,
  CASE WHEN $groupByParentLicenseIssuanceAuthorityEn THEN parent_license_issuance_authority_en ELSE 'All' END as parent_license_issuance_authority_en,
  CASE WHEN $groupByParentLicenseIssuanceAuthorityAr THEN parent_license_issuance_authority_ar ELSE 'All' END as parent_license_issuance_authority_ar,
  CASE WHEN $groupByRelationshipTypeEn THEN relationship_type_en ELSE 'All' END as relationship_type_en,
  CASE WHEN $groupByRelationshipTypeAr THEN relationship_type_ar ELSE 'All' END as relationship_type_ar,
  CASE WHEN $groupByOwnerNationalityAr THEN owner_nationality_ar ELSE 'All' END as owner_nationality_ar,
  CASE WHEN $groupByOwnerGender THEN owner_gender ELSE 'All' END as owner_gender,
  CASE WHEN $groupByOwnerNationalityEn THEN owner_nationality_en ELSE 'All' END as owner_nationality_en,
  CASE WHEN $groupByBusinessActivityDescEn THEN business_activity_desc_en ELSE 'All' END as business_activity_desc_en,
  CASE WHEN $groupByBusinessActivityDescAr THEN business_activity_desc_ar ELSE 'All' END as business_activity_desc_ar,
  CASE WHEN $groupByLicenseLatitude THEN license_latitude ELSE 'All' END as license_latitude,
  CASE WHEN $groupByLicenseLongitude THEN license_longitude ELSE 'All' END as license_longitude,
  CASE WHEN $groupByLicenseLatitude1 THEN license_latitude_1 ELSE 'All' END as license_latitude_1,
  CASE WHEN $groupByLicenseLongitude1 THEN license_longitude_1 ELSE 'All' END as license_longitude_1,
  CASE WHEN $groupByEstDate THEN bl_est_date ELSE 'All' END as bl_est_date,
  CASE WHEN $groupByExpDate THEN bl_exp_date ELSE 'All' END as bl_exp_date,
  CASE WHEN $groupByFullAddress THEN bl_full_address ELSE 'All' END as bl_full_address,
  CASE WHEN $groupByParentLicenceLicenseNumber THEN parent_licence_license_number ELSE 'All' END as parent_licence_license_number,
  CASE WHEN $groupByBusinessActivityCode THEN business_activity_code ELSE 'All' END as business_activity_code,
  COUNT(*) as total_count,
  COUNT(DISTINCT license_pk) as unique_licenses
FROM dim_licenses_v1
WHERE 1=1
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
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36
ORDER BY total_count DESC
LIMIT 100