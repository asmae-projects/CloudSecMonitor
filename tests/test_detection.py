"""
Tests de détection d'attaques
"""
from src.log_analyzer import detect_brute_force
import mysql.connector
from config.config import DB_CONFIG

def test_brute_force_detection():
    """Tester la détection Brute Force"""
    print("Test détection Brute Force...")
    
    # Simuler 10 logs SSH échecs
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Nettoyer anciens logs de test
    cursor.execute("""
        DELETE FROM logs_securite 
        WHERE adresse_ip_source = '999.999.999.999'
    """)
    
    # Insérer 10 tentatives
    for i in range(10):
        cursor.execute("""
            INSERT INTO logs_securite 
            (id_serveur, type_log, adresse_ip_source, 
             utilisateur, statut, description)
            VALUES (1, 'SSH', '999.999.999.999', 'test', 'echec', 'Test')
        """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Tester détection
    attacks = detect_brute_force()
    
    if len(attacks) > 0:
        print("✓ Brute Force détecté correctement")
    else:
        print("✗ Brute Force non détecté")

if __name__ == "__main__":
    test_brute_force_detection()