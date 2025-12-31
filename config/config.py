# Configuration MySQL pour Workbench (WAMP)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Pas de mot de passe (connexion locale WAMPet aussi pour phpmyadmin)
    "database": "cloudsecmonitor", 
    "port": 3306  
}

# IPs suspectes pour simulation d'attaques
SUSPECT_IPS = [
    "203.45.12.88",   # IP attaquant Brute Force
    "198.23.45.67",   # IP Port Scanner
    "176.89.12.34",   # IP accès non autorisé
    "45.76.123.45",   # IP supplémentaire
    "89.234.67.12"    # IP supplémentaire
]

# Utilisateurs testés lors des attaques
TEST_USERS = ["admin", "root", "user", "test", "guest"]

# Types de logs disponibles
LOG_TYPES = ["SSH", "scan_port", "acces_fichier"]

# Statuts possibles
LOG_STATUS = ["succes", "echec", "detecte"]