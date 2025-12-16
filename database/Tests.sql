use cloudsecmonitor;
-- TEST 1 : Procédure creer_incident
CALL creer_incident(1, 1, 'SSH Failed', 'Test', 'critique');
SELECT * FROM incidents ORDER BY id_incident DESC LIMIT 1;

-- TEST 2 : Trigger notification automatique
-- (Vérifier qu'une notification est créée)
SELECT * FROM notifications ORDER BY id_notification DESC LIMIT 1;

-- TEST 3 : Procédure resoudre_incident
CALL resoudre_incident(LAST_INSERT_ID(), 'Soumaya', 'Test résolu');
SELECT * FROM incidents WHERE id_incident = LAST_INSERT_ID();

-- TEST 4 : Requête incidents par serveur
SELECT * FROM (votre requête 1);

-- TEST 5 : Stats
CALL stats_incidents();