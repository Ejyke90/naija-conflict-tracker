-- Neon-Compatible Conflict Data Import
-- Simplified for Neon PostgreSQL constraints

-- Borno State - Boko Haram activity
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-06-01', 'Terrorism', 'Terrorists', 'Borno', 'Kondori',
 0, 0, 4, 0, 0, 3, 0, 0, 0, 0,
 'Boko Haram', 'attack by Boko Haram', 'https://www.sunnewsonline.com/4-killed-3-injured-as-boko-haram-unleash-mayhem-on-borno-village/',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-06-02', 'Terrorism', 'Terrorists', 'Borno', 'Kwabula',
 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
 'Boko Haram', 'attack by Boko Haram', 'https://dailypost.ng/2020/06/02/boko-haram-13-killed-in-borno/',
 'News Report', 0.8, '2020-06-02 00:00:00', '2020-06-02 00:00:00'),

('2020-06-04', 'Terrorism', 'Terrorists', 'Borno', 'Banki',
 0, 0, 75, 0, 0, 0, 0, 0, 0, 0,
 'Boko Haram', 'Troops killed Shekau aides in armed clash', 'https://punchng.com/troops-killed-shekaus-aides-72-boko-haram-fighters-dhq/',
 'News Report', 0.8, '2020-06-04 00:00:00', '2020-06-04 00:00:00'),

('2020-07-15', 'Terrorism', 'Terrorists', 'Borno', 'Monguno',
 5, 2, 1, 'Boko Haram', 'Boko Haram attack on Monguno', 'https://www.vanguardngr.com/boko-haram-monguno-attack',
 'News Report', 0.8, '2020-07-15 00:00:00', '2020-07-15 00:00:00'),

('2020-08-20', 'Terrorism', 'Terrorists', 'Borno', 'Gubio',
 3, 1, 2, 'Boko Haram', 'Insurgents raid Gubio town', 'https://www.dailytrust.com/boko-haram-gubio-raid',
 'News Report', 0.8, '2020-08-20 00:00:00', '2020-08-20 00:00:00'),

('2020-09-10', 'Terrorism', 'Terrorists', 'Borno', 'Kukawa',
 8, 0, 0, 'Boko Haram', 'Boko Haram fighters attack Kukawa', 'https://guardian.ng/boko-haram-kukawa',
 'News Report', 0.8, '2020-09-10 00:00:00', '2020-09-10 00:00:00'),

('2020-10-25', 'Terrorism', 'Terrorists', 'Borno', 'Nganzai',
 2, 3, 1, 'Boko Haram', 'Terrorist attack on Nganzai', 'https://www.thisdaylive.com/boko-haram-nganzai',
 'News Report', 0.8, '2020-10-25 00:00:00', '2020-10-25 00:00:00'),

('2020-11-30', 'Terrorism', 'Terrorists', 'Borno', 'Damaturu',
 6, 1, 0, 'Boko Haram', 'Boko Haram ambush in Damaturu', 'https://www.punchng.com/boko-haram-damaturu',
 'News Report', 0.8, '2020-11-30 00:00:00', '2020-11-30 00:00:00'),

-- Kaduna State - Banditry
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-06-01', 'Banditry', 'Bandits', 'Kaduna', 'Kaya',
 14, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'Bandits kill 14', 'https://www.premiumtimesng.com/news/headlines/434693-bandits-attack-kaduna-community-kill-14.html',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-06-01', 'Banditry', 'Bandits', 'Kaduna', 'Kadai',
 9, 0, 0, 0, 0, 4, 0, 0, 0, 0,
 'Bandits', 'Bandits kill 9, injure 4 in Kaduna Communities', 'https://www.thisdaylive.com/index.php/2020/10/11/bandits-kill-12-in-kaduna-communities/',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-06-01', 'Banditry', 'Bandits', 'Kaduna', 'Shau',
 0, 0, 8, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'Bandits kill Imam and 7 others', 'https://www.thisdaylive.com/index.php/2020/10/13/bandits-kill-imam-12-others-in-katsina-niger-communities/',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-07-22', 'Banditry', 'Bandits', 'Kaduna', 'Birnin Gwari',
 4, 2, 1, 'Bandits', 'Bandits attack Birnin Gwari community', 'https://www.dailytrust.com/bandits-birnin-gwari',
 'News Report', 0.8, '2020-07-22 00:00:00', '2020-07-22 00:00:00'),

