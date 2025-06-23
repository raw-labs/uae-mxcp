-- Optimized aggregate query with performance safeguards
WITH base_data AS (
  SELECT *
  FROM fact_license_owners
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
  AND ($OwnerPk IS NULL OR owner_pk = $OwnerPk)
  AND ($LicensePk IS NULL OR license_pk = $LicensePk)
  AND ($OwnerName IS NULL OR owner_name = $OwnerName)
  AND ($PhoneNumber IS NULL OR phone_number = $PhoneNumber)
  AND ($Emirates IS NULL OR emirates_id = $Emirates)
  AND ($OwnerRegistrationDateFrom IS NULL OR owner_registration_date >= $OwnerRegistrationDateFrom::DATE)
  AND ($OwnerRegistrationDateTo IS NULL OR owner_registration_date <= $OwnerRegistrationDateTo::DATE)
  AND ($CreatedAtFrom IS NULL OR created_at >= $CreatedAtFrom::DATE)
  AND ($CreatedAtTo IS NULL OR created_at <= $CreatedAtTo::DATE)
  -- Performance safeguard: limit large scans
  LIMIT CASE 
    WHEN $OwnerPk IS NOT NULL OR $LicensePk IS NOT NULL OR $OwnerName IS NOT NULL OR $OwnerGender IS NOT NULL OR $Nationality IS NOT NULL 
    THEN 1000000  -- Allow larger scans when filtered
    ELSE 50000    -- Limit unfiltered scans to 50K records
  END
)
SELECT
  -- Dynamic grouping based on group_by array
  CASE WHEN 'OwnerPk' = ANY($group_by) THEN owner_pk ELSE 'All' END as owner_pk,
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN 'OwnerGender' = ANY($group_by) THEN owner_gender ELSE 'All' END as owner_gender,
  CASE WHEN 'Nationality' = ANY($group_by) THEN nationality ELSE 'All' END as nationality,
  CASE WHEN 'OwnerType' = ANY($group_by) THEN owner_type ELSE 'All' END as owner_type,
  CASE WHEN 'Email' = ANY($group_by) THEN email ELSE 'All' END as email,
  CASE WHEN 'IsPrimaryOwner' = ANY($group_by) THEN is_primary_owner ELSE 'All' END as is_primary_owner,
  CASE WHEN 'IsActive' = ANY($group_by) THEN is_active ELSE 'All' END as is_active,
  CASE WHEN 'RequiresApproval' = ANY($group_by) THEN requires_approval ELSE 'All' END as requires_approval,
  CASE WHEN 'OwnerPk' = ANY($group_by) THEN owner_pk ELSE 'All' END as owner_pk,
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END as license_pk,
  CASE WHEN 'OwnerName' = ANY($group_by) THEN owner_name ELSE 'All' END as owner_name,
  CASE WHEN 'PhoneNumber' = ANY($group_by) THEN phone_number ELSE 'All' END as phone_number,
  CASE WHEN 'Emirates' = ANY($group_by) THEN emirates_id ELSE 'All' END as emirates_id,
  CASE WHEN 'CreatedBy' = ANY($group_by) THEN created_by ELSE 'All' END as created_by,
  
  -- Aggregation metrics
  COUNT(*) as total_count,
  COUNT(DISTINCT owner_pk) as unique_records,
  
  -- Metadata with performance info
  JSON_OBJECT(
    'grouped_by', $group_by,
    'filter_applied', JSON_OBJECT(
      'owner_pk', $OwnerPk,
      'license_pk', $LicensePk,
      'owner_gender', $OwnerGender,
      'date_range', CASE 
        WHEN $OwnerRegistrationDateFrom IS NOT NULL OR $OwnerRegistrationDateTo IS NOT NULL 
        THEN JSON_OBJECT('from', $OwnerRegistrationDateFrom, 'to', $OwnerRegistrationDateTo)
        ELSE NULL 
      END
    ),
    'performance_note', CASE 
      WHEN $OwnerPk IS NULL AND $LicensePk IS NULL AND $OwnerName IS NULL AND $OwnerGender IS NULL AND $Nationality IS NULL
      THEN 'Limited to 50K records for performance. Add filters for complete results.'
      ELSE 'Full dataset scan performed.'
    END
  ) as _metadata

FROM base_data
GROUP BY 
  CASE WHEN 'OwnerPk' = ANY($group_by) THEN owner_pk ELSE 'All' END,
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END,
  CASE WHEN 'OwnerGender' = ANY($group_by) THEN owner_gender ELSE 'All' END,
  CASE WHEN 'Nationality' = ANY($group_by) THEN nationality ELSE 'All' END,
  CASE WHEN 'OwnerType' = ANY($group_by) THEN owner_type ELSE 'All' END,
  CASE WHEN 'Email' = ANY($group_by) THEN email ELSE 'All' END,
  CASE WHEN 'IsPrimaryOwner' = ANY($group_by) THEN is_primary_owner ELSE 'All' END,
  CASE WHEN 'IsActive' = ANY($group_by) THEN is_active ELSE 'All' END,
  CASE WHEN 'RequiresApproval' = ANY($group_by) THEN requires_approval ELSE 'All' END,
  CASE WHEN 'OwnerPk' = ANY($group_by) THEN owner_pk ELSE 'All' END,
  CASE WHEN 'LicensePk' = ANY($group_by) THEN license_pk ELSE 'All' END,
  CASE WHEN 'OwnerName' = ANY($group_by) THEN owner_name ELSE 'All' END,
  CASE WHEN 'PhoneNumber' = ANY($group_by) THEN phone_number ELSE 'All' END,
  CASE WHEN 'Emirates' = ANY($group_by) THEN emirates_id ELSE 'All' END,
  CASE WHEN 'CreatedBy' = ANY($group_by) THEN created_by ELSE 'All' END

ORDER BY total_count DESC
LIMIT 100