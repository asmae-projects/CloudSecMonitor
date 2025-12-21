-- SECTION 1 : CRÉATION DE LA BASE

CREATE DATABASE IF NOT EXISTS cloudsecmonitor;
USE cloudsecmonitor;

-- SECTION 2 : CRÉATION DES TABLES

-- Table 1: SERVEURS
CREATE TABLE serveurs (
    id_serveur INT PRIMARY KEY AUTO_INCREMENT,
    nom_serveur VARCHAR(100) NOT NULL,
    adresse_ip VARCHAR(15) NOT NULL,
    systeme_exploitation VARCHAR(50),
    localisation VARCHAR(100),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: LOGS_SECURITE
CREATE TABLE logs_securite (
    id_log INT PRIMARY KEY AUTO_INCREMENT,
    id_serveur INT NOT NULL,
    type_log VARCHAR(50) NOT NULL,
    adresse_ip_source VARCHAR(15) NOT NULL,
    utilisateur VARCHAR(50),
    statut VARCHAR(20) NOT NULL,
    date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (id_serveur) REFERENCES serveurs(id_serveur) ON DELETE CASCADE
);

-- Table 3: REGLES_ALERTE
CREATE TABLE regles_alerte (
    id_regle INT PRIMARY KEY AUTO_INCREMENT,
    nom_regle VARCHAR(100) NOT NULL,
    type_anomalie VARCHAR(50) NOT NULL,
    seuil_declenchement INT NOT NULL,
    niveau_severite ENUM('faible', 'moyen', 'critique') NOT NULL,
    action VARCHAR(100)
);

-- Table 4: INCIDENTS
CREATE TABLE incidents (
    id_incident INT PRIMARY KEY AUTO_INCREMENT,
    id_log INT NOT NULL,
    id_regle INT NOT NULL,
    type_incident VARCHAR(100),
    date_detection DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_resolution DATETIME NULL,
    niveau_severite ENUM('faible', 'moyen', 'critique') NOT NULL,
    statut ENUM('nouveau', 'en_cours', 'resolu') DEFAULT 'nouveau',
    resolu_par VARCHAR(100) NULL,
    notes TEXT NULL,
    description TEXT,
    FOREIGN KEY (id_log) REFERENCES logs_securite(id_log) ON DELETE CASCADE,
    FOREIGN KEY (id_regle) REFERENCES regles_alerte(id_regle) ON DELETE CASCADE
);

-- Table 5: NOTIFICATIONS (pour le trigger)
CREATE TABLE notifications (
    id_notification INT PRIMARY KEY AUTO_INCREMENT,
    type_notification VARCHAR(50),
    message TEXT,
    lu BOOLEAN DEFAULT FALSE,
    date_notification DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- SECTION 3 : INSERTION DES DONNÉES


-- Serveurs
INSERT INTO serveurs (nom_serveur, adresse_ip, systeme_exploitation, localisation) VALUES
('WebServer01', '192.168.1.10', 'Ubuntu 20.04', 'Paris, France'),
('DatabaseServer01', '192.168.1.20', 'CentOS 7', 'London, UK'),
('AppServer01', '192.168.1.30', 'Windows Server 2019', 'Casablanca, Morocco');

-- Règles d'alerte
INSERT INTO regles_alerte (nom_regle, type_anomalie, seuil_declenchement, niveau_severite, action) VALUES
('Brute Force SSH', 'SSH', 5, 'critique', 'Bloquer IP'),
('Port Scan Detection', 'scan_port', 20, 'moyen', 'Alerter admin'),
('Accès fichier sensible', 'acces_fichier', 1, 'critique', 'Bloquer et alerter');

-- Logs de sécurité (exemples pour tests)
INSERT INTO logs_securite (id_serveur, type_log, adresse_ip_source, utilisateur, statut, description) VALUES
(1, 'SSH', '192.168.1.50', 'root', 'echec', 'Tentative de connexion échouée'),
(1, 'SSH', '192.168.1.50', 'admin', 'echec', 'Tentative de connexion échouée'),
(2, 'scan_port', '10.0.0.100', NULL, 'detecte', 'Scan de ports détecté');


-- SECTION 4 : PROCÉDURES STOCKÉES


-- Procédure 1 : Créer un incident automatiquement
DELIMITER //

CREATE PROCEDURE creer_incident(
    IN p_id_log INT,
    IN p_id_regle INT,
    IN p_type_incident VARCHAR(100),
    IN p_description TEXT,
    IN p_severite ENUM('faible', 'moyen', 'critique')
)
BEGIN
    INSERT INTO incidents (
        id_log,
        id_regle,
        type_incident,
        description,
        niveau_severite,
        statut,
        date_detection
    ) VALUES (
        p_id_log,
        p_id_regle,
        p_type_incident,
        p_description,
        p_severite,
        'nouveau',
        NOW()
    );
END//

DELIMITER ;

-- Procédure 2 : Résoudre un incident
DELIMITER //

CREATE PROCEDURE resoudre_incident(
    IN p_id_incident INT,
    IN p_resolu_par VARCHAR(100),
    IN p_notes TEXT
)
BEGIN
    UPDATE incidents
    SET 
        statut = 'resolu',
        date_resolution = NOW(),
        resolu_par = p_resolu_par,
        notes = p_notes
    WHERE id_incident = p_id_incident;
END//

DELIMITER ;

-- Procédure 3 : Obtenir statistiques incidents
DELIMITER //

CREATE PROCEDURE stats_incidents()
BEGIN
    SELECT 
        niveau_severite as severite,
        statut,
        COUNT(*) as nombre_incidents
    FROM incidents
    GROUP BY niveau_severite, statut
    ORDER BY niveau_severite DESC, statut;
END//

DELIMITER ;


-- SECTION 5 : TRIGGERS


-- Trigger 1 : Mise à jour automatique des timestamps
DELIMITER //

CREATE TRIGGER before_incident_update
BEFORE UPDATE ON incidents
FOR EACH ROW
BEGIN
    -- Si on passe à 'en_cours', réinitialiser date_resolution
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
    -- Si incident critique, insérer dans table notifications
    IF NEW.niveau_severite = 'critique' THEN
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


-- SECTION 6 : REQUÊTES SQL AVANCÉES


-- Requête 1 : Incidents par serveur avec nom du serveur
SELECT 
    s.nom_serveur,
    s.adresse_ip,
    COUNT(i.id_incident) as nombre_incidents,
    SUM(CASE WHEN i.niveau_severite = 'critique' THEN 1 ELSE 0 END) as incidents_critiques
FROM serveurs s
LEFT JOIN logs_securite ls ON s.id_serveur = ls.id_serveur
LEFT JOIN incidents i ON ls.id_log = i.id_log
GROUP BY s.id_serveur, s.nom_serveur, s.adresse_ip
ORDER BY nombre_incidents DESC;

-- Requête 2 : Temps moyen de résolution par sévérité
SELECT 
    niveau_severite as severite,
    COUNT(*) as total_resolu,
    AVG(TIMESTAMPDIFF(MINUTE, date_detection, date_resolution)) as temps_moyen_minutes
FROM incidents
WHERE statut = 'resolu'
GROUP BY niveau_severite;

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
    i.niveau_severite as severite,
    i.date_detection,
    TIMESTAMPDIFF(HOUR, i.date_detection, NOW()) as heures_passees
FROM incidents i
JOIN logs_securite ls ON i.id_log = ls.id_log
JOIN serveurs s ON ls.id_serveur = s.id_serveur
WHERE i.statut != 'resolu'
AND TIMESTAMPDIFF(HOUR, i.date_detection, NOW()) > 24
ORDER BY i.niveau_severite DESC, heures_passees DESC;


-- SECTION 7 : TESTS ET VALIDATIONS


-- TEST 1 : Créer un incident
CALL creer_incident(1, 1, 'Connexion SSH échouée', '10 tentatives depuis 192.168.1.50', 'critique');
SELECT * FROM incidents ORDER BY id_incident DESC LIMIT 1;

-- TEST 2 : Vérifier la notification automatique
SELECT * FROM notifications ORDER BY id_notification DESC LIMIT 1;

-- TEST 3 : Résoudre l'incident
CALL resoudre_incident(LAST_INSERT_ID(), 'Soumaya&Asmae', 'Incident résolu après blocage IP');
SELECT * FROM incidents WHERE id_incident = LAST_INSERT_ID();

-- TEST 4 : Statistiques
CALL stats_incidents();

-- TEST 5 : Vérifier les triggers
SHOW TRIGGERS;

-- TEST 6 : Vérifier les procédures
SHOW PROCEDURE STATUS WHERE Db = 'cloudsecmonitor';
