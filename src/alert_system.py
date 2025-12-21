import mysql.connector
from mysql.connector import Error
from datetime import datetime
import sys
import os

# Importer config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG


# Codes couleurs pour le terminal
class Colors:
    RED = '\033[91m'      # Rouge - Critique
    YELLOW = '\033[93m'   # Jaune - Moyen
    GREEN = '\033[92m'    # Vert - Faible
    BLUE = '\033[94m'     # Bleu - Info
    RESET = '\033[0m'     # Reset couleur
    BOLD = '\033[1m'      # Gras


def connect_db():
    """Connexion à la base de données MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"✗ Erreur de connexion MySQL: {e}")
        return None


def create_incident(connection, id_log, id_regle, type_incident, description, niveau_severite):
    """
    Crée un incident dans la table incidents
    
    Args:
        connection: Connexion MySQL
        id_log: ID du log ayant déclenché l'incident
        id_regle: ID de la règle appliquée
        type_incident: Type d'incident (ex: "Brute Force SSH")
        description: Description détaillée
        niveau_severite: 'faible', 'moyen', ou 'critique'
    
    Returns:
        True si succès, False sinon
    """
    try:
        cursor = connection.cursor()
        
        query = """
        INSERT INTO incidents (
            id_log,
            id_regle,
            type_incident,
            description,
            niveau_severite,
            statut,
            date_detection
        ) VALUES (%s, %s, %s, %s, %s, 'nouveau', NOW())
        """
        
        values = (
            id_log,
            id_regle,
            type_incident,
            description,
            niveau_severite
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        incident_id = cursor.lastrowid
        cursor.close()
        
        # Afficher l'alerte
        display_alert(incident_id, type_incident, description, niveau_severite)
        
        return True
        
    except Error as e:
        print(f"✗ Erreur création incident: {e}")
        return False


def display_alert(incident_id, type_incident, description, niveau_severite):
    """
    Affiche une alerte colorée dans le terminal
    
    Args:
        incident_id: ID de l'incident créé
        type_incident: Type d'incident
        description: Description
        niveau_severite: Niveau de sévérité
    """
    # Choisir la couleur selon la sévérité
    if niveau_severite == 'critique':
        color = Colors.RED
        icon = "🔴"
        label = "ALERTE CRITIQUE"
    elif niveau_severite == 'moyen':
        color = Colors.YELLOW
        icon = "🟠"
        label = "ALERTE MOYENNE"
    else:
        color = Colors.GREEN
        icon = "🟢"
        label = "ALERTE FAIBLE"
    
    # Afficher l'alerte
    print(f"\n{color}{Colors.BOLD}{'='*60}")
    print(f"{icon} [{label}] INCIDENT #{incident_id}")
    print(f"{'='*60}{Colors.RESET}")
    print(f"{color}Type: {type_incident}")
    print(f"Sévérité: {niveau_severite.upper()}")
    print(f"Description: {description}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Statut: NOUVEAU{Colors.RESET}")
    print(f"{color}{'='*60}{Colors.RESET}\n")


def get_incidents_stats(connection):
    """Affiche les statistiques des incidents"""
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Stats globales
        query = """
        SELECT 
            niveau_severite,
            statut,
            COUNT(*) as nombre
        FROM incidents
        GROUP BY niveau_severite, statut
        ORDER BY 
            FIELD(niveau_severite, 'critique', 'moyen', 'faible'),
            FIELD(statut, 'nouveau', 'en_cours', 'resolu')
        """
        
        cursor.execute(query)
        stats = cursor.fetchall()
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}📊 STATISTIQUES DES INCIDENTS{Colors.RESET}")
        print("="*60)
        
        if stats:
            for stat in stats:
                sev_color = Colors.RED if stat['niveau_severite'] == 'critique' else (
                    Colors.YELLOW if stat['niveau_severite'] == 'moyen' else Colors.GREEN
                )
                print(f"{sev_color}{stat['niveau_severite'].upper()}{Colors.RESET} - "
                      f"{stat['statut']}: {stat['nombre']}")
        else:
            print("Aucun incident enregistré")
        
        print("="*60)
        
        cursor.close()
        
    except Error as e:
        print(f"✗ Erreur récupération stats: {e}")


def get_recent_incidents(connection, limit=10):
    """Affiche les incidents récents"""
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            i.id_incident,
            i.type_incident,
            i.niveau_severite,
            i.statut,
            i.date_detection,
            i.description,
            s.nom_serveur
        FROM incidents i
        JOIN logs_securite ls ON i.id_log = ls.id_log
        JOIN serveurs s ON ls.id_serveur = s.id_serveur
        ORDER BY i.date_detection DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        incidents = cursor.fetchall()
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}📋 INCIDENTS RÉCENTS (Top {limit}){Colors.RESET}")
        print("="*60)
        
        if incidents:
            for inc in incidents:
                # Couleur selon sévérité
                sev_color = Colors.RED if inc['niveau_severite'] == 'critique' else (
                    Colors.YELLOW if inc['niveau_severite'] == 'moyen' else Colors.GREEN
                )
                
                print(f"\n{sev_color}#{inc['id_incident']} - {inc['type_incident']}{Colors.RESET}")
                print(f"  Serveur: {inc['nom_serveur']}")
                print(f"  Sévérité: {inc['niveau_severite']} | Statut: {inc['statut']}")
                print(f"  Date: {inc['date_detection']}")
                print(f"  Description: {inc['description'][:80]}...")
        else:
            print("Aucun incident récent")
        
        print("="*60)
        
        cursor.close()
        
    except Error as e:
        print(f"✗ Erreur récupération incidents: {e}")


def update_incident_status(connection, incident_id, new_status, resolu_par=None, notes=None):
    """
    Met à jour le statut d'un incident
    
    Args:
        connection: Connexion MySQL
        incident_id: ID de l'incident
        new_status: 'nouveau', 'en_cours', ou 'resolu'
        resolu_par: Nom de la personne (si résolu)
        notes: Notes sur la résolution
    """
    try:
        cursor = connection.cursor()
        
        if new_status == 'resolu':
            query = """
            UPDATE incidents
            SET statut = %s,
                date_resolution = NOW(),
                resolu_par = %s,
                notes = %s
            WHERE id_incident = %s
            """
            cursor.execute(query, (new_status, resolu_par, notes, incident_id))
        else:
            query = """
            UPDATE incidents
            SET statut = %s
            WHERE id_incident = %s
            """
            cursor.execute(query, (new_status, incident_id))
        
        connection.commit()
        cursor.close()
        
        print(f"✓ Incident #{incident_id} mis à jour: {new_status}")
        return True
        
    except Error as e:
        print(f"✗ Erreur mise à jour incident: {e}")
        return False


def main():
    """Fonction principale - Interface de gestion des alertes"""
    print("=" * 60)
    print("   CLOUDSECMONITOR - SYSTÈME D'ALERTES")
    print("=" * 60)
    
    connection = connect_db()
    if not connection:
        print("✗ Impossible de continuer sans connexion MySQL")
        return
    
    try:
        while True:
            print(f"\n{Colors.BLUE}📋 MENU PRINCIPAL{Colors.RESET}")
            print("1. Voir statistiques des incidents")
            print("2. Voir incidents récents")
            print("3. Créer un incident test")
            print("4. Mettre à jour statut d'un incident")
            print("5. Quitter")
            
            choice = input("\nVotre choix (1-5): ").strip()
            
            if choice == "1":
                get_incidents_stats(connection)
            
            elif choice == "2":
                limit = input("Nombre d'incidents à afficher (défaut 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                get_recent_incidents(connection, limit)
            
            elif choice == "3":
                print("\n🧪 CRÉATION D'UN INCIDENT TEST")
                type_inc = input("Type d'incident: ").strip() or "Test Incident"
                desc = input("Description: ").strip() or "Incident de test"
                sev = input("Sévérité (faible/moyen/critique): ").strip() or "moyen"
                
                create_incident(connection, 1, 1, type_inc, desc, sev)
            
            elif choice == "4":
                inc_id = input("ID de l'incident: ").strip()
                if inc_id.isdigit():
                    print("Nouveau statut: 1=en_cours, 2=resolu")
                    status_choice = input("Choix: ").strip()
                    
                    if status_choice == "1":
                        update_incident_status(connection, int(inc_id), 'en_cours')
                    elif status_choice == "2":
                        resolu_par = input("Résolu par: ").strip() or "Admin"
                        notes = input("Notes: ").strip() or "Incident résolu"
                        update_incident_status(connection, int(inc_id), 'resolu', resolu_par, notes)
                else:
                    print("✗ ID invalide")
            
            elif choice == "5":
                print("\n👋 Au revoir!")
                break
            
            else:
                print("✗ Choix invalide")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("✓ Connexion MySQL fermée")


if __name__ == "__main__":
    main()