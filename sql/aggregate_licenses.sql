-- Optimized aggregate query with performance safeguards
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
  AND ($BlEstDateDFrom IS NULL OR bl_est_date_d >= $BlEstDateDFrom::DATE)
  AND ($BlEstDateDTo IS NULL OR bl_est_date_d <= $BlEstDateDTo::DATE)
  AND ($BlExpDateDFrom IS NULL OR bl_exp_date_d >= $BlExpDateDFrom::DATE)
  AND ($BlExpDateDTo IS NULL OR bl_exp_date_d <= $BlExpDateDTo::DATE)
  -- Performance safeguard: limit large scans
  LIMIT CASE 
    WHEN $LicensePk IS NOT NULL OR $Bl IS NOT NULL OR $BlCbls IS NOT NULL OR $EmirateNameEn IS NOT NULL OR $EmirateNameAr IS NOT NULL 
    THEN 1000000  -- Allow larger scans when filtered
    ELSE 50000    -- Limit unfiltered scans to 50K records
  END
)
SELECT
  -- Dynamic grouping based on group_by array
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN 'Bl' = ANY($group_by) THEN bl ELSE 'All' END as bl,
  CASE WHEN 'BlCbls' = ANY($group_by) THEN bl_cbls ELSE 'All' END as bl_cbls,
  CASE WHEN 'EmirateNameEn' = ANY($group_by) THEN emirate_name_en ELSE 'All' END as emirate_name_en,
  CASE WHEN 'EmirateNameAr' = ANY($group_by) THEN emirate_name_ar ELSE 'All' END as emirate_name_ar,
  CASE WHEN 'IssuanceAuthorityEn' = ANY($group_by) THEN issuance_authority_en ELSE 'All' END as issuance_authority_en,
  CASE WHEN 'IssuanceAuthorityAr' = ANY($group_by) THEN issuance_authority_ar ELSE 'All' END as issuance_authority_ar,
  CASE WHEN 'IssuanceAuthorityBranchEn' = ANY($group_by) THEN issuance_authority_branch_en ELSE 'All' END as issuance_authority_branch_en,
  CASE WHEN 'IssuanceAuthorityBranchAr' = ANY($group_by) THEN issuance_authority_branch_ar ELSE 'All' END as issuance_authority_branch_ar,
  CASE WHEN 'BlStatusEn' = ANY($group_by) THEN bl_status_en ELSE 'All' END as bl_status_en,
  CASE WHEN 'BlStatusAr' = ANY($group_by) THEN bl_status_ar ELSE 'All' END as bl_status_ar,
  CASE WHEN 'BlNameEn' = ANY($group_by) THEN bl_name_en ELSE 'All' END as bl_name_en,
  CASE WHEN 'BlNameAr' = ANY($group_by) THEN bl_name_ar ELSE 'All' END as bl_name_ar,
  CASE WHEN 'BlLegalTypeEn' = ANY($group_by) THEN bl_legal_type_en ELSE 'All' END as bl_legal_type_en,
  CASE WHEN 'BlLegalTypeAr' = ANY($group_by) THEN bl_legal_type_ar ELSE 'All' END as bl_legal_type_ar,
  CASE WHEN 'BlTypeEn' = ANY($group_by) THEN bl_type_en ELSE 'All' END as bl_type_en,
  CASE WHEN 'BlTypeAr' = ANY($group_by) THEN bl_type_ar ELSE 'All' END as bl_type_ar,
  CASE WHEN 'LicenseBranchFlag' = ANY($group_by) THEN license_branch_flag ELSE 'All' END as license_branch_flag,
  CASE WHEN 'ParentLicenseIssuanceAuthorityEn' = ANY($group_by) THEN parent_license_issuance_authority_en ELSE 'All' END as parent_license_issuance_authority_en,
  CASE WHEN 'ParentLicenseIssuanceAuthorityAr' = ANY($group_by) THEN parent_license_issuance_authority_ar ELSE 'All' END as parent_license_issuance_authority_ar,
  CASE WHEN 'RelationshipTypeEn' = ANY($group_by) THEN relationship_type_en ELSE 'All' END as relationship_type_en,
  CASE WHEN 'RelationshipTypeAr' = ANY($group_by) THEN relationship_type_ar ELSE 'All' END as relationship_type_ar,
  CASE WHEN 'OwnerNationalityAr' = ANY($group_by) THEN owner_nationality_ar ELSE 'All' END as owner_nationality_ar,
  CASE WHEN 'OwnerGender' = ANY($group_by) THEN owner_gender ELSE 'All' END as owner_gender,
  CASE WHEN 'OwnerNationalityEn' = ANY($group_by) THEN owner_nationality_en ELSE 'All' END as owner_nationality_en,
  CASE WHEN 'BusinessActivityDescEn' = ANY($group_by) THEN business_activity_desc_en ELSE 'All' END as business_activity_desc_en,
  CASE WHEN 'BusinessActivityDescAr' = ANY($group_by) THEN business_activity_desc_ar ELSE 'All' END as business_activity_desc_ar,
  CASE WHEN 'LicenseLatitude' = ANY($group_by) THEN license_latitude ELSE 'All' END as license_latitude,
  CASE WHEN 'LicenseLongitude' = ANY($group_by) THEN license_longitude ELSE 'All' END as license_longitude,
  CASE WHEN 'LicenseLatitude1' = ANY($group_by) THEN license_latitude_1 ELSE 'All' END as license_latitude_1,
  CASE WHEN 'LicenseLongitude1' = ANY($group_by) THEN license_longitude_1 ELSE 'All' END as license_longitude_1,
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN 'EmirateNameEn' = ANY($group_by) THEN emirate_name_en ELSE 'All' END as emirate_name_en,
  CASE WHEN 'EmirateNameAr' = ANY($group_by) THEN emirate_name_ar ELSE 'All' END as emirate_name_ar,
  CASE WHEN 'BlNameEn' = ANY($group_by) THEN bl_name_en ELSE 'All' END as bl_name_en,
  CASE WHEN 'BlNameAr' = ANY($group_by) THEN bl_name_ar ELSE 'All' END as bl_name_ar,
  CASE WHEN 'ParentLicenceLicenseNumber' = ANY($group_by) THEN parent_licence_license_number ELSE 'All' END as parent_licence_license_number,
  CASE WHEN 'BusinessActivityCode' = ANY($group_by) THEN business_activity_code ELSE 'All' END as business_activity_code,
  CASE WHEN 'BlEstDate' = ANY($group_by) THEN bl_est_date ELSE 'All' END as bl_est_date,
  CASE WHEN 'BlExpDate' = ANY($group_by) THEN bl_exp_date ELSE 'All' END as bl_exp_date,
  CASE WHEN 'BlFullAddress' = ANY($group_by) THEN bl_full_address ELSE 'All' END as bl_full_address,
  
  -- Aggregation metrics
  COUNT(*) as total_count,
  COUNT(DISTINCT license_pk) as unique_records,
  
  -- Metadata with performance info
  JSON_OBJECT(
    'grouped_by', $group_by,
    'filter_applied', JSON_OBJECT(
      'license_pk', $LicensePk,
      'bl', $Bl,
      'bl_cbls', $BlCbls,
      'date_range', CASE 
        WHEN $BlEstDateFrom IS NOT NULL OR $BlEstDateTo IS NOT NULL 
        THEN JSON_OBJECT('from', $BlEstDateFrom, 'to', $BlEstDateTo)
        ELSE NULL 
      END
    ),
    'performance_note', CASE 
      WHEN $LicensePk IS NULL AND $Bl IS NULL AND $BlCbls IS NULL AND $EmirateNameEn IS NULL AND $EmirateNameAr IS NULL
      THEN 'Limited to 50K records for performance. Add filters for complete results.'
      ELSE 'Full dataset scan performed.'
    END
  ) as _metadata

