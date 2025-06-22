SELECT
  CASE WHEN $groupByOwnerPk THEN owner_pk ELSE 'All' END as owner_pk,
  CASE WHEN $groupByLicensePk THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN $groupByOwnerGender THEN owner_gender ELSE 'All' END as owner_gender,
  CASE WHEN $groupByNationality THEN nationality ELSE 'All' END as nationality,
  CASE WHEN $groupByOwnerType THEN owner_type ELSE 'All' END as owner_type,
  CASE WHEN $groupByEmail THEN email ELSE 'All' END as email,
  CASE WHEN $groupByIsPrimaryOwner THEN is_primary_owner ELSE 'All' END as is_primary_owner,
  CASE WHEN $groupByIsActive THEN is_active ELSE 'All' END as is_active,
  CASE WHEN $groupByRequiresApproval THEN requires_approval ELSE 'All' END as requires_approval,
  CASE WHEN $groupByPhoneNumber THEN phone_number ELSE 'All' END as phone_number,
  CASE WHEN $groupByEmirates THEN emirates_id ELSE 'All' END as emirates_id,
  CASE WHEN $groupByCreatedBy THEN created_by ELSE 'All' END as created_by,
  COUNT(*) as total_count,
  COUNT(DISTINCT owner_pk) as unique_records
FROM fact_license_owners_v1
WHERE 1=1
  AND ($OwnerPk IS NULL OR owner_pk = $OwnerPk)
  AND ($LicensePk IS NULL OR license_pk = $LicensePk)
  AND ($OwnerGender IS NULL OR owner_gender = $OwnerGender)
  AND ($Nationality IS NULL OR nationality = $Nationality)
  AND ($OwnerType IS NULL OR owner_type = $OwnerType)
  AND ($Email IS NULL OR email = $Email)
  AND ($IsPrimaryOwner IS NULL OR is_primary_owner = $IsPrimaryOwner)
  AND ($IsActive IS NULL OR is_active = $IsActive)
  AND ($RequiresApproval IS NULL OR requires_approval = $RequiresApproval)
  AND ($OwnerRegistrationDateFrom IS NULL OR owner_registration_date >= $OwnerRegistrationDateFrom::DATE)
  AND ($OwnerRegistrationDateTo IS NULL OR owner_registration_date <= $OwnerRegistrationDateTo::DATE)
  AND ($CreatedAtFrom IS NULL OR created_at >= $CreatedAtFrom::DATE)
  AND ($CreatedAtTo IS NULL OR created_at <= $CreatedAtTo::DATE)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
ORDER BY total_count DESC
LIMIT 100