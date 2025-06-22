-- Base query
WITH base_data AS (
SELECT *
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
  AND ($BlStatusAr IS NULL OR bl_status_ar = $BlStatusAr)
  AND ($BlNameEn IS NULL OR bl_name_en = $BlNameEn)
  AND ($BlNameAr IS NULL OR bl_name_ar = $BlNameAr)
  AND ($BlLegalTypeEn IS NULL OR bl_legal_type_en = $BlLegalTypeEn)
  AND ($BlLegalTypeAr IS NULL OR bl_legal_type_ar = $BlLegalTypeAr)
  AND ($BlEstDateFrom IS NULL OR bl_est_date_d >= $BlEstDateFrom::DATE)
  AND ($BlEstDateTo IS NULL OR bl_est_date_d <= $BlEstDateTo::DATE)
  AND ($BlExpDateFrom IS NULL OR bl_exp_date_d >= $BlExpDateFrom::DATE)
  AND ($BlExpDateTo IS NULL OR bl_exp_date_d <= $BlExpDateTo::DATE)
  AND ($BlTypeEn IS NULL OR bl_type_en = $BlTypeEn)
  AND ($BlTypeAr IS NULL OR bl_type_ar = $BlTypeAr)
  AND ($LicenseBranchFlag IS NULL OR license_branch_flag = $LicenseBranchFlag)
  AND ($BlFullAddress IS NULL OR bl_full_address ILIKE '%' || $BlFullAddress || '%')
  AND ($ParentLicenceLicenseNumber IS NULL OR parent_licence_license_number ILIKE '%' || $ParentLicenceLicenseNumber || '%')
  AND ($ParentLicenseIssuanceAuthorityEn IS NULL OR parent_license_issuance_authority_en = $ParentLicenseIssuanceAuthorityEn)
  AND ($ParentLicenseIssuanceAuthorityAr IS NULL OR parent_license_issuance_authority_ar = $ParentLicenseIssuanceAuthorityAr)
  AND ($RelationshipTypeEn IS NULL OR relationship_type_en = $RelationshipTypeEn)
  AND ($RelationshipTypeAr IS NULL OR relationship_type_ar = $RelationshipTypeAr)
  AND ($OwnerNationalityAr IS NULL OR owner_nationality_ar = $OwnerNationalityAr)
  AND ($OwnerGender IS NULL OR owner_gender = $OwnerGender)
  AND ($OwnerNationalityEn IS NULL OR owner_nationality_en = $OwnerNationalityEn)
  AND ($BusinessActivityCode IS NULL OR business_activity_code ILIKE '%' || $BusinessActivityCode || '%')
  AND ($BusinessActivityDescEn IS NULL OR business_activity_desc_en = $BusinessActivityDescEn)
  AND ($BusinessActivityDescAr IS NULL OR business_activity_desc_ar = $BusinessActivityDescAr)
  AND ($LicenseLatitude IS NULL OR license_latitude = $LicenseLatitude)
  AND ($LicenseLongitude IS NULL OR license_longitude = $LicenseLongitude)
  AND ($LicenseLatitude1 IS NULL OR license_latitude_1 = $LicenseLatitude1)
  AND ($LicenseLongitude1 IS NULL OR license_longitude_1 = $LicenseLongitude1)
  AND ($BlEstDateDFrom IS NULL OR bl_est_date_d >= $BlEstDateDFrom::DATE)
  AND ($BlEstDateDTo IS NULL OR bl_est_date_d <= $BlEstDateDTo::DATE)
  AND ($BlExpDateDFrom IS NULL OR bl_exp_date_d >= $BlExpDateDFrom::DATE)
  AND ($BlExpDateDTo IS NULL OR bl_exp_date_d <= $BlExpDateDTo::DATE)
  AND ($LatDdMin IS NULL OR lat_dd >= $LatDdMin)
  AND ($LatDdMax IS NULL OR lat_dd <= $LatDdMax)
  AND ($LonDdMin IS NULL OR lon_dd >= $LonDdMin)
  AND ($LonDdMax IS NULL OR lon_dd <= $LonDdMax)
ORDER BY license_pk DESC
LIMIT $limit
OFFSET $offset
)

-- Enhanced query with conditional embedding
SELECT 
  bd.*,
  CASE 
    WHEN $embed IS NULL OR ARRAY_LENGTH($embed) = 0 THEN NULL
    ELSE JSON_OBJECT()  -- Placeholder for embedded data
  END as _embedded
FROM base_data bd