FROM base_data
GROUP BY 
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END,
  CASE WHEN 'Bl' = ANY($group_by) THEN bl ELSE 'All' END,
  CASE WHEN 'BlCbls' = ANY($group_by) THEN bl_cbls ELSE 'All' END,
  CASE WHEN 'EmirateNameEn' = ANY($group_by) THEN emirate_name_en ELSE 'All' END,
  CASE WHEN 'EmirateNameAr' = ANY($group_by) THEN emirate_name_ar ELSE 'All' END,
  CASE WHEN 'IssuanceAuthorityEn' = ANY($group_by) THEN issuance_authority_en ELSE 'All' END,
  CASE WHEN 'IssuanceAuthorityAr' = ANY($group_by) THEN issuance_authority_ar ELSE 'All' END,
  CASE WHEN 'IssuanceAuthorityBranchEn' = ANY($group_by) THEN issuance_authority_branch_en ELSE 'All' END,
  CASE WHEN 'IssuanceAuthorityBranchAr' = ANY($group_by) THEN issuance_authority_branch_ar ELSE 'All' END,
  CASE WHEN 'BlStatusEn' = ANY($group_by) THEN bl_status_en ELSE 'All' END,
  CASE WHEN 'BlStatusAr' = ANY($group_by) THEN bl_status_ar ELSE 'All' END,
  CASE WHEN 'BlNameEn' = ANY($group_by) THEN bl_name_en ELSE 'All' END,
  CASE WHEN 'BlNameAr' = ANY($group_by) THEN bl_name_ar ELSE 'All' END,
  CASE WHEN 'BlLegalTypeEn' = ANY($group_by) THEN bl_legal_type_en ELSE 'All' END,
  CASE WHEN 'BlLegalTypeAr' = ANY($group_by) THEN bl_legal_type_ar ELSE 'All' END,
  CASE WHEN 'BlTypeEn' = ANY($group_by) THEN bl_type_en ELSE 'All' END,
  CASE WHEN 'BlTypeAr' = ANY($group_by) THEN bl_type_ar ELSE 'All' END,
  CASE WHEN 'LicenseBranchFlag' = ANY($group_by) THEN license_branch_flag ELSE 'All' END,
  CASE WHEN 'ParentLicenseIssuanceAuthorityEn' = ANY($group_by) THEN parent_license_issuance_authority_en ELSE 'All' END,
  CASE WHEN 'ParentLicenseIssuanceAuthorityAr' = ANY($group_by) THEN parent_license_issuance_authority_ar ELSE 'All' END,
  CASE WHEN 'RelationshipTypeEn' = ANY($group_by) THEN relationship_type_en ELSE 'All' END,
  CASE WHEN 'RelationshipTypeAr' = ANY($group_by) THEN relationship_type_ar ELSE 'All' END,
  CASE WHEN 'OwnerNationalityAr' = ANY($group_by) THEN owner_nationality_ar ELSE 'All' END,
  CASE WHEN 'OwnerGender' = ANY($group_by) THEN owner_gender ELSE 'All' END,
  CASE WHEN 'OwnerNationalityEn' = ANY($group_by) THEN owner_nationality_en ELSE 'All' END,
  CASE WHEN 'BusinessActivityDescEn' = ANY($group_by) THEN business_activity_desc_en ELSE 'All' END,
  CASE WHEN 'BusinessActivityDescAr' = ANY($group_by) THEN business_activity_desc_ar ELSE 'All' END,
  CASE WHEN 'LicenseLatitude' = ANY($group_by) THEN license_latitude ELSE 'All' END,
  CASE WHEN 'LicenseLongitude' = ANY($group_by) THEN license_longitude ELSE 'All' END,
  CASE WHEN 'LicenseLatitude1' = ANY($group_by) THEN license_latitude_1 ELSE 'All' END,
  CASE WHEN 'LicenseLongitude1' = ANY($group_by) THEN license_longitude_1 ELSE 'All' END,
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END,
  CASE WHEN 'EmirateNameEn' = ANY($group_by) THEN emirate_name_en ELSE 'All' END,
  CASE WHEN 'EmirateNameAr' = ANY($group_by) THEN emirate_name_ar ELSE 'All' END,
  CASE WHEN 'BlNameEn' = ANY($group_by) THEN bl_name_en ELSE 'All' END,
  CASE WHEN 'BlNameAr' = ANY($group_by) THEN bl_name_ar ELSE 'All' END,
  CASE WHEN 'ParentLicenceLicenseNumber' = ANY($group_by) THEN parent_licence_license_number ELSE 'All' END,
  CASE WHEN 'BusinessActivityCode' = ANY($group_by) THEN business_activity_code ELSE 'All' END,
  CASE WHEN 'BlEstDate' = ANY($group_by) THEN bl_est_date ELSE 'All' END,
  CASE WHEN 'BlExpDate' = ANY($group_by) THEN bl_exp_date ELSE 'All' END,
  CASE WHEN 'BlFullAddress' = ANY($group_by) THEN bl_full_address ELSE 'All' END

ORDER BY total_count DESC
LIMIT 100