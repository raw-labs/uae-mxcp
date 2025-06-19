{{ config(materialized='view') }}

{%- if not var('licenses_file', none) -%}
    {{ exceptions.raise_compiler_error("Please provide the licenses_file path using --vars '{\"licenses_file\": \"/path/to/your/licenses.csv\"}'") }}
{%- endif -%}

SELECT *
FROM read_csv_auto(
       '{{ var("licenses_file") }}',
       delim='|',
       header=true,
       normalize_names=true,
       all_varchar=true
     )
