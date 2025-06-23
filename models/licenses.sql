-- Simple model that reads from the licenses seed file
-- This is the minimal setup for embedded SQL tools demo

SELECT *
FROM read_csv_auto('{{ var("licenses_file", "seeds/licenses_sample.csv") }}')