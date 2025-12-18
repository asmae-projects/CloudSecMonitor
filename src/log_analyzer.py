import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import sys
import os
import time

# Importer config et alert_system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG


def connect_db():
    """Connexion à la base de données MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"✗ Erreur de connexion MySQL: {e}")
        return None


def detect_brute_force(connection):
    """
    Détecte les attaques brute force SSH
    Critère: 5+ tentatives échouées en 5 minutes depuis la même IP
    """
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Récupérer les logs SSH échoués des 5 dernières minutes
        query = """
        SELECT 
            id_log,
            id_serveur,
            adresse_ip_source,
            utilisateur,
            date_heure,
            description
        FROM logs_securite
        WHERE type_log = 'SSH'
        AND statut = 'echec'
        AND date_heure >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
        ORDER BY adresse_ip_source, date_heure DESC
        """
        
        cursor.execute(query)
        logs = cursor.fetchall()
        
        if not logs:
            return []
        
        # Compter les tentatives par IP
        ip_attempts = {}
        for log in logs:
            ip = log['adresse_ip_source']
            if ip not in ip_attempts:
                ip_attempts[ip] = []
            ip_attempts[ip].append(log)
        
        # Détecter les attaques (5+ tentatives)
        attacks = []
        for ip, attempts in ip_attempts.items():
            if len(attempts) >= 5:
                attacks.append({
                    'ip_source': ip,
                    'nb_tentatives': len(attempts),
                    'id_serveur': attempts[0]['id_serveur'],
                    'premier_log': attempts[-1]['id_log'],  # Plus ancien
                    'dernier_log': attempts[0]['id_log'],   # Plus récent
                    'utilisateurs': list(set([a['utilisateur'] for a in attempts if a['utilisateur']])),
                    'periode': f"{attempts[-1]['date_heure']} → {attempts[0]['date_heure']}"
                })
        
        cursor.close()
        return attacks
        
    except Error as e:
        print(f"✗ Erreur détection brute force: {e}")
        return []


def detect_port_scan(connection):
    """
    Détecte les scans de ports massifs
    Critère: 3+ scans détectés en 10 minutes depuis la même IP
    """
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            id_log,
            id_serveur,
            adresse_ip_source,
            date_heure,
            description
        FROM logs_securite
        WHERE type_log = 'scan_port'
        AND statut = 'detecte'
        AND date_heure >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
        ORDER BY adresse_ip_source, date_heure DESC
        """
        
        cursor.execute(query)
        logs = cursor.fetchall()
        
        if not logs:
            return []
        
        # Compter par IP
        ip_scans = {}
        for log in logs:
            ip = log['adresse_ip_source']
            if ip not in ip_scans:
                ip_scans[ip] = []
            ip_scans[ip].append(log)
        
        # Détecter activité suspecte (3+ scans)
        attacks = []
        for ip, scans in ip_scans.items():
            if len(scans) >= 3:
                attacks.append({
                    'ip_source': ip,
                    'nb_scans': len(scans),
                    'id_serveur': scans[0]['id_serveur'],
                    'premier_log': scans[-1]['id_log'],
                    'dernier_log': scans[0]['id_log']
                })
        
        cursor.close()
        return attacks
        
    except Error as e:
        print(f"✗ Erreur détection port scan: {e}")
        return []