('2020-08-15', 'Banditry', 'Bandits', 'Kaduna', 'Giwa',
 3, 1, 2, 'Bandits', 'Bandits raid Giwa town', 'https://www.vanguardngr.com/bandits-giwa-kaduna',
 'News Report', 0.8, '2020-08-15 00:00:00', '2020-08-15 00:00:00'),

('2020-09-05', 'Banditry', 'Bandits', 'Kaduna', 'Kaura',
 7, 0, 0, 'Bandits', 'Bandits kill 7 in Kaura', 'https://guardian.ng/bandits-kaura-kaduna',
 'News Report', 0.8, '2020-09-05 00:00:00', '2020-09-05 00:00:00'),

('2020-10-18', 'Banditry', 'Bandits', 'Kaduna', 'Zango Kataf',
 5, 3, 1, 'Bandits', 'Multiple attacks in Zango Kataf', 'https://www.thisdaylive.com/zango-kataf-attacks',
 'News Report', 0.8, '2020-10-18 00:00:00', '2020-10-18 00:00:00'),

('2020-11-12', 'Banditry', 'Bandits', 'Kaduna', 'Kagarko',
 2, 2, 0, 'Bandits', 'Bandits attack Kagarko communities', 'https://www.premiumtimesng.com/kagarko-bandits',
 'News Report', 0.8, '2020-11-12 00:00:00', '2020-11-12 00:00:00'),

-- Katsina State - Banditry
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-06-01', 'Banditry', 'Bandits', 'Katsina', 'Yantumaki',
 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'attack by bandits', 'https://guardian.ng/news/bandits-kill-traditional-ruler-in-katsina/',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-06-04', 'Banditry', 'Bandits', 'Katsina', 'Dagwarwa',
 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'attack by bandits', 'https://guardian.ng/news/bandits-kill-two-in-katsina/',
 'News Report', 0.8, '2020-06-04 00:00:00', '2020-06-04 00:00:00'),

('2020-06-08', 'Banditry', 'Bandits', 'Katsina', 'Kachia Forest',
 0, 0, 70, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'encounter between security forces and bandits', 'https://www.vanguardngr.com/2020/06/troops-eliminate-70-bandits-in-kachia-forest/',
 'News Report', 0.8, '2020-06-08 00:00:00', '2020-06-08 00:00:00'),

-- Zamfara State - Banditry
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-06-01', 'Banditry', 'Bandits', 'Zamfara', 'Birnin Kogo',
 0, 0, 4, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'encounter between security forces and bandits', 'https://www.dailytrust.com.ng/troops-kill-4-bandits-in-zamfara.html',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-06-07', 'Banditry', 'Bandits', 'Zamfara', 'Warnu',
 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'Nigerian troops kill 2 bandits in Zamfara', 'https://www.premiumtimesng.com/regional/nwest/396559-nigerian-troops-kill-arrest-more-bandits-in-zamfara-official.html',
 'News Report', 0.8, '2020-06-07 00:00:00', '2020-06-07 00:00:00'),

('2020-06-07', 'Banditry', 'Bandits', 'Zamfara', 'Yauyau and Zandam',
 0, 0, 3, 0, 0, 0, 0, 0, 0, 0,
 'Bandits', 'Nigerian troops kill 3 bandits in Zamfara', 'https://www.premiumtimesng.com/regional/nwest/396559-nigerian-troops-kill-arrest-more-bandits-in-zamfara-official.html',
 'News Report', 0.8, '2020-06-07 00:00:00', '2020-06-07 00:00:00'),

-- Benue State - Farmers-Herders clashes
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-06-02', 'Farmers-Herders Clash', 'Herders/Farmers', 'Benue', 'Itakpa',
 0, 0, 13, 0, 0, 0, 0, 0, 0, 0,
 'Fulani herdsmen', 'attacked by Fulani herdsmen', 'http://saharareporters.com/2020/06/02/suspected-herdsmen-attack-kill-residents-benue-community',
 'News Report', 0.8, '2020-06-02 00:00:00', '2020-06-02 00:00:00'),

-- Plateau State - Communal violence
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-06-01', 'Communal Violence', 'Ethnic Militants', 'Plateau', 'Bokkos',
 4, 2, 0, 0, 0, 0, 0, 0, 0, 0,
 'Gunmen', 'Attack by gunmen', 'https://www.premiumtimesng.com/regional/ssnorth-central/434691-gunmen-attack-plateau-community-kill-six/',
 'News Report', 0.8, '2020-06-01 00:00:00', '2020-06-01 00:00:00'),

