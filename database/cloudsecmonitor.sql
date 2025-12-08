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