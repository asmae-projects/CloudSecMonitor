CREATE DATABASE IF NOT EXISTS cloudsecmonitor;
USE cloudsecmonitor;

-- TABLES
CREATE TABLE IF NOT EXISTS serveurs (
    id_serveur INT PRIMARY KEY AUTO_INCREMENT,
    nom_serveur VARCHAR(100) NOT NULL,
    adresse_ip VARCHAR(45) NOT NULL,
    systeme_exploitation VARCHAR(50),
    statut ENUM('actif', 'inactif') DEFAULT 'actif',
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_securite (
    id_log INT PRIMARY KEY AUTO_INCREMENT,
    serveur_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type_log VARCHAR(50) NOT NULL,
    adresse_ip_source VARCHAR(45),
    port_source INT,
    port_destination INT,
    protocole VARCHAR(20),
    message TEXT NOT NULL,
    severite VARCHAR(20) DEFAULT 'info',
    FOREIGN KEY (serveur_id) REFERENCES serveurs(id_serveur)
);

CREATE TABLE IF NOT EXISTS incidents (
    id_incident INT PRIMARY KEY AUTO_INCREMENT,
    log_id INT NOT NULL,
    type_incident VARCHAR(100) NOT NULL,
    severite ENUM('faible', 'moyen', 'critique') NOT NULL,
    description TEXT,
    statut ENUM('nouveau', 'en_cours', 'resolu', 'ignore') DEFAULT 'nouveau',
    date_detection DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_resolution DATETIME,
    FOREIGN KEY (log_id) REFERENCES logs_securite(id_log)
);

CREATE TABLE IF NOT EXISTS regles_alerte (
    id_regle INT PRIMARY KEY AUTO_INCREMENT,
    nom_regle VARCHAR(100) NOT NULL,
    type_log VARCHAR(50),
    condition_type VARCHAR(50),
    condition_valeur VARCHAR(255),
    niveau_severite ENUM('faible', 'moyen', 'critique'),
    description TEXT,
    actif BOOLEAN DEFAULT TRUE
);

-- DONNÉES
INSERT INTO serveurs (nom_serveur, adresse_ip, systeme_exploitation) VALUES
('WebServer-01', '192.168.1.10', 'Ubuntu 22.04'),
('DBServer-01', '192.168.1.20', 'CentOS 8'),
('AppServer-01', '192.168.1.30', 'Windows Server 2019');

INSERT INTO logs_securite (serveur_id, type_log, adresse_ip_source, port_destination, protocole, message, severite) VALUES
(1, 'connexion', '192.168.1.100', 22, 'SSH', 'Connexion SSH réussie', 'info'),
(1, 'connexion', '10.0.0.50', 22, 'SSH', 'Tentative de connexion SSH failed', 'warning');