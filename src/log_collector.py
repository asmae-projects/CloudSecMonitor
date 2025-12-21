import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta
import sys
import os

# Ajouter le dossier parent au path pour importer config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG, SUSPECT_IPS, TEST_USERS, LOG_TYPES, LOG_STATUS


def connect_db():
    """Connexion à la base de données MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✓ Connexion à MySQL réussie")
            return connection
    except Error as e:
        print(f"✗ Erreur de connexion MySQL: {e}")
        return None


def generate_ssh_log():
    """Génère un log SSH aléatoire"""
    log = {
        "id_serveur": random.randint(1, 3),  # Serveurs 1, 2 ou 3
        "type_log": "SSH",
        "adresse_ip_source": random.choice(SUSPECT_IPS + ["192.168.1.100", "10.0.0.50"]),
        "utilisateur": random.choice(TEST_USERS),
        "statut": random.choice(["succes", "echec"]),
        "description": ""
    }
    
    # Description selon le statut
    if log["statut"] == "echec":
        log["description"] = f"Tentative de connexion SSH échouée pour {log['utilisateur']}"
    else:
        log["description"] = f"Connexion SSH réussie pour {log['utilisateur']}"
    
    return log


def generate_port_scan_log():
    """Génère un log de scan de ports"""
    log = {
        "id_serveur": random.randint(1, 3),
        "type_log": "scan_port",
        "adresse_ip_source": random.choice(SUSPECT_IPS),
        "utilisateur": None,
        "statut": "detecte",
        "description": f"Scan de ports détecté - {random.randint(10, 50)} ports analysés"
    }
    return log


def generate_file_access_log():
    """Génère un log d'accès fichier"""
    files = ["/etc/passwd", "/etc/shadow", "/var/log/auth.log", "/root/.ssh/id_rsa"]
    log = {
        "id_serveur": random.randint(1, 3),
        "type_log": "acces_fichier",
        "adresse_ip_source": random.choice(SUSPECT_IPS + ["192.168.1.100"]),
        "utilisateur": random.choice(TEST_USERS),
        "statut": random.choice(["succes", "echec"]),
        "description": f"Tentative d'accès au fichier {random.choice(files)}"
    }
    return log


def insert_log(connection, log):
    """Insère un log dans la base de données"""
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO logs_securite 
        (id_serveur, type_log, adresse_ip_source, utilisateur, statut, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            log["id_serveur"],
            log["type_log"],
            log["adresse_ip_source"],
            log["utilisateur"],
            log["statut"],
            log["description"]
        )
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"✗ Erreur insertion: {e}")
        return False
    finally:
        cursor.close()


def simulate_brute_force(connection, nb_attempts=10):
    """Simule une attaque brute force SSH"""
    print(f"\n🔴 SIMULATION ATTAQUE BRUTE FORCE ({nb_attempts} tentatives)...")
    
    attacker_ip = SUSPECT_IPS[0]  # 203.45.12.88
    target_server = 1  # WebServer01
    
    for i in range(nb_attempts):
        log = {
            "id_serveur": target_server,
            "type_log": "SSH",
            "adresse_ip_source": attacker_ip,
            "utilisateur": random.choice(TEST_USERS),
            "statut": "echec",
            "description": f"Tentative brute force #{i+1} - Mot de passe incorrect"
        }
        
        if insert_log(connection, log):
            print(f"  ✓ Tentative {i+1}/{nb_attempts} enregistrée")
    
    print(f"✓ Attaque brute force simulée avec succès")


def generate_multiple_logs(connection, nb_logs=100):
    """Génère plusieurs logs variés"""
    print(f"\n📊 GÉNÉRATION DE {nb_logs} LOGS...")
    
    success_count = 0
    
    for i in range(nb_logs):
        # Répartition: 60% SSH, 25% scan_port, 15% accès fichier
        rand = random.random()
        
        if rand < 0.60:
            log = generate_ssh_log()
        elif rand < 0.85:
            log = generate_port_scan_log()
        else:
            log = generate_file_access_log()
        
        if insert_log(connection, log):
            success_count += 1
            if (i + 1) % 20 == 0:  # Afficher progression tous les 20 logs
                print(f"  ✓ {i + 1}/{nb_logs} logs générés...")
    
    print(f"✓ {success_count}/{nb_logs} logs insérés avec succès")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("   CLOUDSECMONITOR - COLLECTEUR DE LOGS")
    print("=" * 60)
    
    # Connexion à MySQL
    connection = connect_db()
    if not connection:
        print("✗ Impossible de continuer sans connexion MySQL")
        return
    
    try:
        # Menu
        print("\n📋 QUE VOULEZ-VOUS FAIRE ?")
        print("1. Générer 100 logs variés")
        print("2. Simuler une attaque brute force")
        print("3. Les deux")
        
        choice = input("\nVotre choix (1/2/3): ").strip()
        
        if choice == "1":
            generate_multiple_logs(connection, 100)
        elif choice == "2":
            simulate_brute_force(connection, 10)
        elif choice == "3":
            generate_multiple_logs(connection, 100)
            simulate_brute_force(connection, 10)
        else:
            print("✗ Choix invalide")
        
        print("\n" + "=" * 60)
        print("✓ COLLECTE TERMINÉE - Vérifiez dans phpMyAdmin")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("✓ Connexion MySQL fermée")


if __name__ == "__main__":
    main()