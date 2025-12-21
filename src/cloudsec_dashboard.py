"""
CloudSecMonitor - Dashboard Streamlit
Projet Python et Bases de Données - M. BOUKSIM
Asmae ZIANI & Soumia BADAOUI
"""

import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ========================================
# CONFIGURATION DE LA PAGE
# ========================================

st.set_page_config(
    page_title="CloudSecMonitor Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CHARGER LE CSS EXTERNE
# ========================================

def load_css(file_name):
    """Charge un fichier CSS externe"""
    css_file = Path(__file__).parent.parent / "assets" / file_name
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Charger le style
try:
    load_css("style.css")
except FileNotFoundError:
    st.warning("⚠️ Fichier CSS non trouvé. Le dashboard fonctionnera sans styles personnalisés.")

# ========================================
# FONCTIONS DE CONNEXION BASE DE DONNÉES
# ========================================

@st.cache_resource
def get_connection():
    """Établit la connexion à la base de données MySQL"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="cloudsecmonitor"
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"❌ Erreur de connexion à MySQL: {err}")
        return None

def get_global_stats():
    """Récupère les statistiques globales du système"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    stats = {}
    
    cursor.execute("SELECT COUNT(*) as total FROM logs_securite")
    stats['total_logs'] = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM incidents 
        WHERE niveau_severite = 'critique' AND statut = 'nouveau'
    """)
    stats['incidents_critiques'] = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(DISTINCT adresse_ip_source) as total 
        FROM logs_securite 
        WHERE statut = 'echec'
    """)
    stats['ips_suspectes'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM incidents")
    stats['total_incidents'] = cursor.fetchone()['total']
    
    cursor.close()
    return stats

def get_logs_by_type():
    """Récupère le nombre de logs par type"""
    conn = get_connection()
    if not conn:
        return None
    
    query = """
        SELECT type_log, COUNT(*) as count
        FROM logs_securite
        GROUP BY type_log
        ORDER BY count DESC
    """
    df = pd.read_sql(query, conn)
    return df

def get_recent_logs(limit=50):
    """Récupère les derniers logs"""
    conn = get_connection()
    if not conn:
        return None
    
    query = f"""
        SELECT 
            l.date_heure,
            s.nom_serveur,
            l.type_log,
            l.adresse_ip_source,
            l.utilisateur,
            l.statut,
            l.description
        FROM logs_securite l
        JOIN serveurs s ON l.id_serveur = s.id_serveur
        ORDER BY l.date_heure DESC
        LIMIT {limit}
    """
    df = pd.read_sql(query, conn)
    return df

def get_incidents():
    """Récupère tous les incidents"""
    conn = get_connection()
    if not conn:
        return None
    
    query = """
        SELECT 
            i.id_incident,
            i.date_detection,
            i.niveau_severite,
            i.statut,
            i.description,
            s.nom_serveur,
            l.adresse_ip_source
        FROM incidents i
        JOIN logs_securite l ON i.id_log = l.id_log
        JOIN serveurs s ON l.id_serveur = s.id_serveur
        ORDER BY i.date_detection DESC
    """
    df = pd.read_sql(query, conn)
    return df

def get_incidents_by_day():
    """Récupère le nombre d'incidents par jour"""
    conn = get_connection()
    if not conn:
        return None
    
    query = """
        SELECT 
            DATE(date_detection) as date,
            COUNT(*) as count
        FROM incidents
        GROUP BY DATE(date_detection)
        ORDER BY date DESC
        LIMIT 30
    """
    df = pd.read_sql(query, conn)
    return df

def get_top_suspect_ips():
    """Récupère les IPs les plus suspectes"""
    conn = get_connection()
    if not conn:
        return None
    
    query = """
        SELECT 
            adresse_ip_source,
            COUNT(*) as tentatives
        FROM logs_securite
        WHERE statut = 'echec'
        GROUP BY adresse_ip_source
        ORDER BY tentatives DESC
        LIMIT 10
    """
    df = pd.read_sql(query, conn)
    return df

# ========================================
# SIDEBAR
# ========================================

st.sidebar.markdown("""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <h1 style='color: #42A5F5; font-size: 2rem; font-weight: 900; margin: 0;'>
            🔒 CloudSecMonitor
        </h1>
        <p style='color: #94A3B8; font-size: 0.9rem; margin-top: 0.5rem; letter-spacing: 0.1em;'>
            SECURITY OPERATIONS CENTER
        </p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    ["🏠 Accueil", "📋 Liste des Logs", "🚨 Incidents", "📊 Statistiques Avancées"]
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
    <div class='sidebar-info'>
        <h4>PROJET ACADÉMIQUE</h4>
        <p><strong>Programme:</strong><br/>Python et Bases de Données</p>
        <p><strong>Équipe:</strong><br/>Asmae ZIANI<br/>Soumia BADAOUI</p>
        <p><strong>Encadrant:</strong><br/>M. BOUKSIM</p>
        <p><strong>Formation:</strong><br/>ITIRC 4ème année</p>
    </div>
    """, unsafe_allow_html=True)

# ========================================
# PAGE 1: ACCUEIL
# ========================================

if page == "🏠 Accueil":
    st.markdown('<p class="main-header">CloudSecMonitor</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Système de Surveillance et d\'Audit de Sécurité Cloud en Temps Réel</p>', unsafe_allow_html=True)
    
    stats = get_global_stats()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 LOGS TOTAUX", f"{stats['total_logs']:,}", "Événements surveillés")
        
        with col2:
            st.metric("🚨 ALERTES CRITIQUES", stats['incidents_critiques'], 
                     "Nécessitent action" if stats['incidents_critiques'] > 0 else "Système sécurisé",
                     delta_color="inverse")
        
        with col3:
            st.metric("🌐 MENACES ACTIVES", stats['ips_suspectes'], "IPs suspectes")
        
        with col4:
            st.metric("📋 INCIDENTS TOTAUX", stats['total_incidents'], "Historique complet")
        
        st.markdown("---")
        
        st.markdown("""
            <div class='info-box'>
                <h3>📡 Statut du Système de Surveillance</h3>
                <p>CloudSecMonitor surveille en continu votre infrastructure cloud pour détecter 
                les menaces en temps réel. Analyse comportementale avancée avec détection automatique d'anomalies.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 ANALYSE DES ÉVÉNEMENTS")
            logs_by_type = get_logs_by_type()
            
            if logs_by_type is not None and not logs_by_type.empty:
                fig = px.bar(logs_by_type, x='type_log', y='count',
                           labels={'type_log': 'Type', 'count': 'Nombre'},
                           color='count', color_continuous_scale=['#1976D2', '#42A5F5', '#00BCD4'],
                           template='plotly_dark')
                fig.update_layout(showlegend=False, height=400, paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E7FF'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            st.markdown("### 🎯 MENACES DÉTECTÉES")
            top_ips = get_top_suspect_ips()
            
            if top_ips is not None and not top_ips.empty:
                fig = px.bar(top_ips, x='tentatives', y='adresse_ip_source', orientation='h',
                           labels={'adresse_ip_source': 'IP', 'tentatives': 'Tentatives'},
                           color='tentatives', color_continuous_scale=['#F57C00', '#D32F2F'],
                           template='plotly_dark')
                fig.update_layout(showlegend=False, height=400, paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E7FF'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        st.markdown("### ⚠️ INCIDENTS CRITIQUES RÉCENTS")
        
        incidents_df = get_incidents()
        if incidents_df is not None and not incidents_df.empty:
            critical = incidents_df[incidents_df['niveau_severite'] == 'critique'].head(5)
            
            if not critical.empty:
                for _, row in critical.iterrows():
                    with st.expander(f"🔴 {row['description'][:60]}... | {row['date_detection']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**🖥️ Serveur:** `{row['nom_serveur']}`")
                        with col2:
                            st.write(f"**🌐 IP Source:** `{row['adresse_ip_source']}`")
                        with col3:
                            st.write(f"**📊 Statut:** {row['statut'].upper()}")
                        st.write(f"**Description:** {row['description']}")

# ========================================
# PAGE 2: LISTE DES LOGS
# ========================================

elif page == "📋 Liste des Logs":
    st.markdown('<p class="main-header">Registre des Événements</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Consultation et analyse détaillée des logs de sécurité</p>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 FILTRES DE RECHERCHE")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        type_filter = st.selectbox("TYPE D'ÉVÉNEMENT", ["Tous", "SSH", "scan_port", "acces_fichier"])
    with col2:
        status_filter = st.selectbox("STATUT", ["Tous", "succes", "echec"])
    with col3:
        limit = st.slider("NOMBRE", 10, 200, 50, 10)
    
    st.markdown("---")
    
    logs_df = get_recent_logs(limit)
    
    if logs_df is not None and not logs_df.empty:
        if type_filter != "Tous":
            logs_df = logs_df[logs_df['type_log'] == type_filter]
        if status_filter != "Tous":
            logs_df = logs_df[logs_df['statut'] == status_filter]
        
        logs_df['date_heure'] = pd.to_datetime(logs_df['date_heure']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 AFFICHÉS", len(logs_df))
        with col2:
            echecs = len(logs_df[logs_df['statut'] == 'echec'])
            st.metric("❌ ÉCHECS", echecs)
        with col3:
            succes = len(logs_df[logs_df['statut'] == 'succes'])
            st.metric("✅ SUCCÈS", succes)
        
        st.markdown("---")
        st.markdown("### 📋 TABLEAU DES ÉVÉNEMENTS")
        st.dataframe(logs_df, use_container_width=True, height=600)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = logs_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 EXPORTER EN CSV", csv,
                             f'logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                             'text/csv', use_container_width=True)

# ========================================
# PAGE 3: INCIDENTS
# ========================================

elif page == "🚨 Incidents":
    st.markdown('<p class="main-header">Centre de Gestion des Incidents</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Surveillance et réponse aux menaces de sécurité</p>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 FILTRES")
    col1, col2 = st.columns(2)
    
    with col1:
        severity_filter = st.selectbox("SÉVÉRITÉ", ["Tous", "critique", "moyen", "faible"])
    with col2:
        status_filter = st.selectbox("STATUT", ["Tous", "nouveau", "en_cours", "resolu"])
    
    st.markdown("---")
    
    incidents_df = get_incidents()
    
    if incidents_df is not None and not incidents_df.empty:
        if severity_filter != "Tous":
            incidents_df = incidents_df[incidents_df['niveau_severite'] == severity_filter]
        if status_filter != "Tous":
            incidents_df = incidents_df[incidents_df['statut'] == status_filter]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 CRITIQUES", len(incidents_df[incidents_df['niveau_severite'] == 'critique']))
        with col2:
            st.metric("🟠 MOYENS", len(incidents_df[incidents_df['niveau_severite'] == 'moyen']))
        with col3:
            st.metric("🟢 FAIBLES", len(incidents_df[incidents_df['niveau_severite'] == 'faible']))
        with col4:
            st.metric("⏳ EN COURS", len(incidents_df[incidents_df['statut'].isin(['nouveau', 'en_cours'])]))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 RÉPARTITION")
            severity_counts = incidents_df['niveau_severite'].value_counts()
            fig = px.pie(values=severity_counts.values, names=severity_counts.index,
                        color=severity_counts.index,
                        color_discrete_map={'critique': '#D32F2F', 'moyen': '#F57C00', 'faible': '#388E3C'},
                        template='plotly_dark', hole=0.4)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            st.markdown("### 📈 ÉVOLUTION")
            incidents_by_day = get_incidents_by_day()
            if incidents_by_day is not None and not incidents_by_day.empty:
                fig = px.area(incidents_by_day, x='date', y='count',
                            labels={'date': 'Date', 'count': 'Incidents'},
                            template='plotly_dark')
                fig.update_traces(line_color='#D32F2F', fillcolor='rgba(211, 47, 47, 0.3)')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E7FF'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        st.markdown("### 📋 REGISTRE DES INCIDENTS")
        
        incidents_df['date_detection'] = pd.to_datetime(incidents_df['date_detection']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(incidents_df, use_container_width=True, height=400)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = incidents_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 EXPORTER", csv,
                             f'incidents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                             'text/csv', use_container_width=True)

# ========================================
# PAGE 4: STATISTIQUES AVANCÉES
# ========================================

elif page == "📊 Statistiques Avancées":
    st.markdown('<p class="main-header">Statistiques Avancées</p>', unsafe_allow_html=True)
    
    conn = get_connection()
    
    if conn:
        st.subheader("🖥️ Activité par Serveur")
        query = """
            SELECT s.nom_serveur,
                   COUNT(*) as total_logs,
                   SUM(CASE WHEN l.statut = 'echec' THEN 1 ELSE 0 END) as echecs,
                   SUM(CASE WHEN l.statut = 'succes' THEN 1 ELSE 0 END) as succes
            FROM logs_securite l
            JOIN serveurs s ON l.id_serveur = s.id_serveur
            GROUP BY s.nom_serveur
            ORDER BY total_logs DESC
        """
        server_stats = pd.read_sql(query, conn)
        
        if not server_stats.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Succès', x=server_stats['nom_serveur'], 
                               y=server_stats['succes'], marker_color='green'))
            fig.add_trace(go.Bar(name='Échecs', x=server_stats['nom_serveur'], 
                               y=server_stats['echecs'], marker_color='red'))
            fig.update_layout(barmode='stack', template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True)

# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.markdown("""
<div class='footer'>
    <h3>CloudSecMonitor</h3>
    <p style='font-size: 1.1rem; font-weight: 600; color: #42A5F5;'>
        Système de Surveillance et d'Audit de Sécurité Cloud
    </p>
    <p><strong>Projet Académique</strong> | Python et Bases de Données</p>
    <p>Développé par <strong>Asmae ZIANI</strong> & <strong>Soumia BADAOUI</strong></p>
    <p>Encadré par <strong>M. BOUKSIM</strong></p>
    <p>ITIRC 4ème année | 2024-2025</p>
</div>
""", unsafe_allow_html=True)