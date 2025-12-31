"""
Tests de connexion et opérations de base de données
"""
import mysql.connector
from config.config import DB_CONFIG

def test_connection():
    """Tester la connexion MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✓ Connexion MySQL réussie")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Erreur connexion: {e}")
        return False

def test_tables_exist():
    """Vérifier que toutes les tables existent"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    tables = ['serveurs', 'logs_securite', 'regles_alerte', 
              'incidents', 'notifications']
    
    for table in tables:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        if cursor.fetchone():
            print(f"✓ Table {table} existe")
        else:
            print(f"✗ Table {table} manquante")
    
    cursor.close()
    conn.close()

def test_procedures_exist():
    """Vérifier que les procédures existent"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ROUTINE_NAME 
        FROM INFORMATION_SCHEMA.ROUTINES 
        WHERE ROUTINE_SCHEMA = 'cloudsecmonitor'
    """)
    
    procedures = cursor.fetchall()
    print(f"✓ {len(procedures)} procédures trouvées:")
    for proc in procedures:
        print(f"  - {proc[0]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("=== Tests CloudSecMonitor ===\n")
    test_connection()
    print()
    test_tables_exist()
    print()
    test_procedures_exist()