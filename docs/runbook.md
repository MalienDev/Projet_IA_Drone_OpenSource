# Runbook - Système de Surveillance par Drone

Guide opérationnel pour le déploiement, la maintenance et le dépannage du système de surveillance par drone.

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Démarrage du système](#démarrage-du-système)
4. [Arrêt du système](#arrêt-du-système)
5. [Configuration](#configuration)
6. [Surveillance](#surveillance)
7. [Sauvegarde et restauration](#sauvegarde-et-restauration)
8. [Dépannage](#dépannage)
9. [Mise à jour](#mise-à-jour)
10. [Sécurité](#sécurité)

---

## Prérequis

### Logiciels requis

- **Docker** : Version 20.10 ou supérieure
- **Docker Compose** : Version 2.0 ou supérieure
- **OpenSSL** : Pour la génération des certificats TLS (optionnel)
- **Git** : Pour cloner le dépôt

### Matériel recommandé

- **CPU** : 4 cœurs minimum
- **RAM** : 8 Go minimum (16 Go recommandé)
- **Stockage** : 50 Go minimum (pour les médias et logs)
- **GPU** : NVIDIA GPU avec CUDA (optionnel, pour améliorer les performances IA)

### Systèmes d'exploitation supportés

- Ubuntu Server 22.04/24.04 LTS (recommandé)
- Windows 10/11 (supporté)
- macOS (supporté)

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <repo-url>
cd ai-drone-surveillance
```

### 2. Exécuter le script d'installation

**Windows :**
```powershell
.\scripts\install.ps1
```

**Linux/macOS :**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### 3. Configuration

Éditer le fichier `.env` avec vos configurations :

```env
# Base de données
POSTGRES_DB=drone_surveillance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_change_this
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ports (si modification nécessaire)
MEDIAMTX_RTSP_PORT=8554
MEDIAMTX_RTMP_PORT=1935
BACKEND_PORT=8000
FRONTEND_HTTP_PORT=3000
FRONTEND_HTTPS_PORT=3443
```

### 4. Générer les certificats TLS

Les certificats sont générés automatiquement par le script d'installation. Pour régénérer :

**Windows :**
```powershell
.\infra\certs\generate-certs.ps1
```

**Linux/macOS :**
```bash
chmod +x infra/certs/generate-certs.sh
./infra/certs/generate-certs.sh
```

---

## Démarrage du système

### Démarrage complet

```bash
docker compose up -d
```

### Démarrage sélectif

```bash
# Démarrer uniquement les services de base
docker compose up -d mediamtx redis postgres

# Démarrer le backend
docker compose up -d backend

# Démarrer le frontend
docker compose up -d frontend
```

### Vérifier l'état des services

```bash
docker compose ps
```

### Vérifier les logs

```bash
# Tous les services
docker compose logs -f

# Service spécifique
docker compose logs -f mediamtx
docker compose logs -f backend
docker compose logs -f frontend
```

### Accéder au dashboard

- **HTTP** : http://localhost:3000
- **HTTPS** : https://localhost:3443

**Identifiants par défaut :**
- Utilisateur : `admin`
- Mot de passe : `admin123` (à changer au premier login)

---

## Arrêt du système

### Arrêt gracieux

```bash
docker compose down
```

### Arrêt et suppression des volumes

```bash
docker compose down -v
```

⚠️ **Attention** : Cela supprime toutes les données persistantes (base de données, médias).

### Arrêt d'un service spécifique

```bash
docker compose stop mediamtx
docker compose stop backend
```

---

## Configuration

### MediaMTX

Configuration dans `ingestion/mediamtx.yml` :

```yaml
# Protocoles et ports
rtsp: yes
rtmp: yes
srt: yes

# Configuration des flux
paths:
  drone-01-los:
    source: publisher
  drone-01-blos:
    source: publisher
```

### Backend API

Configuration via variables d'environnement dans `.env` ou `docker-compose.yml` :

- `DATABASE_URL` : URL de connexion PostgreSQL
- `REDIS_HOST` : Hôte Redis
- `REDIS_PORT` : Port Redis
- `JWT_SECRET_KEY` : Clé secrète pour les tokens JWT

### Frontend

Configuration dans `frontend/src/services/api.ts` :

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
const WS_URL = import.meta.env.VITE_WS_URL || '/ws';
```

### IA Pipeline

Configuration dans `ai-pipeline/inference/config.py` :

```python
# Modèle
model_path = "yolov8n.pt"
confidence_threshold = 0.5

# Tracking
use_tracking = True
tracker_type = "bytetrack"

# SAHI (détection petits objets)
use_sahi = False  # Activer sur GPU

# Règles
enable_rules_engine = True
enable_alert_publishing = True
```

---

## Surveillance

### Vérifier l'état des services

```bash
docker compose ps
```

### Surveiller l'utilisation des ressources

```bash
# CPU et mémoire
docker stats

# Espace disque
docker system df
```

### Vérifier les logs en temps réel

```bash
# Backend
docker compose logs -f backend

# MediaMTX
docker compose logs -f mediamtx

# IA Pipeline (si exécuté hors conteneur)
tail -f ai-pipeline/logs/detector.log
```

### Health checks

```bash
# Backend health check
curl http://localhost:8000/api/health

# MediaMTX interface
curl http://localhost:8888
```

---

## Sauvegarde et restauration

### Sauvegarde de la base de données

```bash
# Sauvegarder PostgreSQL
docker compose exec postgres pg_dump -U postgres drone_surveillance > backup.sql

# Sauvegarder avec date
docker compose exec postgres pg_dump -U postgres drone_surveillance > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restauration de la base de données

```bash
# Restaurer PostgreSQL
docker compose exec -T postgres psql -U postgres drone_surveillance < backup.sql
```

### Sauvegarde des médias

```bash
# Archiver le répertoire media
tar -czf media_backup_$(date +%Y%m%d).tar.gz data/media/
```

### Sauvegarde complète

```bash
# Script de sauvegarde complète
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec postgres pg_dump -U postgres drone_surveillance > backup_${DATE}.sql
tar -czf full_backup_${DATE}.tar.gz data/media/ backup_${DATE}.sql
```

---

## Dépannage

### Problème : Les conteneurs ne démarrent pas

**Symptôme** : `docker compose up` échoue

**Solutions :**
1. Vérifier que Docker est en cours d'exécution : `docker ps`
2. Vérifier les ports disponibles : `netstat -tuln` (Linux) ou `netstat -an` (Windows)
3. Vérifier les logs : `docker compose logs`
4. Reconstruire les images : `docker compose build --no-cache`

### Problème : Le backend ne se connecte pas à la base de données

**Symptôme** : Erreur de connexion PostgreSQL dans les logs backend

**Solutions :**
1. Vérifier que PostgreSQL est en cours d'exécution : `docker compose ps postgres`
2. Vérifier les identifiants dans `.env`
3. Attendre que PostgreSQL soit prêt (healthcheck)
4. Redémarrer le backend : `docker compose restart backend`

### Problème : Le frontend ne peut pas contacter l'API

**Symptôme** : Erreur CORS ou 502 Bad Gateway

**Solutions :**
1. Vérifier que le backend est en cours d'exécution : `docker compose ps backend`
2. Vérifier la configuration du proxy dans `nginx.conf`
3. Vérifier les variables d'environnement frontend
4. Redémarrer le frontend : `docker compose restart frontend`

### Problème : MediaMTX ne reçoit pas le flux

**Symptôme** : Pas de flux visible sur l'interface MediaMTX

**Solutions :**
1. Vérifier que le simulateur ou le drone envoie le flux
2. Vérifier la configuration dans `ingestion/mediamtx.yml`
3. Vérifier les ports : `netstat -tuln | grep 1935` (RTMP)
4. Tester avec ffplay : `ffplay rtsp://localhost:8554/drone-01-los`

### Problème : Certificat TLS non reconnu

**Symptôme** : Avertissement de sécurité du navigateur

**Solutions :**
1. Les certificats sont auto-signés, c'est normal
2. Accepter l'avertissement de sécurité dans le navigateur
3. Pour un environnement de production, utiliser des certificats Let's Encrypt

### Problème : FPS IA trop bas

**Symptôme** : Détection lente (< 1 FPS)

**Solutions :**
1. Désactiver SAHI sur CPU
2. Utiliser un modèle plus petit (YOLOv8n)
3. Utiliser un GPU NVIDIA avec TensorRT
4. Réduire la résolution du flux

### Problème : Pas de détections

**Symptôme** : Aucune détection sur le flux

**Solutions :**
1. Vérifier que le flux contient des objets
2. Baisser le seuil de confiance
3. Vérifier les classes cibles dans la configuration
4. Tester avec une vidéo de validation connue

---

## Mise à jour

### Mise à jour du code

```bash
# Récupérer les dernières modifications
git pull

# Reconstruire les images
docker compose build

# Redémarrer les services
docker compose up -d
```

### Mise à jour des dépendances

```bash
# Backend
cd backend
pip install -r requirements.txt --upgrade
cd ..

# Frontend
cd frontend
npm update
cd ..
```

### Mise à jour des modèles IA

```bash
# Télécharger un nouveau modèle YOLO
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Ou entraîner un modèle custom
cd ai-pipeline/training
python train.py --data ../datasets/dataset_merged/data.yaml --epochs 100
```

---

## Sécurité

### Changer les mots de passe par défaut

1. Connecter au dashboard : https://localhost:3443
2. Login avec `admin` / `admin123`
3. Changer le mot de passe dans les paramètres
4. Changer `POSTGRES_PASSWORD` dans `.env`
5. Redémarrer PostgreSQL : `docker compose restart postgres`

### Activer HTTPS

HTTPS est activé par défaut avec des certificats auto-signés. Pour un environnement de production :

1. Obtenir des certificats Let's Encrypt
2. Remplacer les certificats dans `infra/certs/`
3. Redémarrer le frontend : `docker compose restart frontend`

### Restreindre l'accès réseau

Modifier `docker-compose.yml` pour exposer uniquement les ports nécessaires :

```yaml
services:
  frontend:
    ports:
      - "3000:80"   # HTTP interne uniquement
      - "3443:443"  # HTTPS externe
  backend:
    ports:
      - "127.0.0.1:8000:8000"  # Accès local uniquement
```

### Audit des logs

```bash
# Logs d'authentification
docker compose logs backend | grep -i auth

# Logs d'alertes
docker compose logs backend | grep -i alert

# Logs d'erreurs
docker compose logs | grep -i error
```

### Rotation des logs

Configurer la rotation des logs dans `docker-compose.yml` :

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Checklist de déploiement

Avant de déployer en production :

- [ ] Changer tous les mots de passe par défaut
- [ ] Configurer des certificats TLS valides
- [ ] Restreindre l'accès réseau (firewall)
- [ ] Configurer la sauvegarde automatique
- [ ] Tester le pipeline IA avec des vraies vidéos
- [ ] Valider les alertes et notifications
- [ ] Configurer le monitoring (Prometheus/Grafana)
- [ ] Documenter les procédures d'urgence
- [ ] Former les opérateurs
- [ ] Vérifier la conformité légale (RGPD, réglementation drones)

---

## Support

Pour toute question ou problème :

1. Consulter la documentation : `docs/`
2. Vérifier les logs : `docker compose logs`
3. Consulter le rapport d'intégration : `docs/integration-test-report.md`
4. Ouvrir une issue sur le dépôt Git
