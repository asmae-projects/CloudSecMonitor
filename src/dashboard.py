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

# ========================================
# CONFIGURATION DE LA PAGE
# ========================================

st.set_page_config(
    page_title="CloudSecMonitor",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CSS INTÉGRÉ — Design Premium SOC
# ========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ─── RESET & BASE ─── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #05080f;
    font-family: 'Inter', sans-serif;
}

/* Grain texture overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
    opacity: 0.4;
}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: #080c14 !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0;
}

/* ─── SIDEBAR LOGO AREA ─── */
.brand-block {
    padding: 2rem 1.5rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 1rem;
}

.brand-mark {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.35rem;
    letter-spacing: -0.03em;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.brand-mark .dot {
    width: 8px;
    height: 8px;
    background: #3b82f6;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 12px #3b82f6;
    animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 12px #3b82f6; }
    50% { opacity: 0.5; box-shadow: 0 0 6px #3b82f6; }
}

.brand-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.35rem;
}

/* ─── SIDEBAR NAV ─── */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 2px !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent !important;
    padding: 0.65rem 1.2rem !important;
    border-radius: 6px !important;
    margin-bottom: 1px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.45) !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-left: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(59,130,246,0.06) !important;
    color: rgba(255,255,255,0.75) !important;
    border-left-color: rgba(59,130,246,0.4) !important;
    transform: none !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stSidebar"] [aria-checked="true"] {
    background: rgba(59,130,246,0.1) !important;
    color: #93c5fd !important;
    border-left-color: #3b82f6 !important;
}

/* ─── PROJECT INFO BLOCK ─── */
.proj-card {
    margin: 1rem;
    padding: 1.2rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
}

.proj-card .label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    display: block;
}

.proj-card .field {
    margin-bottom: 0.6rem;
}

.proj-card .field-key {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.3);
    font-weight: 400;
}

.proj-card .field-val {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.7);
    font-weight: 500;
}

/* ─── MAIN CONTENT ─── */
.main-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.04em;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.main-title span {
    color: #3b82f6;
}

.page-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* ─── METRIC CARDS ─── */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    padding: 1.4rem 1.6rem !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

div[data-testid="metric-container"]:hover {
    border-color: rgba(59,130,246,0.25) !important;
    background: rgba(59,130,246,0.04) !important;
    transform: none !important;
    box-shadow: none !important;
}

div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.4), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}

div[data-testid="metric-container"]:hover::before {
    opacity: 1;
}

[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: -0.03em !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.62rem !important;
    font-weight: 400 !important;
    color: rgba(255,255,255,0.3) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
}

/* ─── DIVIDERS ─── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.05) !important;
    margin: 2rem 0 !important;
}

/* ─── STATUS BOX ─── */
.status-band {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.4rem;
    background: rgba(16, 185, 129, 0.06);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 8px;
    margin-bottom: 2rem;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 8px #10b981;
    flex-shrink: 0;
}

.status-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.55);
    letter-spacing: 0.05em;
}

.status-text strong {
    color: #10b981;
    font-weight: 500;
}

/* ─── EXPANDERS ─── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.7) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    padding: 0.8rem 1rem !important;
}

.streamlit-expanderContent {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-top: none !important;
    background: rgba(255,255,255,0.01) !important;
}

/* ─── SEVERITY BADGE ─── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.badge-critical {
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.3);
}

.badge-medium {
    background: rgba(245,158,11,0.12);
    color: #fcd34d;
    border: 1px solid rgba(245,158,11,0.25);
}

.badge-low {
    background: rgba(16,185,129,0.1);
    color: #6ee7b7;
    border: 1px solid rgba(16,185,129,0.2);
}

/* ─── INCIDENT ROW ─── */
.incident-row {
    padding: 1rem 1.2rem;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    background: rgba(255,255,255,0.02);
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: border-color 0.2s;
}

.incident-row:hover {
    border-color: rgba(255,255,255,0.1);
}

.incident-accent {
    width: 3px;
    align-self: stretch;
    border-radius: 2px;
    flex-shrink: 0;
}

