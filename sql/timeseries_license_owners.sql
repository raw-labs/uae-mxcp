SELECT
  DATE_TRUNC($granularity, 
    CASE 
    WHEN $timeField = 'owner_registration_date' THEN owner_registration_date
    WHEN $timeField = 'created_at' THEN created_at
    WHEN $timeField = 'created_by' THEN created_by
      ELSE owner_registration_date
    END
  ) as period,
  COUNT(*) as count,
  COUNT(DISTINCT owner_pk) as unique_records
FROM fact_license_owners_v1
WHERE CASE 
    WHEN $timeField = 'owner_registration_date' THEN owner_registration_date
    WHEN $timeField = 'created_at' THEN created_at
    WHEN $timeField = 'created_by' THEN created_by
      ELSE owner_registration_date
  END IS NOT NULL
  AND ($startDate IS NULL OR 
    CASE 
    WHEN $timeField = 'owner_registration_date' THEN owner_registration_date
    WHEN $timeField = 'created_at' THEN created_at
    WHEN $timeField = 'created_by' THEN created_by
      ELSE owner_registration_date
    END >= $startDate::DATE)
  AND ($endDate IS NULL OR 
    CASE 
    WHEN $timeField = 'owner_registration_date' THEN owner_registration_date
    WHEN $timeField = 'created_at' THEN created_at
    WHEN $timeField = 'created_by' THEN created_by
      ELSE owner_registration_date
    END <= $endDate::DATE)
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
GROUP BY period
ORDER BY period DESC