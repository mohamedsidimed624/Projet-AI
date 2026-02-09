# 🛢️ Well Analysis AI Platform

Plateforme web moderne pour la gestion, la visualisation et l'analyse intelligente des données de puits pétroliers (Well Logs).

![Status](https://img.shields.io/badge/Status-Development-blue)
![Python](https://img.shields.io/badge/Backend-Flask%20%7C%20SQLAlchemy-green)
![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-blue)

## 🌟 Fonctionnalités

### 📊 Visualisation & Gestion
- **Gestion des Puits** : Création, modification et suivi des puits par champ et localisation.
- **Visualisation Interactive** : Affichage graphique des logs (Gamma Ray, Résistivité, Densité, Neutron) avec zoom et curseurs.
- **Crossplots** : Analyse Densité-Neutron avec lignes de référence lithologiques (Grès, Calcaire, Dolomite) et identification des effets de gaz.

### 🧠 Analyse Assistée
- **Calculs Pétrophysiques** : Estimation automatique du Vshale, de la Porosité et de la Saturation en eau.
- **Identification des Zones** : Détection automatique des réservoirs potentiels et des zones d'argile.
- **Rapports** : Génération de rapports complets au format HTML et JSON téléchargeables.

### 🛡️ Sécurité & Architecture
- **Authentification** : Système sécurisé par JWT (JSON Web Tokens).
- **Architecture Modulaire** : Backend Flask scalable et Frontend React performant.
- **Base de Données** : Support SQLite (Dév) et MySQL (Prod).

---

## 🚀 Installation

### Prérequis
- Python 3.8+
- Node.js 14+
- npm ou yarn

### 1. Backend (Flask)

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
# Activer (Windows)
venv\Scripts\activate
# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données et créer les données de test
python seed_data.py
# (Cela crée aussi l'utilisateur démo)
```

### 2. Frontend (React)

```bash
cd frontend

# Installer les dépendances
npm install
```

---

## ▶️ Démarrage

### Lancer le Backend
Dans un terminal, dossier `backend` :
```bash
python run.py
# Le serveur démarre sur http://localhost:5000
```

### Lancer le Frontend
Dans un autre terminal, dossier `frontend` :
```bash
npm run dev
# L'application sera accessible sur http://localhost:3000
```

---

## 👤 Compte de Démonstration

Une fois les données initialisées via `seed_data.py`, vous pouvez vous connecter avec :

- **Utilisateur** : `demo`
- **Mot de passe** : `demo123`

Ce compte contient déjà :
- 2 Puits (Hassi Messaoud, Oued Righ)
- Des logs complets (GR, RESIS, DENS, NEUT, SP)
- Des zones pétrophysiques analysées

---

## 📂 Structure du Projet

```
AI-project/
├── backend/                # API Flask
│   ├── app/
│   │   ├── models/         # Modèles SQLAlchemy (User, Well, Log...)
│   │   ├── routes/         # Endpoints API (Auth, Wells, Analysis...)
│   │   └── services/       # Logique métier
│   ├── instance/           # Base de données SQLite
│   ├── run.py              # Point d'entrée serveur
│   └── seed_data.py        # Script de peuplement de la BDD
│
└── frontend/               # Application React
    ├── src/
    │   ├── components/     # Composants réutilisables (Navbar, Charts...)
    │   ├── context/        # État global (AuthContext)
    │   ├── pages/          # Pages (Dashboard, LogViewer, Analysis...)
    │   └── services/       # Appels API Axios
    └── vite.config.js      # Configuration Vite
```

## 🛠️ Technologies

- **Backend** : Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Pandas, NumPy
- **Frontend** : React.js, React Router, Axios, Plotly.js (via react-plotly.js)
- **Base de données** : SQLite (Developpement), MySQL (Production)

---

## 📝 Auteurs
Projet développé dans le cadre du module d'Intelligence Artificielle appliquée aux Géosciences.
