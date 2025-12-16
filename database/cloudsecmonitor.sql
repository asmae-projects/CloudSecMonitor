-- Créer la base de données
CREATE DATABASE IF NOT EXISTS cloudsecmonitor;
USE cloudsecmonitor;

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
    date_detection DATETIME DEFAULT CURRENT_TIMESTAMP,
    niveau_severite ENUM('faible', 'moyen', 'critique') NOT NULL,
    statut ENUM('nouveau', 'en_cours', 'resolu') DEFAULT 'nouveau',
    description TEXT,
    FOREIGN KEY (id_log) REFERENCES logs_securite(id_log) ON DELETE CASCADE,
    FOREIGN KEY (id_regle) REFERENCES regles_alerte(id_regle) ON DELETE CASCADE
);

-- Insérer des données de test

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



--Créer des procédures stockées

--Procédure 1 : Créer un incident automatiquement

DELIMITER //

CREATE PROCEDURE creer_incident(
    IN p_id_serveur INT,
    IN p_id_regle INT,
    IN p_type_incident VARCHAR(100),
    IN p_description TEXT,
    IN p_severite ENUM('faible', 'moyen', 'critique')
)
BEGIN
    INSERT INTO incidents (
        id_serveur,
        id_regle,
        type_incident,
        description,
        severite,
        statut,
        date_detection
    ) VALUES (
        p_id_serveur,
        p_id_regle,
        p_type_incident,
        p_description,
        p_severite,
        'nouveau',
        NOW()
    );
END//

DELIMITER ;

--Test de la procédure 
CALL creer_incident(1, 1, 'Connexion SSH échouée', '10 tentatives depuis 192.168.1.50', 'critique');
SELECT * FROM incidents ORDER BY id_incident DESC LIMIT 1;

--Procédure 2 : Résoudre un incident

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

--Test 
CALL resoudre_incident(1, 'Admin Soumaya', 'Incident résolu après blocage IP');
SELECT * FROM incidents WHERE id_incident = 1;

--Procédure 3 : Obtenir statistiques incidents
DELIMITER //

CREATE PROCEDURE stats_incidents()
BEGIN
    SELECT 
        severite,
        statut,
        COUNT(*) as nombre_incidents
    FROM incidents
    GROUP BY severite, statut
    ORDER BY severite DESC, statut;
END//

DELIMITER ;

--test
CALL stats_incidents();

