-- Trigger et Requêtes
USE cloudsecmonitor;
-- Trigger 1 : Mise à jour automatique des timestamps
DELIMITER //

CREATE TRIGGER before_incident_update
BEFORE UPDATE ON incidents
FOR EACH ROW
BEGIN
    -- Si on passe à 'en_cours', enregistrer la date
    IF NEW.statut = 'en_cours' AND OLD.statut = 'nouveau' THEN
        SET NEW.date_resolution = NULL;
    END IF;
    
    -- Si on passe à 'resolu', enregistrer la date
    IF NEW.statut = 'resolu' AND OLD.statut != 'resolu' THEN
        SET NEW.date_resolution = NOW();
    END IF;
END//

DELIMITER ;

-- Trigger 2 : Auto-notification des incidents critiques
DELIMITER //

CREATE TRIGGER after_incident_critical
AFTER INSERT ON incidents
FOR EACH ROW
BEGIN
    -- Si incident critique, insérer dans une table de notifications
    IF NEW.severite = 'critique' THEN
        INSERT INTO notifications (
            type_notification,
            message,
            date_notification
        ) VALUES (
            'ALERTE_CRITIQUE',
            CONCAT('Incident critique détecté : ', NEW.type_incident),
            NOW()
        );
    END IF;
END//

DELIMITER ;

CREATE TABLE notifications (
    id_notification INT PRIMARY KEY AUTO_INCREMENT,
    type_notification VARCHAR(50),
    message TEXT,
    lu BOOLEAN DEFAULT FALSE,
    date_notification DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Requêtes SQL avancées

-- Requête 1 : Incidents par serveur avec nom du serveur

SELECT 
    s.nom_serveur,
    s.ip_adresse,
    COUNT(i.id_incident) as nombre_incidents,
    SUM(CASE WHEN i.severite = 'critique' THEN 1 ELSE 0 END) as incidents_critiques
FROM serveurs s
LEFT JOIN incidents i ON s.id_serveur = i.id_serveur
GROUP BY s.id_serveur, s.nom_serveur, s.ip_adresse
ORDER BY nombre_incidents DESC;

-- Requête 2 : Temps moyen de résolution par sévérité
SELECT 
    severite,
    COUNT(*) as total_resolu,
    AVG(TIMESTAMPDIFF(MINUTE, date_detection, date_resolution)) as temps_moyen_minutes
FROM incidents
WHERE statut = 'resolu'
GROUP BY severite;

-- Requête 3 : Top 5 des règles les plus déclenchées
SELECT 
    r.nom_regle,
    r.type_anomalie,
    COUNT(i.id_incident) as nb_declenchements
FROM regles_alerte r
LEFT JOIN incidents i ON r.id_regle = i.id_regle
GROUP BY r.id_regle, r.nom_regle, r.type_anomalie
ORDER BY nb_declenchements DESC
LIMIT 5;

-- Requête 4 : Incidents non résolus depuis plus de 24h
SELECT 
    i.id_incident,
    s.nom_serveur,
    i.type_incident,
    i.severite,
    i.date_detection,
    TIMESTAMPDIFF(HOUR, i.date_detection, NOW()) as heures_passees
FROM incidents i
JOIN serveurs s ON i.id_serveur = s.id_serveur
WHERE i.statut != 'resolu'
AND TIMESTAMPDIFF(HOUR, i.date_detection, NOW()) > 24
ORDER BY i.severite DESC, heures_passees DESC;


