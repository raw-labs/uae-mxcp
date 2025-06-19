{{ config(materialized='view') }}

SELECT *
FROM read_csv_auto(
       '/opt/projects/raw/projects/uae-mxcp/seeds/licenses.csv',
       delim='|',
       header=true,
       normalize_names=true,
       all_varchar=true
     )
