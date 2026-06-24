# Système de Surveillance par Drone — 100% Local, 100% Open Source

Système de surveillance vidéo par drone avec détection IA temps réel, entièrement local et open source. Détection de personnes, véhicules, armes, regroupements et déplacements, avec alertes vers un dashboard web.

## 🎯 Objectifs

- **Détection temps réel** : Personnes, véhicules, armes, regroupements, déplacements (pied/moto)
- **100% local** : Aucune dépendance cloud pour le cœur du système
- **100% open source** : Composants open source au maximum
- **Alertes opérateur** : Dashboard web avec alertes visuelles et sonores
- **Confirmation humaine** : Le système détecte et alerte, l'opérateur décide

## 🏗️ Architecture

```
Drone → Liaison LOS/BLOS → MediaMTX → Pipeline IA → Redis/MQTT → FastAPI → Dashboard
```

### Stack technique

| Composant | Outil | Licence |
|-----------|-------|---------|
| Ingestion média | MediaMTX | MIT |
| Détection IA | YOLOv8/v11 + SAHI | AGPL-3.0 / MIT |
| Tracking | ByteTrack | MIT |
| Backend | FastAPI + Uvicorn | MIT |
| Bus de messages | Redis | BSD-3 |
| Base de données | PostgreSQL + PostGIS | PostgreSQL License / GPL-2 |
| Frontend | React + Vite + TypeScript | MIT |
| Cartographie | Leaflet + tuiles OSM auto-hébergées | BSD-2 |
| Déploiement | Docker + Docker Compose | — |

## 📋 Exigences fonctionnelles

1. **Personnes** : Détection + comptage + tracking individuel
2. **Intrusion / véhicules** : Détection véhicules + alerte si franchissement de zone
3. **Armes** : Détection avec confirmation opérateur obligatoire
4. **Regroupement** : Détection de N+ personnes dans une zone pendant D+ secondes
5. **Déplacement** : Classification piéton vs moto (association personne↔véhicule + vitesse)

## 🚀 Démarrage rapide

```bash
# Cloner le dépôt
git clone <repo-url>
cd ai-drone-surveillance

# Copier les variables d'environnement
cp .env.example .env

# Lancer tous les services
docker compose up -d

# Accéder au dashboard
# http://localhost:3000
```

## 📁 Structure du dépôt

```
ai-drone-surveillance/
├── docker-compose.yml
├── .env.example
├── README.md
├── PROGRESS.md
├── AGENTS.md
├── docs/
│   ├── architecture.md
│   └── runbook.md
├── ingestion/
│   └── mediamtx.yml
├── ai-pipeline/
│   ├── inference/
│   ├── tracking/
│   ├── zones/
│   ├── training/
│   ├── simulator/
│   └── tests/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── websocket/
│   │   └── db/
│   ├── alembic/
│   └── tests/
├── frontend/
│   ├── src/
│   └── public/
├── infra/
│   ├── nginx/
│   └── certs/
└── datasets/
```

## 📖 Documentation

- **[Architecture détaillée](docs/architecture.md)** — Spécifications techniques et stack
- **[PROGRESS.md](PROGRESS.md)** — Suivi de progression du projet
- **[AGENTS.md](AGENTS.md)** — Instructions pour l'agent IA

## 🔧 Configuration

Voir `.env.example` pour toutes les variables d'environnement configurables :

- Ports des services (MediaMTX, Redis, PostgreSQL, FastAPI, Frontend)
- Paramètres IA (modèle, seuils, SAHI)
- Règles de détection (seuils de regroupement, vitesse)
- Stockage médias

## ⚠️ Conformité légale

La détection de personnes/véhicules/armes par drone est encadrée juridiquement selon les pays (protection des données, droit à l'image, réglementation aérienne/drone, autorisations de surveillance). Ce projet ne remplace pas un avis juridique — une validation par les autorités/services compétents est requise avant toute mise en production.

## 📄 Licence

À définir (projet open source)

## 🤝 Contribution

Ce projet est en développement actif. Voir [PROGRESS.md](PROGRESS.md) pour l'état actuel.
