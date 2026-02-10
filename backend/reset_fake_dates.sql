-- Reset fake dates to NULL so we can properly identify what needs fixing
-- This will revert the temporary fix and show us the real scope of the problem

UPDATE conflicts 
SET incidence_date = NULL 
WHERE incidence_date = '2026-02-09';

-- Show the result
SELECT 
    incidence_date IS NULL as needs_real_date,
    COUNT(*) as count 
FROM conflicts 
GROUP BY incidence_date IS NULL 
ORDER BY count DESC;
