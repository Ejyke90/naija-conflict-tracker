-- Demo heatmap data for Nextier Conflict Tracker
-- Inserts 11 conflicts across 4 regions of Nigeria with varying fatalities
-- to demonstrate green/orange/red intensity bands in the heatmap

INSERT INTO conflict_events 
(event_date, year, month, event_type, event_category, conflict_type, 
 state, lga, location, latitude, longitude, actor1, actor2, actor1_type, actor2_type,
 fatalities, injuries, properties_destroyed, displaced_persons, source, notes, verified, confidence_level)
VALUES
-- Kaduna - High Intensity (Red) 
('2026-01-25'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Kaduna', 'Chikun', 'Chikun LGA violence', 9.1267, 7.3486, 'Armed Group', 'Civilians',
 'Rebel Group', 'Civilians', 52, 104, 0, 520, 'Demo Data', 'Highest fatality incident for demo', true, 'High'),

('2026-01-22'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Kaduna', 'Kaduna South', 'Kaduna town incident', 9.0267, 7.4486, 'Armed Group', 'State Forces',
 'Rebel Group', 'Military', 38, 76, 0, 380, 'Demo Data', 'High fatality rural clash', true, 'High'),

('2026-01-18'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Kaduna', 'Kaduna Rural', 'Kaduna rural clash', 8.9267, 7.3486, 'Community Groups', 'Community Groups',
 'Militia', 'Militia', 45, 90, 0, 450, 'Demo Data', 'High fatality community violence', true, 'High'),

('2026-01-15'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Kaduna', 'Igabi', 'Igabi community attack', 9.2267, 7.4486, 'Armed Group', 'Civilians',
 'Rebel Group', 'Civilians', 28, 56, 0, 280, 'Demo Data', 'Medium-high fatality incident', true, 'High'),

-- Maiduguri/Borno - Medium-High Intensity (Orange-Red)
('2026-01-27'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Borno', 'Maiduguri', 'Maiduguri fringe battle', 12.9567, 2.0967, 'Insurgent Group', 'State Forces',
 'Armed Group', 'Military', 35, 70, 0, 350, 'Demo Data', 'High intensity battle', true, 'High'),

('2026-01-23'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Borno', 'Borno Rural', 'Borno rural clash', 13.0967, 2.2367, 'Community Groups', 'Community Groups',
 'Militia', 'Militia', 20, 40, 0, 200, 'Demo Data', 'Medium intensity clash', true, 'High'),

('2026-01-20'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
 'Borno', 'Jere', 'Jere community violence', 13.2367, 2.0967, 'Community Groups', 'Civilians',
 'Militia', 'Civilians', 18, 36, 0, 180, 'Demo Data', 'Medium intensity violence', true, 'Medium'),

-- Port Harcourt/Rivers - Low-Medium Intensity (Green-Orange)
('2026-01-26'::date, 2026, 1, 'Crime/Piracy', 'Criminal Violence', 'Piracy/Robbery',
 'Rivers', 'Port Harcourt', 'Rivers piracy incident', 4.6157, 6.9422, 'Criminal Gang', 'Civilians',
 'Gang', 'Civilians', 12, 24, 0, 120, 'Demo Data', 'Low intensity incident', true, 'Medium'),

('2026-01-21'::date, 2026, 1, 'Crime/Gang', 'Criminal Violence', 'Gang Violence',
 'Rivers', 'Port Harcourt', 'Port Harcourt gang clash', 4.7357, 7.0622, 'Criminal Gang', 'Criminal Gang',
 'Gang', 'Gang', 8, 16, 0, 80, 'Demo Data', 'Very low intensity gang clash', true, 'Medium'),

-- Lagos/Southwest - Low Intensity (Green)
('2026-01-24'::date, 2026, 1, 'Community Dispute', 'Communal Conflict', 'Land/Border Dispute',
 'Lagos', 'Ibeju-Lekki', 'Lagos border dispute', 6.3744, 3.3292, 'Community A', 'Community B',
 'Civilians', 'Civilians', 5, 10, 0, 50, 'Demo Data', 'Very low fatality dispute', true, 'Medium'),

('2026-01-19'::date, 2026, 1, 'Community Dispute', 'Communal Conflict', 'Land/Border Dispute',
 'Oyo', 'Ibarapa', 'Oyo community clash', 6.4744, 3.4292, 'Community A', 'Community B',
 'Civilians', 'Civilians', 3, 6, 0, 30, 'Demo Data', 'Minimal fatality clash', true, 'Low');

-- Verification
SELECT COUNT(*) as "Total Demo Conflicts Inserted" FROM conflict_events 
WHERE source = 'Demo Data';

SELECT 
  location, 
  latitude, 
  longitude, 
  fatalities,
  CASE 
    WHEN fatalities >= 35 THEN '🔴 High Intensity (Red)'
    WHEN fatalities >= 18 THEN '🟠 Medium Intensity (Orange)'
    ELSE '🟢 Low Intensity (Green)'
  END as "Heatmap Color"
FROM conflict_events
WHERE source = 'Demo Data'
ORDER BY fatalities DESC;
