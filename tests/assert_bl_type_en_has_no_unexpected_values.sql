-- This custom test checks for values in bl_type_en that are not in the expected list.
-- It will return rows for any value that is not in the hardcoded list, causing the test to fail.

WITH all_values AS (
    SELECT DISTINCT bl_type_en FROM {{ ref('dim_licenses', version='1') }}
)
SELECT av.bl_type_en
FROM all_values av
LEFT JOIN (
    VALUES
        ('Agrecultural & Animals'),
        ('Business Invest License'),
        ('Commercial'),
        ('E''dmad  (Reliance)'),
        ('E-Commerce License'),
        ('Educational License'),
        ('Event   License'),
        ('Handicraft'),
        ('Industrial'),
        ('International Business Companies'),
        ('Media License'),
        ('Preliminary License'),
        ('Professional'),
        ('Service'),
        ('Service License'),
        ('Standard'),
        ('Trade'),
        ('tourism license')
) AS expected_values (val) ON av.bl_type_en = expected_values.val
WHERE expected_values.val IS NULL 