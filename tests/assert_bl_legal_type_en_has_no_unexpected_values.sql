-- This custom test checks for values in bl_legal_type_en that are not in the expected list.
-- It will return rows for any value that is not in the hardcoded list, causing the test to fail.

WITH all_values AS (
    SELECT DISTINCT bl_legal_type_en FROM {{ ref('dim_licenses') }}
)
SELECT av.bl_legal_type_en
FROM all_values av
LEFT JOIN (
    VALUES
        ('Civil Company'),
        ('Free Zone Establishment'),
        ('LLC'),
        ('Sole Establishment')
) AS expected_values (val) ON av.bl_legal_type_en = expected_values.val
WHERE expected_values.val IS NULL 