def get_server_name(connection, id_serveur):
    """Récupère le nom du serveur depuis son ID"""
    try:
        cursor = connection.cursor()
        query = "SELECT nom_serveur FROM serveurs WHERE id_serveur = %s"
        cursor.execute(query, (id_serveur,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else f"Serveur {id_serveur}"
    except:
        return f"Serveur {id_serveur}"


def check_if_incident_exists(connection, id_log, id_regle):
    """Vérifie si un incident existe déjà pour ce log et cette règle"""
    try:
        cursor = connection.cursor()
        query = """
        SELECT COUNT(*) FROM incidents 
        WHERE id_log = %s AND id_regle = %s
        """
        cursor.execute(query, (id_log, id_regle))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except:
        return False


def analyze_logs(connection):
    """
    Fonction principale d'analyse
    Appelle les fonctions de détection et crée des incidents
    """
    print("\n" + "="*60)
    print("   ANALYSE DES LOGS EN COURS...")
    print("="*60)
    
    total_incidents = 0
    
    # 1. Détection Brute Force
    print("\n🔍 Recherche d'attaques Brute Force SSH...")
    brute_force_attacks = detect_brute_force(connection)
    
    if brute_force_attacks:
        print(f"⚠️  {len(brute_force_attacks)} attaque(s) brute force détectée(s)!")
        
        for attack in brute_force_attacks:
            server_name = get_server_name(connection, attack['id_serveur'])
            
            print(f"\n🔴 ATTAQUE DÉTECTÉE:")
            print(f"   IP Source: {attack['ip_source']}")
            print(f"   Serveur: {server_name}")
            print(f"   Tentatives: {attack['nb_tentatives']}")
            print(f"   Utilisateurs testés: {', '.join(attack['utilisateurs'])}")
            print(f"   Période: {attack['periode']}")
            
            # Vérifier si incident existe déjà
            if not check_if_incident_exists(connection, attack['dernier_log'], 1):
                # Créer l'incident via alert_system
                from alert_system import create_incident
                
                description = f"Attaque Brute Force SSH détectée - {attack['nb_tentatives']} tentatives depuis {attack['ip_source']}"
                
                if create_incident(
                    connection,
                    attack['dernier_log'],
                    1,  # id_regle pour Brute Force SSH
                    "Brute Force SSH",
                    description,
                    'critique'
                ):
                    print(f"   ✓ Incident créé dans la base de données")
                    total_incidents += 1
            else:
                print(f"   ℹ️  Incident déjà enregistré pour cette attaque")
    else:
        print("✓ Aucune attaque brute force détectée")
    
    # 2. Détection Port Scan
    print("\n🔍 Recherche de scans de ports...")
    port_scans = detect_port_scan(connection)
    
    if port_scans:
        print(f"⚠️  {len(port_scans)} scan(s) de ports détecté(s)!")
        
        for scan in port_scans:
            server_name = get_server_name(connection, scan['id_serveur'])
            
            print(f"\n🟠 SCAN DÉTECTÉ:")
            print(f"   IP Source: {scan['ip_source']}")
            print(f"   Serveur: {server_name}")
            print(f"   Nombre de scans: {scan['nb_scans']}")
            
            if not check_if_incident_exists(connection, scan['dernier_log'], 2):
                from alert_system import create_incident
                
                description = f"Scan de ports massif détecté - {scan['nb_scans']} scans depuis {scan['ip_source']}"
                
                if create_incident(
                    connection,
                    scan['dernier_log'],
                    2,  # id_regle pour Port Scan
                    "Port Scan Detection",
                    description,
                    'moyen'
                ):
                    print(f"   ✓ Incident créé dans la base de données")
                    total_incidents += 1
            else:
                print(f"   ℹ️  Incident déjà enregistré pour ce scan")
    else:
        print("✓ Aucun scan de ports détecté")
    
    print("\n" + "="*60)
    print(f"✓ ANALYSE TERMINÉE - {total_incidents} nouveau(x) incident(s) créé(s)")
    print("="*60)
    
    return total_incidents


def continuous_monitoring(interval=30):
    """
    Mode de surveillance continue
    Analyse les logs toutes les X secondes
    """
    print("\n🔄 MODE SURVEILLANCE CONTINUE ACTIVÉ")
    print(f"📊 Analyse toutes les {interval} secondes")
    print("⏸️  Appuyez sur Ctrl+C pour arrêter\n")
    
    connection = connect_db()
    if not connection:
        print("✗ Impossible de démarrer la surveillance")
        return
    
    try:
        iteration = 1
        while True:
            print(f"\n--- Itération #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            analyze_logs(connection)
            
            print(f"\n⏳ Prochaine analyse dans {interval} secondes...")
            time.sleep(interval)
            iteration += 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Surveillance arrêtée par l'utilisateur")
    finally:
        if connection.is_connected():
            connection.close()
            print("✓ Connexion MySQL fermée")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("   CLOUDSECMONITOR - ANALYSEUR DE LOGS")
    print("=" * 60)
    
    connection = connect_db()
    if not connection:
        print("✗ Impossible de continuer sans connexion MySQL")
        return
    
    try:
        print("\n📋 MODE D'ANALYSE:")
        print("1. Analyse unique (maintenant)")
        print("2. Surveillance continue (toutes les 30 secondes)")
        
        choice = input("\nVotre choix (1/2): ").strip()
        
        if choice == "1":
            analyze_logs(connection)
        elif choice == "2":
            connection.close()  # Fermer pour rouvrir dans continuous_monitoring
            continuous_monitoring(30)
        else:
            print("✗ Choix invalide")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ Connexion MySQL fermée")


if __name__ == "__main__":
    main()