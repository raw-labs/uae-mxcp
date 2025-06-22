SELECT
  CASE WHEN $groupByLicensePk THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN $groupByBl THEN bl ELSE 'All' END as bl,
  CASE WHEN $groupByBlCbls THEN bl_cbls ELSE 'All' END as bl_cbls,
  CASE WHEN $groupByEmirateNameEn THEN emirate_name_en ELSE 'All' END as emirate_name_en,
  CASE WHEN $groupByEmirateNameAr THEN emirate_name_ar ELSE 'All' END as emirate_name_ar,
  CASE WHEN $groupByIssuanceAuthorityEn THEN issuance_authority_en ELSE 'All' END as issuance_authority_en,
  CASE WHEN $groupByIssuanceAuthorityAr THEN issuance_authority_ar ELSE 'All' END as issuance_authority_ar,
  CASE WHEN $groupByIssuanceAuthorityBranchEn THEN issuance_authority_branch_en ELSE 'All' END as issuance_authority_branch_en,
  CASE WHEN $groupByIssuanceAuthorityBranchAr THEN issuance_authority_branch_ar ELSE 'All' END as issuance_authority_branch_ar,
  CASE WHEN $groupByBlStatusEn THEN bl_status_en ELSE 'All' END as bl_status_en,
  CASE WHEN $groupByBlStatusAr THEN bl_status_ar ELSE 'All' END as bl_status_ar,
  CASE WHEN $groupByBlNameEn THEN bl_name_en ELSE 'All' END as bl_name_en,
  CASE WHEN $groupByBlNameAr THEN bl_name_ar ELSE 'All' END as bl_name_ar,
  CASE WHEN $groupByBlLegalTypeEn THEN bl_legal_type_en ELSE 'All' END as bl_legal_type_en,
  CASE WHEN $groupByBlLegalTypeAr THEN bl_legal_type_ar ELSE 'All' END as bl_legal_type_ar,
  CASE WHEN $groupByBlTypeEn THEN bl_type_en ELSE 'All' END as bl_type_en,
  CASE WHEN $groupByBlTypeAr THEN bl_type_ar ELSE 'All' END as bl_type_ar,
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
  CASE WHEN $groupByBlEstDate THEN bl_est_date ELSE 'All' END as bl_est_date,
  CASE WHEN $groupByBlExpDate THEN bl_exp_date ELSE 'All' END as bl_exp_date,
  CASE WHEN $groupByBlFullAddress THEN bl_full_address ELSE 'All' END as bl_full_address,
  CASE WHEN $groupByParentLicenceLicenseNumber THEN parent_licence_license_number ELSE 'All' END as parent_licence_license_number,
  CASE WHEN $groupByBusinessActivityCode THEN business_activity_code ELSE 'All' END as business_activity_code,
  COUNT(*) as total_count,
  COUNT(DISTINCT license_pk) as unique_records
FROM dim_licenses_v1
WHERE 1=1
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
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36
ORDER BY total_count DESC
LIMIT 100