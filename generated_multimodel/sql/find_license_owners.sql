-- Base query
WITH base_data AS (
SELECT *
FROM fact_license_owners_v1
WHERE 1=1
  AND ($OwnerPk IS NULL OR owner_pk = $OwnerPk)
  AND ($LicensePk IS NULL OR license_pk = $LicensePk)
  AND ($OwnerName IS NULL OR owner_name ILIKE '%' || $OwnerName || '%')
  AND ($OwnerGender IS NULL OR owner_gender = $OwnerGender)
  AND ($Nationality IS NULL OR nationality = $Nationality)
  AND ($OwnerType IS NULL OR owner_type = $OwnerType)
  AND ($OwnershipPercentage IS NULL OR ownership_percentage ILIKE '%' || $OwnershipPercentage || '%')
  AND ($PhoneNumber IS NULL OR phone_number ILIKE '%' || $PhoneNumber || '%')
  AND ($Email IS NULL OR email = $Email)
  AND ($Emirates IS NULL OR emirates_id ILIKE '%' || $Emirates || '%')
  AND ($OwnerRegistrationDateFrom IS NULL OR owner_registration_date >= $OwnerRegistrationDateFrom::DATE)
  AND ($OwnerRegistrationDateTo IS NULL OR owner_registration_date <= $OwnerRegistrationDateTo::DATE)
  AND ($IsPrimaryOwner IS NULL OR is_primary_owner = $IsPrimaryOwner)
  AND ($IsActive IS NULL OR is_active = $IsActive)
  AND ($RequiresApproval IS NULL OR requires_approval = $RequiresApproval)
  AND ($CreatedAtFrom IS NULL OR created_at_d >= $CreatedAtFrom::DATE)
  AND ($CreatedAtTo IS NULL OR created_at_d <= $CreatedAtTo::DATE)
  AND ($CreatedByFrom IS NULL OR created_by_d >= $CreatedByFrom::DATE)
  AND ($CreatedByTo IS NULL OR created_by_d <= $CreatedByTo::DATE)
ORDER BY created_at DESC
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