# CloudSecMonitor - Système de Monitoring et Audit de Sécurité Cloud

## 📋 Description
Système de surveillance de sécurité pour infrastructure cloud simulée. Collecte et analyse des logs de sécurité (connexions SSH, tentatives d'accès, scans de ports) avec détection automatique d'anomalies et génération d'alertes en temps réel.

## 🎯 Objectifs
- Collecter et stocker des logs de sécurité
- Détecter automatiquement les comportements suspects
- Générer des alertes selon le niveau de sévérité
- Visualiser les statistiques via un dashboard

## 🛠️ Technologies
- **Python 3.x** - Scripts de collecte et analyse
- **MySQL** - Base de données avec procédures stockées et triggers
- **Flask/Streamlit** - Dashboard de visualisation
- **GitHub** - Gestion de versions

## 🏗️ Architecture Base de Données

### Tables
1. **serveurs** - Serveurs cloud surveillés
2. **logs_securite** - Logs de sécurité collectés
3. **regles_alerte** - Règles de détection d'anomalies
4. **incidents** - Incidents détectés

### Relations
- Un serveur génère plusieurs logs
- Un log peut déclencher un incident
- Une règle détecte plusieurs incidents

## 📦 Installation

### Prérequis
- Python 3.8+
- MySQL 8.0+ (WAMP/XAMPP)
- Git

## 📊 Fonctionnalités

### Détection d'Anomalies
- Tentatives de connexion SSH répétées
- Scans de ports massifs
- Accès non autorisés

### Niveaux d'Alerte
- **Faible** - Événements inhabituels
- **Moyen** - Comportements suspects
- **Critique** - Attaques confirmées

## 📁 Structure du Projet
```
CloudSecMonitor/
├── config/          # Configuration (paramètres MySQL, constantes)
├── database/        # Scripts SQL et exports de la base de données
├── docs/            # Documentation technique et guides
├── src/             # Code source Python (modules principaux)
├── tests/           # Tests unitaires
└── requirements.txt # Dépendances Python
```
> **Note:** Les fichiers `.gitkeep` dans les dossiers vides permettent de conserver la structure des répertoires dans Git, car Git ne track pas les dossiers vides par défaut.

## 👥 Équipe
- **Asmae ZIANI** - 
- **Soumia BADAOUI** - 

## 📅 Statut
🚧 **Phase 1 - Conception** (Semaine 1/6)
- ✅ Schéma de base de données créé
- ✅ Tables et relations définies
- ⏳ Scripts Python en cours


Projet Python et Bases de Données - 4ème année ITIRC  
Encadrant: M. BOUKSIM

---


