-- This custom test checks for values in relationship_type_en that are not in the expected list.
-- It will return rows for any value that is not in the hardcoded list, causing the test to fail.

WITH all_values AS (
    SELECT DISTINCT relationship_type_en FROM {{ ref('dim_licenses') }}
)
SELECT av.relationship_type_en
FROM all_values av
LEFT JOIN (
    VALUES
        ('Authorized signatory'),
        ('Chairman of the Board of Directors'),
        ('Cheif Executive'),
        ('Designated Member'),
        ('Designated Member'),
        ('Doctor'),
        ('Founder'),
        ('Leased-Rented'),
        ('Manager'),
        ('Owner'),
        ('Partner'),
        ('Pharmacist'),
        ('Representative of the Board'),
        ('Representative of the Successors '),
        ('Secretary'),
        ('Service Agent'),
        ('Shareholders of the Company'),
        ('Successors'),
        ('The Board of Directors, Member and CEO/Executive Director')
) AS expected_values (val) ON av.relationship_type_en = expected_values.val
WHERE expected_values.val IS NULL 