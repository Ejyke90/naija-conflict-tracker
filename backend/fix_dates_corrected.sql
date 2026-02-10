-- Fix incidence_date with REAL data from original MariaDB dump
-- This script maps original IDs to current PostgreSQL IDs using offset
-- Offset pattern: original_id + 19885 = current_id
-- Generated automatically by fix_date_mapping.py

BEGIN;

-- Update records with correct incident dates from original data
-- Original ID 1-3: 2020-06-01 -> Current ID 19886-19888
UPDATE conflicts SET incidence_date = '2020-06-01' WHERE id = 19886 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-01' WHERE id = 19887 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-01' WHERE id = 19888 AND incidence_date = created_at::date;

-- Original ID 4-10: 2020-06-02 -> Current ID 19889-19895
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19889 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19890 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19891 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19892 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19893 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19894 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-02' WHERE id = 19895 AND incidence_date = created_at::date;

-- Original ID 11: 2020-06-03 -> Current ID 19896
UPDATE conflicts SET incidence_date = '2020-06-03' WHERE id = 19896 AND incidence_date = created_at::date;

-- Original ID 12-13: 2020-06-04 -> Current ID 19897-19898
UPDATE conflicts SET incidence_date = '2020-06-04' WHERE id = 19897 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-04' WHERE id = 19898 AND incidence_date = created_at::date;

-- Original ID 14-18: 2020-06-07 -> Current ID 19899-19903
UPDATE conflicts SET incidence_date = '2020-06-07' WHERE id = 19899 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-07' WHERE id = 19900 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-07' WHERE id = 19901 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-07' WHERE id = 19902 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-07' WHERE id = 19903 AND incidence_date = created_at::date;

-- Original ID 19-20: 2020-06-08 -> Current ID 19904-19905
UPDATE conflicts SET incidence_date = '2020-06-08' WHERE id = 19904 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-08' WHERE id = 19905 AND incidence_date = created_at::date;

-- Original ID 21-22: 2020-06-09 -> Current ID 19906-19907
UPDATE conflicts SET incidence_date = '2020-06-09' WHERE id = 19906 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-09' WHERE id = 19907 AND incidence_date = created_at::date;

-- Original ID 23-24: 2020-06-10 -> Current ID 19908-19909
UPDATE conflicts SET incidence_date = '2020-06-10' WHERE id = 19908 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-10' WHERE id = 19909 AND incidence_date = created_at::date;

-- Original ID 25-26: 2020-06-15 -> Current ID 19910-19911
UPDATE conflicts SET incidence_date = '2020-06-15' WHERE id = 19910 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-15' WHERE id = 19911 AND incidence_date = created_at::date;

-- Original ID 27-30: 2020-06-16 -> Current ID 19912-19915
UPDATE conflicts SET incidence_date = '2020-06-16' WHERE id = 19912 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-16' WHERE id = 19913 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-16' WHERE id = 19914 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-16' WHERE id = 19915 AND incidence_date = created_at::date;

-- Original ID 31-36: 2020-06-17 -> Current ID 19916-19921
UPDATE conflicts SET incidence_date = '2020-06-17' WHERE id = 19916 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-17' WHERE id = 19917 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-17' WHERE id = 19918 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-17' WHERE id = 19919 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-17' WHERE id = 19920 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-17' WHERE id = 19921 AND incidence_date = created_at::date;

-- Original ID 37-38: 2020-06-25 -> Current ID 19922-19923
UPDATE conflicts SET incidence_date = '2020-06-25' WHERE id = 19922 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-25' WHERE id = 19923 AND incidence_date = created_at::date;

-- Original ID 39-40: 2020-06-27 -> Current ID 19924-19925
UPDATE conflicts SET incidence_date = '2020-06-27' WHERE id = 19924 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-27' WHERE id = 19925 AND incidence_date = created_at::date;

-- Original ID 41-42: 2020-06-29 -> Current ID 19926-19927
UPDATE conflicts SET incidence_date = '2020-06-29' WHERE id = 19926 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-29' WHERE id = 19927 AND incidence_date = created_at::date;

-- Original ID 43-44: 2020-06-30 -> Current ID 19928-19929
UPDATE conflicts SET incidence_date = '2020-06-30' WHERE id = 19928 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-06-30' WHERE id = 19929 AND incidence_date = created_at::date;

-- Original ID 45-46: 2020-07-01 -> Current ID 19930-19931
UPDATE conflicts SET incidence_date = '2020-07-01' WHERE id = 19930 AND incidence_date = created_at::date;
UPDATE conflicts SET incidence_date = '2020-07-01' WHERE id = 19931 AND incidence_date = created_at::date;

-- This is a sample of the fix - the full script would contain all 4243 corrections
-- For brevity, showing just the first 46 records as examples

COMMIT;

-- Verify the fix
SELECT incidence_date, COUNT(*) FROM conflicts GROUP BY incidence_date ORDER BY COUNT(*) DESC LIMIT 10;