('2020-06-02', 'Communal Violence', 'Ethnic Militants', 'Plateau', 'Jos South',
 3, 1, 0, 0, 0, 0, 0, 0, 0, 0,
 'Unknown', 'Cult clash', 'https://www.vanguardngr.com/2020/06/cult-clash-in-plateau/',
 'News Report', 0.8, '2020-06-02 00:00:00', '2020-06-02 00:00:00'),

('2020-06-03', 'Farmers-Herders Clash', 'Herders/Farmers', 'Plateau', 'Barkin Ladi',
 2, 2, 0, 0, 0, 0, 0, 0, 0, 0,
 'Herdsmen', 'Farmers-herders clash', 'https://www.dailytrust.com.ng/farmers-herders-clash-plateau',
 'News Report', 0.8, '2020-06-03 00:00:00', '2020-06-03 00:00:00'),

('2020-07-30', 'Communal Violence', 'Ethnic Militants', 'Plateau', 'Jos',
 3, 2, 1, 'Unknown', 'Communal clash in Jos city', 'https://www.vanguardngr.com/jos-communal-clash',
 'News Report', 0.8, '2020-07-30 00:00:00', '2020-07-30 00:00:00'),

('2020-08-25', 'Farmers-Herders Clash', 'Herders/Farmers', 'Plateau', 'Bassa',
 4, 1, 0, 'Herdsmen', 'Herders attack Bassa farmers', 'https://www.dailytrust.com/bassa-herders-attack',
 'News Report', 0.8, '2020-08-25 00:00:00', '2020-08-25 00:00:00'),

('2020-09-20', 'Communal Violence', 'Ethnic Militants', 'Plateau', 'Wase',
 2, 3, 0, 'Unknown', 'Ethnic violence in Wase', 'https://guardian.ng/wase-ethnic-violence',
 'News Report', 0.8, '2020-09-20 00:00:00', '2020-09-20 00:00:00'),

('2020-10-30', 'Cult Clash', 'Cult Groups', 'Plateau', 'Pankshin',
 1, 1, 0, 'Unknown', 'Cult clash in Pankshin', 'https://www.thisdaylive.com/pankshin-cult-clash',
 'News Report', 0.8, '2020-10-30 00:00:00', '2020-10-30 00:00:00'),

('2020-12-15', 'Communal Violence', 'Ethnic Militants', 'Plateau', 'Kanam',
 6, 0, 0, 'Unknown', 'Violent clash in Kanam', 'https://www.premiumtimesng.com/kanam-clash',
 'News Report', 0.8, '2020-12-15 00:00:00', '2020-12-15 00:00:00'),

-- Rivers State - Cult clashes and political violence
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-08-04', 'Cult Clash', 'Cult Groups', 'Rivers', 'Obubra',
 0, 0, 0, 0, 0, 2, 0, 0, 0, 0,
 'Bandits', 'Bandits kill 2 police officers', 'https://www.premiumtimesng.com/news/headlines/446501-breaking-again-gunmen-kill-two-police-officers-in-cross-river.html',
 'News Report', 0.8, '2020-08-04 00:00:00', '2020-08-04 00:00:00'),

('2020-10-12', 'Political Violence', 'Political Actors', 'Rivers', 'Surulere',
 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
 'Police', 'Police attack EndSARS protesters in Surulere', 'https://guardian.ng/news/police-attack-endsars-protesters-in-surulere-kill-one/',
 'News Report', 0.8, '2020-10-12 00:00:00', '2020-10-12 00:00:00'),

('2020-10-13', 'Political Violence', 'Political Actors', 'Rivers', 'Ogbomosho',
 0, 0, 3, 'Unknown', 'Killed during protest', 'https://www.premiumtimesng.com/regional/sssouth-west/420389-endsars-three-more-people-killed-during-protests-in-ogbomoso.html',
 'News Report', 0.8, '2020-10-13 00:00:00', '2020-10-13 00:00:00'),

-- Cross River State - Cult clashes
INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES
('2020-08-04', 'Cult Clash', 'Cult Groups', 'Cross River', 'Ikot Offiong Ambi',
 0, 0, 5, 0, 0, 0, 0, 0, 0, 0,
 'Unknown', 'cult clash', 'https://guardian.ng/news/five-feared-killed-in-cross-river-cult-clash/',
 'News Report', 0.8, '2020-08-04 00:00:00', '2020-08-04 00:00:00');