.accent-critical { background: #ef4444; }
.accent-medium   { background: #f59e0b; }
.accent-low      { background: #10b981; }

.incident-body { flex: 1; min-width: 0; }

.incident-desc {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.75);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.3rem;
}

.incident-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    color: rgba(255,255,255,0.3);
    display: flex;
    gap: 1.2rem;
    flex-wrap: wrap;
}

/* ─── BUTTONS ─── */
.stDownloadButton > button {
    background: rgba(59,130,246,0.12) !important;
    color: #93c5fd !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.4rem !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    font-weight: 400 !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
}

.stDownloadButton > button:hover {
    background: rgba(59,130,246,0.2) !important;
    border-color: rgba(59,130,246,0.5) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ─── ALERTS ─── */
.stAlert {
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ─── DATAFRAME ─── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

/* ─── SELECTBOX / SLIDER ─── */
.stSelectbox label, .stSlider label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    color: rgba(255,255,255,0.35) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    font-weight: 400 !important;
}

/* ─── FOOTER ─── */
.footer-block {
    margin-top: 4rem;
    padding: 1.5rem 0 1rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1rem;
}

.footer-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: rgba(255,255,255,0.15);
    letter-spacing: -0.02em;
}

.footer-credits {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: rgba(255,255,255,0.2);
    text-align: right;
    line-height: 1.8;
    letter-spacing: 0.05em;
}

/* ─── HIDE STREAMLIT CHROME ─── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ========================================
# FONCTIONS DE CONNEXION BASE DE DONNÉES
# ========================================

@st.cache_resource
def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cloudsecmonitor",
            port=3306
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion MySQL: {err}")
        return None

def get_global_stats():
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    stats = {}
    cursor.execute("SELECT COUNT(*) as total FROM logs_securite")
    stats['total_logs'] = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM incidents WHERE niveau_severite = 'critique' AND statut = 'nouveau'")
    stats['incidents_critiques'] = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT adresse_ip_source) as total FROM logs_securite WHERE statut = 'echec'")
    stats['ips_suspectes'] = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM incidents")
    stats['total_incidents'] = cursor.fetchone()['total']
    cursor.close()
    return stats

def get_logs_by_type():
    conn = get_connection()
    if not conn:
        return None
    query = "SELECT type_log, COUNT(*) as count FROM logs_securite GROUP BY type_log ORDER BY count DESC"
    return pd.read_sql(query, conn)

def get_recent_logs(limit=50):
    conn = get_connection()
    if not conn:
        return None
    query = f"""
        SELECT l.date_heure, s.nom_serveur, l.type_log,
               l.adresse_ip_source, l.utilisateur, l.statut, l.description
        FROM logs_securite l
        JOIN serveurs s ON l.id_serveur = s.id_serveur
        ORDER BY l.date_heure DESC LIMIT {limit}
    """
    return pd.read_sql(query, conn)

def get_incidents():
    conn = get_connection()
    if not conn:
        return None
    query = """
        SELECT i.id_incident, i.date_detection, i.niveau_severite,
               i.statut, i.description, s.nom_serveur, l.adresse_ip_source
        FROM incidents i
        JOIN logs_securite l ON i.id_log = l.id_log
        JOIN serveurs s ON l.id_serveur = s.id_serveur
        ORDER BY i.date_detection DESC
    """
    return pd.read_sql(query, conn)

def get_incidents_by_day():
    conn = get_connection()
    if not conn:
        return None
    query = """
        SELECT DATE(date_detection) as date, COUNT(*) as count
        FROM incidents GROUP BY DATE(date_detection)
        ORDER BY date DESC LIMIT 30
    """
    return pd.read_sql(query, conn)

def get_top_suspect_ips():
    conn = get_connection()
    if not conn:
        return None
    query = """
        SELECT adresse_ip_source, COUNT(*) as tentatives
        FROM logs_securite WHERE statut = 'echec'
        GROUP BY adresse_ip_source ORDER BY tentatives DESC LIMIT 10
    """
    return pd.read_sql(query, conn)

# ========================================
# PLOTLY THEME
# ========================================

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Mono, monospace', color='rgba(255,255,255,0.4)', size=10),
    margin=dict(l=0, r=0, t=24, b=0),
    xaxis=dict(
        gridcolor='rgba(255,255,255,0.04)',
        linecolor='rgba(255,255,255,0.06)',
        tickfont=dict(size=9)
    ),
    yaxis=dict(
        gridcolor='rgba(255,255,255,0.04)',
        linecolor='rgba(255,255,255,0.06)',
        tickfont=dict(size=9)
    )
)

# ========================================
# SIDEBAR
# ========================================

st.sidebar.markdown("""
<div class="brand-block">
    <div class="brand-mark">
        <span class="dot"></span>
        CloudSecMonitor
    </div>
    <div class="brand-sub">Security Operations</div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Logs", "Incidents", "Statistiques"],
    label_visibility="collapsed"
)

st.sidebar.markdown("""
<div class="proj-card">
    <span class="label">Contexte</span>
    <div class="field">
        <div class="field-key">Module</div>
        <div class="field-val">Python & Bases de Données</div>
    </div>
    <div class="field">
        <div class="field-key">Équipe</div>
        <div class="field-val">A. Ziani · S. Badaoui</div>
    </div>
    <div class="field">
        <div class="field-key">Encadrant</div>
        <div class="field-val">M. Bouksim</div>
    </div>
    <div class="field">
        <div class="field-key">Formation</div>
        <div class="field-val">ITIRC — 4ème année</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========================================
# PAGE 1 — ACCUEIL
# ========================================

if page == "Accueil":
    st.markdown('<p class="main-title">Cloud<span>Sec</span>Monitor</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Surveillance et audit de sécurité — infrastructure cloud simulée</p>', unsafe_allow_html=True)

    stats = get_global_stats()

    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Logs collectés", f"{stats['total_logs']:,}", "Total événements")
        with col2:
            st.metric("Alertes critiques", stats['incidents_critiques'],
                     "Action requise" if stats['incidents_critiques'] > 0 else "Système nominal",
                     delta_color="inverse")
        with col3:
            st.metric("IP suspectes", stats['ips_suspectes'], "Sources malveillantes")
        with col4:
            st.metric("Incidents totaux", stats['total_incidents'], "Historique")

        st.markdown("""
        <div class="status-band">
            <div class="status-dot"></div>
            <div class="status-text"><strong>Surveillance active</strong> — Analyse comportementale en cours · Détection d'anomalies en temps réel</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-label">Répartition des événements</div>', unsafe_allow_html=True)
            logs_by_type = get_logs_by_type()
            if logs_by_type is not None and not logs_by_type.empty:
                fig = px.bar(
                    logs_by_type, x='type_log', y='count',
                    labels={'type_log': '', 'count': ''},
                )
                fig.update_traces(
                    marker_color='rgba(59,130,246,0.7)',
                    marker_line_color='rgba(59,130,246,0.0)',
                    marker_line_width=0,
                )
                fig.update_layout(height=320, showlegend=False, **PLOT_LAYOUT)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with col2:
            st.markdown('<div class="section-label">Top menaces — IP sources</div>', unsafe_allow_html=True)
            top_ips = get_top_suspect_ips()
            if top_ips is not None and not top_ips.empty:
                fig = px.bar(
                    top_ips, x='tentatives', y='adresse_ip_source', orientation='h',
                    labels={'adresse_ip_source': '', 'tentatives': ''},
                )
                fig.update_traces(
                    marker_color='rgba(239,68,68,0.65)',
                    marker_line_width=0,
                )
                fig.update_layout(height=320, showlegend=False, **PLOT_LAYOUT)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Incidents critiques récents</div>', unsafe_allow_html=True)

        incidents_df = get_incidents()
        if incidents_df is not None and not incidents_df.empty:
            critical = incidents_df[incidents_df['niveau_severite'] == 'critique'].head(5)
            if not critical.empty:
                for _, row in critical.iterrows():
                    desc = str(row['description'])[:80] + '...' if len(str(row['description'])) > 80 else str(row['description'])
                    date_str = str(row['date_detection'])[:16]
                    st.markdown(f"""
                    <div class="incident-row">
                        <div class="incident-accent accent-critical"></div>
                        <div class="incident-body">
                            <div class="incident-desc">{desc}</div>
                            <div class="incident-meta">
                                <span>{date_str}</span>
                                <span>{row['nom_serveur']}</span>
                                <span>{row['adresse_ip_source']}</span>
                                <span class="badge badge-critical">critique</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ========================================
# PAGE 2 — LOGS
# ========================================

elif page == "Logs":
    st.markdown('<p class="main-title">Registre des <span>Événements</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Consultation et analyse des logs de sécurité</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Type d'événement", ["Tous", "SSH", "scan_port", "acces_fichier"])
    with col2:
        status_filter = st.selectbox("Statut", ["Tous", "succes", "echec"])
    with col3:
        limit = st.slider("Nombre de logs", 10, 200, 50, 10)

    st.markdown('<hr>', unsafe_allow_html=True)

    logs_df = get_recent_logs(limit)

    if logs_df is not None and not logs_df.empty:
        if type_filter != "Tous":
            logs_df = logs_df[logs_df['type_log'] == type_filter]
        if status_filter != "Tous":
            logs_df = logs_df[logs_df['statut'] == status_filter]

        logs_df['date_heure'] = pd.to_datetime(logs_df['date_heure']).dt.strftime('%Y-%m-%d %H:%M:%S')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Affichés", len(logs_df))
        with col2:
            st.metric("Échecs", len(logs_df[logs_df['statut'] == 'echec']))
        with col3:
            st.metric("Succès", len(logs_df[logs_df['statut'] == 'succes']))

        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Tableau des événements</div>', unsafe_allow_html=True)
        st.dataframe(logs_df, use_container_width=True, height=560)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = logs_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Exporter CSV",
                csv,
                f'logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'text/csv',
                use_container_width=True
            )

# ========================================
# PAGE 3 — INCIDENTS
# ========================================

elif page == "Incidents":
    st.markdown('<p class="main-title">Gestion des <span>Incidents</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Surveillance et réponse aux menaces de sécurité</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        severity_filter = st.selectbox("Sévérité", ["Tous", "critique", "moyen", "faible"])
    with col2:
        status_filter = st.selectbox("Statut", ["Tous", "nouveau", "en_cours", "resolu"])

    st.markdown('<hr>', unsafe_allow_html=True)

    incidents_df = get_incidents()

    if incidents_df is not None and not incidents_df.empty:
        if severity_filter != "Tous":
            incidents_df = incidents_df[incidents_df['niveau_severite'] == severity_filter]
        if status_filter != "Tous":
            incidents_df = incidents_df[incidents_df['statut'] == status_filter]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Critiques", len(incidents_df[incidents_df['niveau_severite'] == 'critique']))
        with col2:
            st.metric("Moyens", len(incidents_df[incidents_df['niveau_severite'] == 'moyen']))
        with col3:
            st.metric("Faibles", len(incidents_df[incidents_df['niveau_severite'] == 'faible']))
        with col4:
            st.metric("En cours", len(incidents_df[incidents_df['statut'].isin(['nouveau', 'en_cours'])]))

        st.markdown('<hr>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-label">Répartition par sévérité</div>', unsafe_allow_html=True)
            severity_counts = incidents_df['niveau_severite'].value_counts()
            fig = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                color=severity_counts.index,
                color_discrete_map={
                    'critique': 'rgba(239,68,68,0.75)',
                    'moyen': 'rgba(245,158,11,0.75)',
                    'faible': 'rgba(16,185,129,0.7)'
                },
                hole=0.6
            )
            fig.update_traces(
                textfont=dict(family='DM Mono, monospace', size=10, color='rgba(255,255,255,0.5)'),
                marker=dict(line=dict(color='#05080f', width=3))
            )
            fig.update_layout(
                height=300,
                legend=dict(font=dict(size=10, color='rgba(255,255,255,0.4)', family='DM Mono, monospace')),
                **PLOT_LAYOUT
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with col2:
            st.markdown('<div class="section-label">Évolution temporelle</div>', unsafe_allow_html=True)
            incidents_by_day = get_incidents_by_day()
            if incidents_by_day is not None and not incidents_by_day.empty:
                fig = px.area(
                    incidents_by_day, x='date', y='count',
                    labels={'date': '', 'count': ''},
                )
                fig.update_traces(
                    line_color='rgba(239,68,68,0.8)',
                    fillcolor='rgba(239,68,68,0.07)',
                    line_width=1.5
                )
                fig.update_layout(height=300, **PLOT_LAYOUT)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Registre des incidents</div>', unsafe_allow_html=True)

        incidents_df['date_detection'] = pd.to_datetime(incidents_df['date_detection']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(incidents_df, use_container_width=True, height=400)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = incidents_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Exporter CSV",
                csv,
                f'incidents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'text/csv',
                use_container_width=True
            )

# ========================================
# PAGE 4 — STATISTIQUES
# ========================================

elif page == "Statistiques":
    st.markdown('<p class="main-title">Analyse <span>Avancée</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Statistiques détaillées par serveur et par activité</p>', unsafe_allow_html=True)

    conn = get_connection()

    if conn:
        st.markdown('<div class="section-label">Activité par serveur</div>', unsafe_allow_html=True)

        query = """
            SELECT s.nom_serveur,
                   COUNT(*) as total_logs,
                   SUM(CASE WHEN l.statut = 'echec' THEN 1 ELSE 0 END) as echecs,
                   SUM(CASE WHEN l.statut = 'succes' THEN 1 ELSE 0 END) as succes
            FROM logs_securite l
            JOIN serveurs s ON l.id_serveur = s.id_serveur
            GROUP BY s.nom_serveur ORDER BY total_logs DESC
        """
        server_stats = pd.read_sql(query, conn)

        if not server_stats.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Succès', x=server_stats['nom_serveur'],
                y=server_stats['succes'],
                marker_color='rgba(16,185,129,0.65)',
                marker_line_width=0
            ))
            fig.add_trace(go.Bar(
                name='Échecs', x=server_stats['nom_serveur'],
                y=server_stats['echecs'],
                marker_color='rgba(239,68,68,0.65)',
                marker_line_width=0
            ))
            fig.update_layout(
                barmode='stack',
                height=380,
                legend=dict(font=dict(size=10, color='rgba(255,255,255,0.35)', family='DM Mono')),
                **PLOT_LAYOUT
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ========================================
# FOOTER
# ========================================

st.markdown("""
<div class="footer-block">
    <div class="footer-name">CloudSecMonitor</div>
    <div class="footer-credits">
        Asmae Ziani · Soumia Badaoui<br/>
        Encadré par M. Bouksim — ITIRC 4ème année · 2024–2025
    </div>
</div>
""", unsafe_allow_html=True)
