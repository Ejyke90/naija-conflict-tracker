-- Fix missing incidence_date values by using created_at as fallback
-- This addresses the data quality issue where 4243 out of 4297 records had NULL dates

UPDATE conflicts 
SET incidence_date = created_at::date 
WHERE incidence_date IS NULL AND created_at::date IS NOT NULL;

-- Verify the fix
SELECT 
    incidence_date IS NULL as has_null_date,
    COUNT(*) as count 
FROM conflicts 
GROUP BY incidence_date IS NULL 
ORDER BY count DESC;
